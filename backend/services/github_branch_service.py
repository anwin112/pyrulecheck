import httpx
from fastapi import HTTPException
from datetime import datetime

GITHUB_API_BASE = "https://api.github.com"

async def create_fixes_branch(access_token: str, owner: str, repo: str, base_branch: str) -> dict:
    """
    Creates a new branch off the base branch.
    Returns a dict with 'branch_name' and 'ref'.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # 1. Get the SHA of the base branch
    base_ref_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/ref/heads/{base_branch}"
    async with httpx.AsyncClient() as client:
        ref_response = await client.get(base_ref_url, headers=headers)
        if ref_response.status_code != 200:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to fetch base branch '{base_branch}': {ref_response.text}"
            )
        base_sha = ref_response.json()["object"]["sha"]
        
    # 2. Create the new branch
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_branch_name = f"pyrulecheck/fixes-{timestamp}"
    new_ref = f"refs/heads/{new_branch_name}"
    
    create_ref_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs"
    payload = {
        "ref": new_ref,
        "sha": base_sha
    }
    
    async with httpx.AsyncClient() as client:
        create_response = await client.post(create_ref_url, headers=headers, json=payload)
        status = create_response.status_code
        if status not in [201, 200]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create new branch '{new_branch_name}': {create_response.text}"
            )
            
    return {
        "branch_name": new_branch_name,
        "ref": new_ref,
        "base_sha": base_sha
    }
