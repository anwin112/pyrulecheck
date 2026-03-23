import os
import shutil
import subprocess
import tempfile

def clone_repository(github_url: str) -> str:
    """Clones a GitHub repository to a temporary directory and returns the path."""
    temp_dir = tempfile.mkdtemp(prefix="pyrulecheck_")
    
    # Safe subprocess call
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", github_url, temp_dir],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError(f"Failed to clone repository: {e.stderr}")
    return temp_dir

def cleanup_repository(temp_dir: str):
    """Safely removes the temporary directory."""
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
