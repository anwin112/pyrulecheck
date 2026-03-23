import os
import shutil
from services.file_validator import get_python_files, validate_files
from config import MAX_FILES, MAX_LINES_PER_FILE

print(f"Testing against config: MAX_FILES={MAX_FILES}, MAX_LINES={MAX_LINES_PER_FILE}")

# Setup temporary test repository structure
test_dir = "mock_repo_test"
os.makedirs(test_dir, exist_ok=True)

try:
    # Scenario: 6 Python files + 2 text files (Mixed)
    for i in range(6):
        with open(os.path.join(test_dir, f"test_script_{i}.py"), "w", encoding='utf-8') as f:
            f.write("print('hello')\n")
            
    with open(os.path.join(test_dir, "ignore_me.txt"), "w", encoding='utf-8') as f:
        f.write("Plain text file")
    with open(os.path.join(test_dir, "config.json"), "w", encoding='utf-8') as f:
        f.write("{}")

    # TEST: Does it grab exactly 5 files and ignore non-py?
    extracted = get_python_files(test_dir)
    print(f"1) Extracted files count (Expected: 5): {len(extracted)}")
    
    # TEST: Does validation pass for these valid 5 files?
    valid, msg = validate_files(extracted)
    print(f"2) Validate 5 normal files (Expected: True): {valid} {msg}")

    # TEST: 1000 line file (Boundary logic)
    boundary_file = os.path.join(test_dir, "edge_case_1000.py")
    with open(boundary_file, "w", encoding='utf-8') as f:
        for _ in range(1000):
            f.write("pass\n")
    valid, msg = validate_files([boundary_file])
    print(f"3) Validate 1000-line file (Expected: True): {valid} {msg}")

    # TEST: 1001 line file (Over limit)
    huge_file = os.path.join(test_dir, "violation_1001.py")
    with open(huge_file, "w", encoding='utf-8') as f:
        for _ in range(1001):
            f.write("pass\n")
    valid, msg = validate_files([huge_file])
    print(f"4) Validate 1001-line file (Expected: False): {valid} | Message: {msg}")

finally:
    # Cleanup
    shutil.rmtree(test_dir, ignore_errors=True)
