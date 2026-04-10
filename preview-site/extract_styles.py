"""Extract exact styling from downloaded Wix page."""
import re

with open('wix-source.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find wfont references
wfont_refs = re.findall(r'wfont_\w+_\w+', html)
print('=== WFONT REFS (unique) ===')
for w in sorted(set(wfont_refs)):
    print(f'  {w}')

# Find font-family declarations with actual names
font_families = re.findall(r'font-family:\s*([^;}{]+);', html)
print('\n=== FONT-FAMILY declarations (unique, first 20) ===')
seen = set()
for f in font_families:
    clean = f.strip()
    if clean not in seen and len(clean) < 200:
        seen.add(clean)
        if 'din' in clean.lower() or 'wfont' in clean.lower() or 'serif' in clean.lower():
            print(f'  {clean}')

# Extract complete <style> blocks
styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
print(f'\n=== STYLE BLOCKS: {len(styles)} ===')

# Find header background color
for s in styles:
    if 'SITE_HEADER' in s or 'headerBg' in s or '#4B0082' in s or 'rgb(75' in s:
        # Extract bg colors near header references
        bg_matches = re.findall(r'background(?:-color)?:\s*([^;]{3,50});', s)
        for b in bg_matches:
            if 'rgb' in b or '#' in b:
                print(f'  Header-area bg: {b.strip()}')

# Find the actual rendered header background from inline styles
header_inline = re.findall(r'data-testid="inline-content"[^>]*style="([^"]+)"', html)
print(f'\n=== INLINE CONTENT STYLES ===')
for h in header_inline[:5]:
    print(f'  {h[:200]}')

# Find specific section backgrounds
bg_sections = re.findall(r'background(?:-color)?:\s*rgb\((\d+,\s*\d+,\s*\d+)\)', html)
print(f'\n=== ALL RGB BACKGROUNDS (unique) ===')
for b in sorted(set(bg_sections)):
    r, g, bl = [int(x.strip()) for x in b.split(',')]
    print(f'  rgb({b}) = #{r:02x}{g:02x}{bl:02x}')

# Find the blog post content area structure
# Look for the actual blog text to find its container classes
rebate_idx = html.find('sitting on the fence')
if rebate_idx > -1:
    chunk = html[max(0, rebate_idx-2000):rebate_idx+500]
    classes = re.findall(r'class="([^"]+)"', chunk)
    print(f'\n=== CLASSES NEAR BLOG CONTENT ===')
    for c in classes[-15:]:
        print(f'  .{c}')

# Extract font CSS URLs
font_css_urls = re.findall(r'href="(https://[^"]*fonts[^"]*)"', html)
print(f'\n=== FONT CSS URLs ===')
for u in font_css_urls[:5]:
    print(f'  {u[:150]}')
