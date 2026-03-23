import os
import httpx
from fastapi import HTTPException
from config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI

GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_USER_URL = "https://api.github.com/user"

async def exchange_code_for_token(code: str) -> str:
    """Exchange the OAuth callback code for an access token."""
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub OAuth is not configured on the server.")

    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI
    }
    headers = {
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(GITHUB_TOKEN_URL, data=data, headers=headers)
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange GitHub access token.")
        
    response_data = response.json()
    if "error" in response_data:
        raise HTTPException(status_code=400, detail=response_data.get("error_description", "Invalid callback code"))
        
    return response_data.get("access_token")

async def get_github_user_profile(access_token: str) -> dict:
    """Fetch the authenticated user's profile from GitHub."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(GITHUB_API_USER_URL, headers=headers)
        
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to fetch GitHub user profile or token expired.")
        
    user_data = response.json()
    return {
        "authenticated": True,
        "username": user_data.get("login"),
        "avatar_url": user_data.get("avatar_url"),
        "name": user_data.get("name") or user_data.get("login"),
        "github_id": str(user_data.get("id"))
    }
