import httpx
from fastapi import HTTPException

GITHUB_API_BASE = "https://api.github.com"

async def create_pull_request(
    access_token: str, 
    owner: str, 
    repo: str, 
    head_branch: str, 
    base_branch: str, 
    title: str, 
    body: str
) -> dict:
    """
    Creates a pull request on GitHub.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
    payload = {
        "title": title,
        "body": body,
        "head": head_branch,
        "base": base_branch
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        
        if response.status_code != 201:
            # Maybe the PR already exists or other error
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to create Pull Request: {response.text}"
            )
            
        data = response.json()
        return {
            "pr_url": data["html_url"],
            "pr_number": data["number"],
            "state": data["state"]
        }
