python -c "
import ast
tree = ast.parse(open('project_starter.py').read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f'{node.name}  (line {node.lineno})')
"

python -c "import ast; ast.parse(open('project_template.py').read()); print('Syntax OK')"
python -c "from project_template import handle_customer_request; print('Import OK')"