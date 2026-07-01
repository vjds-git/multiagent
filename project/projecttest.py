
import ast
tree = ast.parse(open('project_starter.py').read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f'{node.name}  (line {node.lineno})')