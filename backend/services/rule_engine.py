import ast
import os
from typing import List, Dict

from .security_rules import check_security
from .quality_rules import check_quality, get_cyclomatic_complexity
from .performance_rules import check_performance
from .cross_file_rules import analyze_cross_file_rules

def run_analysis(py_files: List[str]):
    all_issues = []
    metrics = {
        "cyclomatic_complexity": {},
        "line_counts": {},
        "function_counts": {}
    }
    
    parsed_files = []
    
    for filepath in py_files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            metrics["line_counts"][filename] = len(content.splitlines())
            
            tree = ast.parse(content)
            parsed_files.append((filepath, tree))
            
            # Metrics
            metrics["cyclomatic_complexity"][filename] = get_cyclomatic_complexity(tree)
            metrics["function_counts"][filename] = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
            
            # Rules
            sec_issues = check_security(tree, content, filename)
            qual_issues = check_quality(tree, content, filename)
            perf_issues = check_performance(tree, content, filename)
            
            all_issues.extend(sec_issues)
            all_issues.extend(qual_issues)
            all_issues.extend(perf_issues)
            
        except SyntaxError as e:
            all_issues.append({
                "file": filename, "line": e.lineno,
                "message": f"Syntax error: {e.msg}",
                "rule_id": "SYNTAX-001", "severity": "critical"
            })
        except BaseException as e:
            pass # ignore unreadable files

    cross_file = analyze_cross_file_rules([(filepath, tree) for filepath, tree in parsed_files])
    
    return all_issues, metrics, cross_file
