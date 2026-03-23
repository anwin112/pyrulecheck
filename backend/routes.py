from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Request
from fastapi.responses import JSONResponse, FileResponse
from models.schemas import AnalyzeRequest, AnalyzeResponse, Summary, Issues, Metrics, CrossFileAnalysis, PushFixesRequest
from services.repo_service import clone_repository, cleanup_repository
from services.file_validator import get_python_files, validate_files
from services.github_repo_service import get_repository_details
from services.github_branch_service import create_fixes_branch
from services.github_write_service import commit_files_to_branch, get_modified_files
from services.github_pr_service import create_pull_request
from services.rule_engine import run_analysis
from services.scoring_service import calculate_grades
from services.ai_fix_service import generate_fixes_for_issues
import logging
import os
import shutil
import tempfile
from dotenv import load_dotenv
from config import ENABLE_CODE_PATCHING
from services.code_patch_service import apply_code_patch

load_dotenv()

# Basic state-tracking hack for MVP (replaces DB)
ACTIVE_REPO_PATH = None
# In-memory tracking to know pending AI suggestions for 'Apply All'
PENDING_FIXES = {}

LAST_PUSH_STATUS = {"status": "none"}

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repo(request: AnalyzeRequest):
    github_url = request.github_url
    if not github_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")

    global ACTIVE_REPO_PATH, PENDING_FIXES
    
    temp_dir = None
    try:
        temp_dir = clone_repository(github_url)
        
        # Override active repo tracking
        ACTIVE_REPO_PATH = temp_dir
        PENDING_FIXES.clear()
        py_files = get_python_files(temp_dir)
        
        is_valid, validation_msg = validate_files(py_files)
        if not is_valid:
            raise HTTPException(status_code=400, detail=validation_msg)
            
        raw_issues, metrics_data, cross_file_data = run_analysis(py_files)
        
        # Categorize
        critical, major, minor = [], [], []
        sec_count, qual_count, perf_count = 0, 0, 0
        
        for issue in raw_issues:
            if issue['severity'] == 'critical':
                critical.append(issue)
            elif issue['severity'] == 'major':
                major.append(issue)
            else:
                minor.append(issue)
                
            if issue['rule_id'].startswith("SEC"): sec_count += 1
            if issue['rule_id'].startswith("QUAL"): qual_count += 1
            if issue['rule_id'].startswith("PERF"): perf_count += 1

        grades = calculate_grades(sec_count, qual_count, perf_count)
        
        # Integrate AI Fix Service
        target_issues = critical + major
        ai_fixes = []
        ai_status = "not_configured"
        
        if target_issues:
            if os.environ.get("GEMINI_API_KEY"):
                from services.ai_fix_service import RateLimitError
                try:
                    ai_fixes = generate_fixes_for_issues(target_issues)
                    ai_status = "success" if ai_fixes else "failed"
                except RateLimitError:
                    ai_status = "rate_limited"
                except Exception as e:
                    logger.error(f"Error during AI fix generation: {e}")
                    ai_status = "failed"
                
                # Store pending fixes in memory so /apply-all can find them
                for f in ai_fixes:
                    PENDING_FIXES[f["fix_id"]] = f
            else:
                ai_status = "skipped_no_key"
        else:
            ai_status = "no_issues_to_fix"
        
        response = AnalyzeResponse(
            summary=Summary(
                overall_grade=grades['overall_grade'],
                security_score=grades['security_score'],
                code_quality_score=grades['code_quality_score'],
                maintainability_score=grades['maintainability_score'],
                total_files_reviewed=len(py_files)
            ),
            issues=Issues(
                critical=critical,
                major=major,
                minor=minor
            ),
            metrics=Metrics(
                cyclomatic_complexity=metrics_data['cyclomatic_complexity'],
                line_counts=metrics_data['line_counts'],
                function_counts=metrics_data['function_counts']
            ),
            cross_file_analysis=CrossFileAnalysis(
                circular_imports=cross_file_data['circular_imports'],
                shared_globals=cross_file_data['shared_globals'],
                duplicate_classes=cross_file_data['duplicate_classes']
            ),
            recommendations=[
                "Review critical security issues immediately.",
                "Ensure functions are less than 50 lines to improve readability.",
                "Avoid using eval() or exec() in production environments."
            ],
            ai_status=ai_status,
            ai_fix_suggestions=ai_fixes
        )
        return response
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        # Re-raise intentional HTTP exceptions so the frontend gets the right 400 message
        raise he
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")
    finally:
        # If patching is enabled, leave the files alone so the user can patch them.
        # Otherwise, clean them up immediately like before.
        if temp_dir and not ENABLE_CODE_PATCHING:
            cleanup_repository(temp_dir)
            ACTIVE_REPO_PATH = None

from models.schemas import ApplyFixRequest, RejectFixRequest, ActionResponse

@router.post("/apply-fix", response_model=ActionResponse)
async def apply_fix(req: ApplyFixRequest):
    if not ACTIVE_REPO_PATH:
        raise HTTPException(status_code=400, detail="No active repository to patch.")
        
    success = apply_code_patch(ACTIVE_REPO_PATH, req.file, req.line, req.secure_code_example)
    if success:
        PENDING_FIXES.pop(req.fix_id, None)
        return ActionResponse(status="success", message="Fix applied successfully")
    else:
        raise HTTPException(status_code=500, detail="Failed to apply patch to file.")

