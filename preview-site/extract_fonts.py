import re
with open('../.firecrawl/wix-blog-html.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find @font-face blocks
faces = re.findall(r'@font-face\s*\{([^}]+)\}', html)
print(f'{len(faces)} @font-face declarations')
for face in faces[:20]:
    family = re.search(r'font-family:\s*([^;]+)', face)
    src_match = re.search(r'url\(([^)]+)\)', face)
    if family:
        fam = family.group(1).strip().strip('"').strip("'")
        url = src_match.group(1).strip().strip('"').strip("'") if src_match else 'no-url'
        if 'wfont' in fam or 'din' in fam.lower() or 'myriad' in fam.lower():
            print(f'  {fam}')
            print(f'    -> {url[:130]}')

# Find all woff/woff2 font file URLs
font_urls = re.findall(r'(https://[^\s"\'<>]+\.woff2?)', html)
print(f'\n{len(font_urls)} woff/woff2 URLs')
for u in sorted(set(font_urls)):
    print(f'  {u[:130]}')
