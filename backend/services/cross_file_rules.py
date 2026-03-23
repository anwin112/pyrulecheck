import os
import ast
from typing import List, Dict, Tuple, Set

def analyze_cross_file_rules(files_data: List[Tuple[str, ast.AST]]) -> Dict[str, List[str]]:
    results: Dict[str, List[str]] = {
        "circular_imports": [],
        "shared_globals": [],
        "duplicate_classes": [],
        "unresolved_imports": []
    }
    
    imports_map: Dict[str, Set[str]] = {}
    class_map: Dict[str, str] = {}
    # Map from module name to its full filepath
    module_to_path: Dict[str, str] = {}
    
    for filepath, tree in files_data:
        filename = os.path.basename(filepath)
        mod_name = os.path.splitext(filename)[0]
        module_to_path[mod_name] = filepath
        imports_map[mod_name] = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split('.')[0]
                    imports_map[mod_name].add(root_mod)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split('.')[0]
                    imports_map[mod_name].add(root_mod)
                # Handle relative imports without module name (e.g., from . import x)
                elif node.level > 0:
                    # In this simple engine, we might not resolve these perfectly
                    pass
            elif isinstance(node, ast.ClassDef):
                if node.name in class_map:
                    if class_map[node.name] != filename:
                        results["duplicate_classes"].append(f"Class '{node.name}' found in both {class_map[node.name]} and {filename}")
                else:
                    class_map[node.name] = filename
    
    # Check for simple circular imports and unresolved local imports
    analyzed_modules = list(imports_map.keys())
    for mod, imported_mods in imports_map.items():
        for imported_mod in imported_mods:
            if imported_mod in analyzed_modules:
                if mod != imported_mod:
                    # Check if imported_mod imports mod
                    if mod in imports_map.get(imported_mod, set()):
                        pair = tuple(sorted([mod, imported_mod]))
                        msg = f"Circular import between {pair[0]}.py and {pair[1]}.py"
                        if msg not in results["circular_imports"]:
                            results["circular_imports"].append(msg)
            else:
                # This could be a standard library or an unresolved local import
                # For this MVP, we only care if it 'looks' like it should be here but isn't
                # However, without a list of all project files, we can't be sure.
                pass
                        
    return results
