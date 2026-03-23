from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from config import GITHUB_REDIRECT_URI
from services.github_auth_service import exchange_code_for_token, get_github_user_profile
import os

router = APIRouter()

@router.get("/login")
async def github_login():
    """Redirect user to GitHub authorization page."""
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="GitHub Client ID not configured.")
        
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        f"&scope=read:user user:email repo"
    )
    return RedirectResponse(url=github_auth_url)

@router.get("/callback")
async def github_callback(code: str, request: Request):
    """Handle the callback from GitHub, exchange code for token, store in session."""
    try:
        access_token = await exchange_code_for_token(code)
        
        # Store in session securely
        request.session["github_access_token"] = access_token
        
        # Redirect back to the frontend dashboard
        frontend_url = "http://localhost:5173"
        return RedirectResponse(url=frontend_url)
    except HTTPException as e:
        # Pass through expected errors
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/me")
async def get_current_user(request: Request):
    """Return the authenticated user profile."""
    access_token = request.session.get("github_access_token")
    if not access_token:
        # Not logged in
        return JSONResponse(status_code=401, content={"authenticated": False, "message": "Not authenticated"})
        
    try:
        user_profile = await get_github_user_profile(access_token)
        return user_profile
    except HTTPException:
        # Token likely expired or revoked, clear session
        request.session.pop("github_access_token", None)
        return JSONResponse(status_code=401, content={"authenticated": False, "message": "Session expired"})

@router.post("/logout")
async def github_logout(request: Request):
    """Clear the session securely."""
    request.session.clear()
    return JSONResponse(content={"status": "success", "message": "Logged out successfully."})
