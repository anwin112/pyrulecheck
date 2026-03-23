import httpx
from fastapi import HTTPException
from typing import List, Dict, Any

GITHUB_API_BASE = "https://api.github.com"

async def fetch_user_repositories(access_token: str) -> List[Dict[str, Any]]:
    """
    Fetch all repositories the authenticated user has access to.
    Returns a simplified list containing necessary metadata.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # We fetch both owned and member repositories
    url = f"{GITHUB_API_BASE}/user/repos?sort=updated&per_page=100&affiliation=owner,collaborator,organization_member"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Failed to fetch repositories from GitHub: {response.text}"
            )
            
        repos = response.json()
        
        # Simplify the repo list for the frontend
        simplified_repos = []
        for repo in repos:
            simplified_repos.append({
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "private": repo["private"],
                "html_url": repo["html_url"],
                "clone_url": repo["clone_url"],
                "default_branch": repo["default_branch"],
                "permissions": repo.get("permissions", {})
            })
            
        return simplified_repos

async def get_repository_details(access_token: str, owner: str, repo: str) -> Dict[str, Any]:
    """
    Fetch specific details for a repository using the user's token.
    Throws a 404 or 403 if the user does not have access.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Repository not found or access denied.")
        elif response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Failed to fetch repository details: {response.text}"
            )
            
        repo_data = response.json()
        return {
            "id": repo_data["id"],
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "private": repo_data["private"],
            "html_url": repo_data["html_url"],
            "clone_url": repo_data["clone_url"],
            "default_branch": repo_data["default_branch"],
            "permissions": repo_data.get("permissions", {})
        }
