"""Analyze Wix source HTML to extract styling."""
import re

with open('wix-source.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find style blocks with relevant content
styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
print(f'{len(styles)} style blocks found')

for i, s in enumerate(styles):
    has_colors = '--color_' in s
    has_fonts = '--font_' in s or 'din-next' in s
    has_blog = 'richTextParagraph' in s or 'MMl86N' in s or 'ku3DBC' in s
    markers = []
    if has_colors: markers.append('COLORS')
    if has_fonts: markers.append('FONTS')
    if has_blog: markers.append('BLOG')
    if markers:
        print(f'  Block {i}: {len(s)} chars [{" | ".join(markers)}]')

# Save the blog-relevant style block
for i, s in enumerate(styles):
    if 'ku3DBC' in s or 'MMl86N' in s:
        with open(f'wix-blog-styles-{i}.css', 'w', encoding='utf-8') as f:
            f.write(s)
        print(f'  Saved block {i} to wix-blog-styles-{i}.css')

# Save the colors/fonts style block
for i, s in enumerate(styles):
    if '--color_19' in s and '--font_1' in s:
        with open(f'wix-vars-{i}.css', 'w', encoding='utf-8') as f:
            f.write(s)
        print(f'  Saved vars block {i} to wix-vars-{i}.css')

# Extract the header section HTML (simplified)
# Find the <header> element
header_match = re.search(r'<header[^>]*id="SITE_HEADER"[^>]*>(.*?)</header>', html, re.DOTALL)
if header_match:
    header_html = header_match.group(0)
    print(f'\nHeader HTML: {len(header_html)} chars')
    with open('wix-header.html', 'w', encoding='utf-8') as f:
        f.write(header_html)
    print('  Saved to wix-header.html')
else:
    print('\nHeader not found as <header> tag, trying alternate...')
    idx = html.find('SITE_HEADER_WRAPPER')
    if idx > -1:
        chunk = html[max(0, idx-100):idx+5000]
        print(f'  Found SITE_HEADER_WRAPPER, chunk: {len(chunk)} chars')

# Extract footer section
footer_match = re.search(r'<footer[^>]*id="SITE_FOOTER"[^>]*>(.*?)</footer>', html, re.DOTALL)
if footer_match:
    footer_html = footer_match.group(0)
    print(f'\nFooter HTML: {len(footer_html)} chars')
    with open('wix-footer.html', 'w', encoding='utf-8') as f:
        f.write(footer_html)
    print('  Saved to wix-footer.html')
else:
    print('\nFooter not found as <footer> tag')
