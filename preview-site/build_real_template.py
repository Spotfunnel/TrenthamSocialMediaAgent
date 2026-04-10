"""Build template by taking the ACTUAL Wix page and replacing only the blog content.

Downloads the real page, finds the article body text, replaces it with a placeholder
marker, and saves as template. Server injects draft content at the marker.
"""
import re

with open('wix-source.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The blog body paragraphs sit inside a specific container.
# Strategy: find the first body paragraph text and the last body paragraph text,
# then replace everything between with a single marker.

# First paragraph starts with "If you've been sitting on the fence"
first_text = "sitting on the fence"
first_idx = html.find(first_text)
print(f"First body text at: {first_idx}")

# Last paragraph ends with the contact CTA
last_text = "what a solar and battery system could do for your home"
last_idx = html.find(last_text)
print(f"Last body text at: {last_idx}")

# We need to find the containing elements.
# Go back from first_idx to find the opening <div or <p that contains it
# Go forward from last_idx to find the closing </p> or </div>

# Find the parent rich text container by going back to find data-hook or class
pre = html[max(0, first_idx - 5000):first_idx]

# Find the <article> tag — that's our outer boundary
article_start = html.rfind('<article', 0, first_idx)
article_end = html.find('</article>', last_idx) + len('</article>')
print(f"Article: {article_start} to {article_end}")

# Inside the article, the structure is:
# - title section (h1, author bar)
# - content body (all the paragraphs, headings, images)
# - share buttons
#
# We want to keep the article wrapper but replace the content body.
# The content body starts after the author section and ends before share buttons.

# Find the title H1 - it contains the actual title text
title_text = "How to Maximize the Solar Battery Rebate in Victoria (2026 Guide)"
title_idx = html.find(title_text)

# The "More actions" button is the end of the author/title section
more_actions_idx = html.find('More actions', title_idx)
# Find the </button> after "More actions"
more_btn_end = html.find('</button>', more_actions_idx) + len('</button>')
# Find the next </div> that closes the author section
author_section_end = html.find('</div>', more_btn_end) + len('</div>')

# After the author section, there's a content wrapper div
# Find it by looking for the next <div after author_section_end
content_div_start = html.find('<div', author_section_end)
print(f"Content div starts at: {content_div_start}")

# The share buttons section — find "Share via Facebook" or similar
share_idx = html.find('Share via Facebook', last_idx)
if share_idx == -1:
    share_idx = html.find('share', last_idx)
print(f"Share section at: {share_idx}")

# Go back from share to find its container div opening
pre_share = html[max(0, share_idx - 2000):share_idx]
# Find the last major <div before the share section
share_container_pattern = re.findall(r'<div[^>]*>', pre_share)
# The share container is likely the last few divs
share_container_start = share_idx - 2000 + pre_share.rfind('<div')
print(f"Share container starts at: {share_container_start}")

# APPROACH: Split the page into:
# PART 1: everything from start to content_div_start (header, nav, title, author)
# PART 2: replaced with {{BLOG_BODY}} marker
# PART 3: everything from share_container_start to end (share, recent posts, footer)

# But we also need to replace the title text
part1 = html[:content_div_start]
part3 = html[share_container_start:]

# Replace the title in part1
part1 = part1.replace(title_text, '{{BLOG_TITLE}}')

# Also replace the <title> tag content
part1 = re.sub(r'<title>[^<]*</title>', '<title>{{BLOG_TITLE}} | Trentham Electrical &amp; Solar</title>', part1)

# Replace meta description
part1 = re.sub(r'<meta property="og:description" content="[^"]*"', '<meta property="og:description" content="{{BLOG_META}}"', part1)

# Add draft preview banner right after <body>
part1 = part1.replace('<body ', '<body data-preview="true" ')
# Insert banner after the first element inside body
body_idx = part1.find('<body')
body_tag_end = part1.find('>', body_idx) + 1
part1 = part1[:body_tag_end] + '\n<div style="background:#fff3cd;border-bottom:1px solid #edd078;text-align:center;padding:6px;font-size:11px;font-weight:600;color:#866404;letter-spacing:.8px;text-transform:uppercase;position:fixed;top:0;left:0;right:0;z-index:99999">DRAFT PREVIEW — Not published on the live website</div>\n' + part1[body_tag_end:]

# Build template
template = part1 + '\n<div class="blog-draft-content" style="padding:0">\n{{BLOG_BODY}}\n</div>\n' + part3

# Save
with open('page-template.html', 'w', encoding='utf-8') as f:
    f.write(template)

print(f"\nTemplate saved: {len(template)} chars")
print(f"Part 1 (header/title): {len(part1)} chars")
print(f"Part 3 (share/footer): {len(part3)} chars")
print(f"Markers: {{BLOG_TITLE}}, {{BLOG_META}}, {{BLOG_BODY}}")
