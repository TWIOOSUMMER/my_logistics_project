import re

filepath = r'd:\homework\2\my_logistics_project\templates\logistics\index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    pct_open = line.count('{%') - line.count('%}')
    brace_open = line.count('{{') - line.count('}}')
    total_open = pct_open + brace_open
    if total_open > 0 and i + 1 < len(lines):
        merged = line
        i += 1
        while i < len(lines):
            merged = merged.rstrip() + ' ' + lines[i].lstrip()
            pct_open = merged.count('{%') - merged.count('%}')
            brace_open = merged.count('{{') - merged.count('}}')
            if pct_open <= 0 and brace_open <= 0:
                break
            i += 1
        new_lines.append(merged)
    else:
        new_lines.append(line)
    i += 1

fixed = '\n'.join(new_lines)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(fixed)

print('Merged all split Django template tags. File saved.')
