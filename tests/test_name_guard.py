import ast
import builtins
import sys
from pathlib import Path

def find_undefined_names(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)
    
    defined = set(dir(builtins))
    defined.update({'__name__', '__file__', '__doc__', '__path__'})
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined.add(node.id)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                defined.add(alias.asname or alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined.add(alias.asname or alias.name)
        elif isinstance(node, ast.alias):
            defined.add(node.asname or node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            defined.add(node.name)
            
    undefined = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in defined:
                undefined.append((node.id, node.lineno))
                
    return undefined

def test_no_undefined_names():
    src_dir = Path("src/snowline")
    all_undefined = {}
    for py_file in src_dir.rglob("*.py"):
        res = find_undefined_names(str(py_file))
        if res:
            all_undefined[str(py_file)] = res
            
    if all_undefined:
        errors = []
        for f, undefs in all_undefined.items():
            for name, line in undefs:
                errors.append(f"File {f}, line {line}: {name}")
        error_msg = "Undefined names found:\n" + "\n".join(errors)
        assert False, error_msg

if __name__ == '__main__':
    test_no_undefined_names()
    print("ALL GREEN")