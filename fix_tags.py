import re

path = 'templates/logistics/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
clean_lines = []
for line in lines:
    if '{{' in line and '}}' in line:
        line = re.sub(r' {2,}', ' ', line)
    clean_lines.append(line)
content = '\n'.join(clean_lines)

lines = content.split('\n')
fixed = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.rstrip()

    open_tags = stripped.count('{%')
    close_tags = stripped.count('%}')
    open_vars = stripped.count('{{')
    close_vars = stripped.count('}}')

    unbalanced = (open_tags > close_tags) or (open_vars > close_vars)

    if unbalanced:
        combined = stripped
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            combined += ' ' + nxt
            i += 1
            if combined.count('{%') <= combined.count('%}') and combined.count('{{') <= combined.count('}}'):
                break
        fixed.append(combined + '\n')
    else:
        fixed.append(line + '\n')
        i += 1

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(fixed)

print('Fixed all split Django tags and variables')
