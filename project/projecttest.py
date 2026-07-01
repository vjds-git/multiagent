
import ast
tree = ast.parse(open('project_starter.py').read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f'{node.name}  (line {node.lineno})')
"

python -c "
import pandas as pd
df = pd.read_csv('test_results.csv')
fulfilled = df[df['response'].str.contains('confirmed|purchased|processed|successfully', case=False, na=False)]
declined = df[~df['response'].str.contains('confirmed|purchased|processed|successfully', case=False, na=False)]
print('Total requests:', len(df))
print('Fulfilled:', len(fulfilled))
print('Declined:', len(declined))
print('Starting cash:', df['cash_balance'].iloc[0])
print('Final cash:', df['cash_balance'].iloc[-1])
cash_changes = df['cash_balance'].diff().dropna()
print('Rows with cash change:', (cash_changes != 0).sum())
"