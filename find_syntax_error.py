import ast
import traceback

with open('healthplan_navigator/output/report.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Try parsing progressively to find where it breaks
for i in range(200, 225):
    try:
        partial_content = '\n'.join(lines[:i+1])
        ast.parse(partial_content)
        print(f"Line {i+1}: OK")
    except Exception as e:
        print(f"Line {i+1}: {type(e).__name__}: {e}")
        print(f"Content of line {i+1}: {repr(lines[i])}")
        break