from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import re
from services.github_repo_service import fetch_user_repositories, get_repository_details

router = APIRouter()

class RepoValidateRequest(BaseModel):
    repo_url: str

def parse_github_url(url: str):
    """Parses a typical GitHub URL to extract owner and repo name."""
    # Matches: https://github.com/owner/repo or github.com/owner/repo
    pattern = r"^(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$"
    match = re.match(pattern, url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL pattern.")
    return match.group(1), match.group(2)

@router.get("/list")
async def get_my_repositories(request: Request):
    """
    Get the list of repositories accessible to the logged-in user.
    """
    access_token = request.session.get("github_access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in with GitHub.")
        
    repos = await fetch_user_repositories(access_token)
    return {"status": "success", "repositories": repos}

@router.post("/validate")
async def validate_repository(req: RepoValidateRequest, request: Request):
    """
    Validate that a given GitHub URL is a valid repository AND that the logged-in user has access.
    """
    access_token = request.session.get("github_access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in with GitHub.")

    owner, repo_name = parse_github_url(req.repo_url)
    
    # Attempt to fetch repo details using the user's token. 
    # If the user doesn't have read access to a private repo, GitHub returns a 404 (not found).
    repo_details = await get_repository_details(access_token, owner, repo_name)
    
    # Validate the user has at least pull (read) access
    permissions = repo_details.get("permissions", {})
    if not permissions.get("pull", False):
         raise HTTPException(status_code=403, detail="You do not have read access to this repository.")
         
    return {"status": "success", "repository": repo_details}

@router.get("/{owner}/{repo}")
async def get_repository(owner: str, repo: str, request: Request):
    """
    Get details for a specific repository.
    """
    access_token = request.session.get("github_access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in with GitHub.")
        
    repo_details = await get_repository_details(access_token, owner, repo)
    return {"status": "success", "repository": repo_details}
