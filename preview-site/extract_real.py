import re

with open('wix-source.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find ALL wixstatic image URLs
pattern = r'https://static\.wixstatic\.com/media/[^\s"<>)]+?\.(?:png|jpg|jpeg|svg|webp)[^\s"<>)]*'
imgs = sorted(set(re.findall(pattern, html)))
print(f'=== {len(imgs)} WIXSTATIC IMAGES ===')
for i in imgs:
    print(f'  {i[:150]}')

# Find phone number location - the header
phone_idx = html.find('1300 3458 00')
print(f'\nPhone at: {phone_idx}')

# Get the region around the phone (header area)
if phone_idx > -1:
    region = html[max(0, phone_idx-3000):phone_idx+3000]

    # Find img tags
    img_tags = re.findall(r'<img[^>]+>', region)
    print(f'\nImg tags near header: {len(img_tags)}')
    for it in img_tags:
        src = re.search(r'src="([^"]+)"', it)
        alt = re.search(r'alt="([^"]+)"', it)
        if src:
            print(f'  src: {src.group(1)[:120]}')
            if alt:
                print(f'  alt: {alt.group(1)[:80]}')

    # Find background colors as inline styles
    styles_with_bg = re.findall(r'style="[^"]*(?:background|bg)[^"]*"', region)
    print(f'\nBackground styles in header region: {len(styles_with_bg)}')
    for s in styles_with_bg[:5]:
        print(f'  {s[:200]}')

# Find the nav area
for item in ['HOME', 'ABOUT', 'SOLAR']:
    idx = html.find('>' + item + '<')
    if idx > -1:
        chunk = html[max(0, idx-100):idx+100]
        print(f'\nNav "{item}" context: ...{chunk}...')
        break

# Find the actual header background - look for the wrapper style
header_wrapper = html.find('SITE_HEADER_WRAPPER')
if header_wrapper > -1:
    hw_chunk = html[header_wrapper:header_wrapper+5000]
    inline_styles = re.findall(r'style="([^"]{10,200})"', hw_chunk)
    print(f'\nHeader wrapper inline styles:')
    for s in inline_styles[:10]:
        if 'background' in s or 'color' in s or 'rgb' in s:
            print(f'  {s}')
