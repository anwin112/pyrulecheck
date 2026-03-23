import ast
import re
from typing import List, Dict

def check_security(tree: ast.AST, file_content: str, filename: str) -> List[Dict]:
    issues = []
    
    # 1. Hardcoded secrets (basic regex check on strings)
    secret_patterns = [
        re.compile(r'(?i)(api[_-]?key|secret|password|token)\s*=\s*[\'"].+[\'"]')
    ]
    for line_no, line in enumerate(file_content.splitlines(), start=1):
        for pattern in secret_patterns:
            if pattern.search(line):
                issues.append({
                    "file": filename, "line": line_no,
                    "message": "Potential hardcoded secret discovered",
                    "rule_id": "SEC-001", "severity": "critical"
                })

    # AST Walk
    for node in ast.walk(tree):
        # 2. Use of eval() or exec()
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec']:
                issues.append({
                    "file": filename, "line": getattr(node, 'lineno', 0),
                    "message": f"Use of {node.func.id}() is highly discouraged/unsafe.",
                    "rule_id": "SEC-002", "severity": "critical"
                })
        
        # 3. SQL string concatenation (rough approximation: variable inside string or f-string with sql keywords)
        # Note: We can look at f-strings
        if isinstance(node, ast.JoinedStr):
            # check if it contains sql keywords like SELECT, INSERT, etc
            f_str_content = "".join([v.value for v in node.values if isinstance(v, ast.Constant) and isinstance(v.value, str)])
            if any(keyword in f_str_content.upper() for keyword in ["SELECT ", "INSERT ", "UPDATE ", "DELETE "]):
                issues.append({
                    "file": filename, "line": getattr(node, 'lineno', 0),
                    "message": "Potential SQL injection: built SQL query via string interpolation.",
                    "rule_id": "SEC-006", "severity": "critical"
                })

        # 4. Weak hashing
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'hashlib':
                if node.func.attr in ['md5', 'sha1']:
                    issues.append({
                        "file": filename, "line": getattr(node, 'lineno', 0),
                        "message": f"Weak hashing algorithm detected: hashlib.{node.func.attr}()",
                        "rule_id": "SEC-008", "severity": "major"
                    })
        
        # 5. Broad exception catching
        if isinstance(node, ast.ExceptHandler):
            if node.type is None or (isinstance(node.type, ast.Name) and node.type.id == "Exception"):
                issues.append({
                    "file": filename, "line": getattr(node, 'lineno', 0),
                    "message": "Broad exception catching (except: or except Exception:)",
                    "rule_id": "SEC-009", "severity": "minor"
                })

    return issues
