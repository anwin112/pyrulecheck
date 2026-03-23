import ast
from typing import List, Dict

def check_performance(tree: ast.AST, file_content: str, filename: str) -> List[Dict]:
    issues = []
    
    for node in ast.walk(tree):
        # 1. Nested loops
        if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
            for child in ast.walk(node):
                if child is not node and isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                    issues.append({
                        "file": filename, "line": getattr(node, 'lineno', 0),
                        "message": "Nested loop detected. Can lead to O(n^2) or worse performance.",
                        "rule_id": "PERF-001", "severity": "minor"
                    })
                    break # Only report once per outer loop
        
        # 2. Re-computing len() or similar inside loop (Approximation)
        if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    if child.func.id in ['len', 'sum', 'min', 'max']:
                        issues.append({
                            "file": filename, "line": getattr(child, 'lineno', getattr(node, 'lineno', 0)),
                            "message": f"Computation '{child.func.id}()' inside a loop may be inefficient.",
                            "rule_id": "PERF-003", "severity": "minor"
                        })
    return issues