@router.post("/reject-fix", response_model=ActionResponse)
async def reject_fix(req: RejectFixRequest):
    if req.fix_id in PENDING_FIXES:
        PENDING_FIXES.pop(req.fix_id)
    return ActionResponse(status="success", message="Fix rejected")

@router.post("/apply-all-fixes", response_model=ActionResponse)
async def apply_all_fixes():
    if not ACTIVE_REPO_PATH:
        raise HTTPException(status_code=400, detail="No active repository to patch.")
        
    applied_count = 0
    # Copy keys to dict list to iterate safely while modifying
    fixes_to_apply = list(PENDING_FIXES.values())
    
    for fix in fixes_to_apply:
        success = apply_code_patch(ACTIVE_REPO_PATH, fix["file"], fix["line"], fix["secure_code_example"])
        if success:
            applied_count += 1
            PENDING_FIXES.pop(fix["fix_id"], None)
            
    return ActionResponse(status="success", applied_fixes=applied_count)

@router.get("/download-repo")
async def download_repo(background_tasks: BackgroundTasks):
    if not ACTIVE_REPO_PATH or not os.path.exists(ACTIVE_REPO_PATH):
        raise HTTPException(status_code=400, detail="No active repository to download.")
    
    # Create a temporary zip file
    zip_filename = tempfile.mktemp(prefix="patched_repo_", suffix=".zip")
    base_name = zip_filename.replace(".zip", "")
    
    # Compress the directory
    shutil.make_archive(base_name, 'zip', ACTIVE_REPO_PATH)
    
    # Clean up the zip file after sending
    background_tasks.add_task(os.remove, zip_filename)
    
    return FileResponse(
        path=zip_filename, 
        filename="patched_repository.zip", 
        media_type="application/zip"
    )

@router.post("/github/push-fixes")
async def push_fixes(req: PushFixesRequest, request: Request):
    global ACTIVE_REPO_PATH, LAST_PUSH_STATUS
    if not ACTIVE_REPO_PATH:
        raise HTTPException(status_code=400, detail="No active repository to push.")
        
    access_token = request.session.get("github_access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated with GitHub.")
        
    try:    
        owner, repo_name = req.repo_full_name.split("/")
    except ValueError:
        raise HTTPException(status_code=400, detail="repo_full_name must be 'owner/repo'")
        
    LAST_PUSH_STATUS = {"status": "in_progress", "step": "Validating access"}
    
    # Validate write access
    repo_details = await get_repository_details(access_token, owner, repo_name)
    if not repo_details.get("permissions", {}).get("push", False):
        LAST_PUSH_STATUS = {"status": "failed", "error": "No write access"}
        raise HTTPException(status_code=403, detail="You do not have write access to this repository.")
        
    base_branch = req.base_branch or repo_details.get("default_branch", "main")
    
    LAST_PUSH_STATUS = {"status": "in_progress", "step": "Finding changes"}
    modified_files = get_modified_files(ACTIVE_REPO_PATH)
    if not modified_files:
        LAST_PUSH_STATUS = {"status": "failed", "error": "No local changes"}
        raise HTTPException(status_code=400, detail="No local changes found. Apply fixes first.")
        
    try:
        LAST_PUSH_STATUS = {"status": "in_progress", "step": "Creating branch"}
        branch_info = await create_fixes_branch(access_token, owner, repo_name, base_branch)
        new_branch = branch_info["branch_name"]
        base_sha = branch_info["base_sha"]
        
        LAST_PUSH_STATUS = {"status": "in_progress", "step": "Committing files"}
        commit_msg = "Apply PyRuleCheck approved security and code quality fixes"
        commit_info = await commit_files_to_branch(
            access_token, owner, repo_name, new_branch, base_sha, modified_files, commit_msg
        )
        
        LAST_PUSH_STATUS = {"status": "in_progress", "step": "Opening Pull Request"}
        pr_title = "PyRuleCheck automated fixes for detected Python issues"
        pr_body = (
            "## PyRuleCheck Automated Fixes\n\n"
            f"This PR contains **{len(modified_files)}** file changes with AI-suggested code fixes applied locally by the user.\n\n"
            "**Changes included:**\n"
        )
        for f in modified_files:
            pr_body += f"- `{f['path']}`\n"
            
        pr_body += "\n> ⚠️ **Note:** These fixes were generated by AI and approved by the user. Please review carefully before merging."
        
        pr_info = await create_pull_request(
            access_token, owner, repo_name, new_branch, base_branch, pr_title, pr_body
        )
        
        LAST_PUSH_STATUS = {
            "status": "success",
            "branch": new_branch,
            "commit_url": commit_info["url"],
            "pr_url": pr_info["pr_url"],
            "pr_number": pr_info["pr_number"]
        }
        return LAST_PUSH_STATUS
        
    except HTTPException as e:
        LAST_PUSH_STATUS = {"status": "failed", "error": str(e.detail)}
        raise e
    except Exception as e:
        logger.error(f"Push to GitHub failed: {e}")
        LAST_PUSH_STATUS = {"status": "failed", "error": str(e)}
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/github/push-status")
async def get_push_status():
    return LAST_PUSH_STATUS
