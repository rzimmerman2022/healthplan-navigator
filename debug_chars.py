with open('healthplan_navigator/output/report.py', 'r', encoding='utf-8') as f:
    content = f.read()

line_start = content.find('body {{ font-family')
snippet = content[line_start:line_start+100]
print('First 50 characters of the problematic line:')
for i, char in enumerate(snippet[:50]):
    print(f'{i:2d}: {repr(char):6s} ({ord(char):3d})')