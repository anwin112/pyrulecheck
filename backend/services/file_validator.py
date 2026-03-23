import os
from typing import List, Tuple
from config import MAX_FILES, MAX_LINES_PER_FILE

def get_python_files(repo_path: str) -> List[str]:
    """Extracts all .py files from the repository."""
    py_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
                if len(py_files) >= MAX_FILES:
                    return py_files
    return py_files

def validate_files(py_files: List[str]) -> Tuple[bool, str]:
    """
    Validates the files against the constraints:
    - Max 3 Python files
    - Max 500 lines per file
    - At least 1 Python file
    """
    if not py_files:
        return False, "No Python files found in the repository."
    
    if len(py_files) > MAX_FILES:
        py_files[:] = py_files[:MAX_FILES]  # Mutate in place to guarantee system bounds
    
    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f)
                if lines > MAX_LINES_PER_FILE:
                    filename = os.path.basename(file_path)
                    return False, f"File exceeds maximum allowed length of {MAX_LINES_PER_FILE} lines."
        except Exception as e:
            return False, f"Could not read file {os.path.basename(file_path)}: {str(e)}"
            
    return True, ""
