import httpx
from fastapi import HTTPException
from typing import List, Dict
import subprocess
import os

GITHUB_API_BASE = "https://api.github.com"

async def commit_files_to_branch(
    access_token: str, 
    owner: str, 
    repo: str, 
    branch_name: str, 
    base_sha: str, 
    modified_files: List[Dict[str, str]], 
    commit_message: str
) -> dict:
    """
    Commits a list of modified files to the specified branch.
    `modified_files` is a list of dicts: [{"path": "src/main.py", "content": "..."}]
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    async with httpx.AsyncClient() as client:
        # 1. Get the base commit to find the base tree SHA
        commit_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/commits/{base_sha}"
        commit_res = await client.get(commit_url, headers=headers)
        if commit_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch base commit")
        base_tree_sha = commit_res.json()["tree"]["sha"]
        
        # 2. Create blobs for all modified files
        tree_elements = []
        for file in modified_files:
            blob_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/blobs"
            blob_payload = {
                "content": file["content"],
                "encoding": "utf-8"
            }
            blob_res = await client.post(blob_url, headers=headers, json=blob_payload)
            if blob_res.status_code != 201:
                raise HTTPException(status_code=400, detail=f"Failed to create blob for {file['path']}")
            
            blob_sha = blob_res.json()["sha"]
            tree_elements.append({
                "path": file["path"],
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            })
            
        # 3. Create a new tree
        tree_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees"
        tree_payload = {
            "base_tree": base_tree_sha,
            "tree": tree_elements
        }
        tree_res = await client.post(tree_url, headers=headers, json=tree_payload)
        if tree_res.status_code != 201:
            raise HTTPException(status_code=400, detail="Failed to create git tree")
        new_tree_sha = tree_res.json()["sha"]
        
        # 4. Create a new commit
        create_commit_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/commits"
        commit_payload = {
            "message": commit_message,
            "tree": new_tree_sha,
            "parents": [base_sha]
        }
        create_commit_res = await client.post(create_commit_url, headers=headers, json=commit_payload)
        if create_commit_res.status_code != 201:
            raise HTTPException(status_code=400, detail="Failed to create git commit")
        new_commit_sha = create_commit_res.json()["sha"]
        
        # 5. Update branch reference to point to new commit
        update_ref_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs/heads/{branch_name}"
        update_payload = {
            "sha": new_commit_sha,
            "force": False
        }
        update_ref_res = await client.patch(update_ref_url, headers=headers, json=update_payload)
        if update_ref_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to update branch reference")
            
        return {
            "commit_sha": new_commit_sha,
            "url": create_commit_res.json()["html_url"]
        }

def get_modified_files(repo_path: str) -> List[Dict[str, str]]:
    """
    Uses git diff to find modified files in the given repo path and returns their content.
    Returns something like [{"path": "relative/path/to/file.py", "content": "file body..."}]
    """
    if not repo_path or not os.path.exists(repo_path):
        return []
        
    try:
        # Get list of modified files
        result = subprocess.run(
            ["git", "diff", "--name-only"], 
            cwd=repo_path, 
            capture_output=True, 
            text=True, 
            check=True
        )
    except subprocess.CalledProcessError:
        return []

    files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    
    modified_data = []
    for file_path in files:
        full_path = os.path.join(repo_path, file_path)
        if os.path.isfile(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            modified_data.append({
                "path": file_path,
                "content": content
            })
            
    return modified_data
