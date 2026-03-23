import os
from dotenv import load_dotenv

load_dotenv(override=True)

MAX_FILES = 5
MAX_LINES_PER_FILE = 1000

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8005/api/auth/github/callback")
SESSION_SECRET = os.getenv("SESSION_SECRET", "super-secret-session-key-change-me")

# Code Patching Configuration
ENABLE_CODE_PATCHING = True
CREATE_FILE_BACKUP = True
