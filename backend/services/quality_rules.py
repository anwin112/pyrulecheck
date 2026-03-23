import ast
from collections import defaultdict
from typing import List, Dict, Any

def get_cyclomatic_complexity(tree: ast.AST) -> int:
    # A very basic approximation of complexity using AST.
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.AsyncWith, ast.BoolOp)):
            complexity += 1
    return complexity

def get_nesting_depth(node, depth=0):
    max_depth = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            max_depth = max(max_depth, get_nesting_depth(child, depth + 1))
        else:
            max_depth = max(max_depth, get_nesting_depth(child, depth))
    return max_depth

def check_quality(tree: ast.AST, file_content: str, filename: str) -> List[Dict]:
    issues = []
    
    # 1. Missing docstrings for module
    if not ast.get_docstring(tree):
        issues.append({
            "file": filename, "line": 1,
            "message": "Missing module docstring.",
            "rule_id": "QUAL-004", "severity": "minor"
        })

    class_names = set()
    func_names = set()

    for node in ast.iter_child_nodes(tree):
        # 2. Missing docstrings, large functions, too many params
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_names.add(node.name)
            
            # Missing docstring
            if not ast.get_docstring(node):
                issues.append({
                    "file": filename, "line": node.lineno,
                    "message": f"Missing docstring for function '{node.name}'.",
                    "rule_id": "QUAL-004", "severity": "minor"
                })
            
            # Function > 50 lines
            if hasattr(node, "end_lineno") and (node.end_lineno - node.lineno > 50):
                issues.append({
                    "file": filename, "line": node.lineno,
                    "message": f"Function '{node.name}' is too large (> 50 lines).",
                    "rule_id": "QUAL-001", "severity": "major"
                })
                
            # Long parameter lists (> 5 parameters)
            if len(node.args.args) > 5:
                issues.append({
                    "file": filename, "line": node.lineno,
                    "message": f"Function '{node.name}' has too many parameters (> 5).",
                    "rule_id": "QUAL-009", "severity": "major"
                })
        
        # 3. God classes (> 10 methods)
        elif isinstance(node, ast.ClassDef):
            class_names.add(node.name)
            methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            if len(methods) > 10:
                issues.append({
                    "file": filename, "line": node.lineno,
                    "message": f"God class detected: '{node.name}' has more than 10 methods.",
                    "rule_id": "QUAL-010", "severity": "major"
                })

    # Deep nesting > 3 levels
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            depth = get_nesting_depth(node)
            if depth > 3:
                issues.append({
                    "file": filename, "line": node.lineno,
                    "message": f"Function '{node.name}' has deep nesting (> 3 levels).",
                    "rule_id": "QUAL-003", "severity": "major"
                })
    
    return issues
