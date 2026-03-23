from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from routes import router as analyze_router
from auth_routes import router as auth_router
from github_repo_routes import router as github_repos_router
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
from config import SESSION_SECRET

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="PyRuleCheck API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"], # Must be specific for credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, max_age=86400) # 24 hour session

app.include_router(analyze_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth/github")
app.include_router(github_repos_router, prefix="/api/github/repos")

@app.get("/")
def read_root():
    return {"message": "PyRuleCheck API is running"}
