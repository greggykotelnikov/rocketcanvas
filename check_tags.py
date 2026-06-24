import os, re
templates_dir = r'c:\Users\kotel\rocketcanvas\templates'
count = 0
for root, _, files in os.walk(templates_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                scripts = re.findall(r'<script[^>]*src=[^>]*>', content)
                for s in scripts:
                    if 'integrity' not in s:
                        print(f'Missing SRI in {f}: {s}')
                        count += 1
                links = re.findall(r'<link[^>]*rel=[\'\"]stylesheet[\'\"][^>]*>', content)
                for l in links:
                    if 'integrity' not in l:
                        print(f'Missing SRI in {f}: {l}')
                        count += 1

print(f"Total missing: {count}")
