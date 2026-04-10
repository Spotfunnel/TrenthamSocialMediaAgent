"""Build the preview template from the actual Wix blog page.

Strategy: Take the downloaded Wix HTML, find the blog article content,
replace it with a placeholder, and save as template. The server will
inject draft content into the placeholder at runtime.
"""
import re

with open('wix-source.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The blog content lives inside <article>. We need to find the rich text
# content area inside it and replace with our placeholder.
#
# Looking at the structure, the actual blog text starts after the title/author
# and is in a rich text container. We'll find the first paragraph of content
# and replace everything from there to the share buttons.

# Find "sitting on the fence" which is the start of blog body text
body_start_marker = "sitting on the fence"
body_start = html.find(body_start_marker)
print(f"Blog body text found at: {body_start}")

# Go back to find the container div before it
# We need to find the parent of the paragraphs — look for the rich text wrapper
pre_body = html[max(0, body_start - 3000):body_start]

# Find the last occurrence of a major container before the body
# The rich text area is wrapped in a div with data-hook or specific class
container_patterns = [
    'data-hook="post-body"',
    'class="post-content"',
    'rich-text-container',
]

# Actually, let's use a simpler approach: find the title "How to Maximize..."
# and the share buttons, and replace everything between them
title_text = "How to Maximize the Solar Battery Rebate in Victoria (2026 Guide)"
title_idx = html.find(title_text)
print(f"Title found at: {title_idx}")

# Find the title's H1 tag — go back to find <h1
pre_title = html[max(0, title_idx - 500):title_idx]
h1_start = pre_title.rfind('<h1')
actual_h1_start = max(0, title_idx - 500) + h1_start
print(f"H1 tag starts at: {actual_h1_start}")

# Find where the blog content ends — look for share buttons or "Recent Posts"
share_marker = "Share via"
share_idx = html.find(share_marker, body_start)
# Go back to find the container start
if share_idx == -1:
    share_marker = "Recent Posts"
    share_idx = html.find(share_marker, body_start)

print(f"Share/end marker at: {share_idx}")

# Find the div that wraps the share section
pre_share = html[max(0, share_idx - 2000):share_idx]
# Look for a major div boundary
# Actually, let's take a more robust approach:
# Replace the ENTIRE article content section with placeholders

# The blog body is between the author info and the share buttons
# Find: after the author bar, before share buttons
# Author bar ends with the three-dot menu (More actions button)

more_actions = html.find("More actions", title_idx)
if more_actions == -1:
    more_actions = html.find("aria-label=\"More actions\"", title_idx)
print(f"More actions button at: {more_actions}")

# The actual content div starts after the author section
# Let's find the rich text wrapper by looking for the paragraphs
# The first <p in the body area after the author bar
first_p = html.find('<p', more_actions + 50)
# Go back to find the wrapping div
wrap_search = html[max(0, first_p - 1000):first_p]
last_div_open = wrap_search.rfind('<div')
content_wrapper_start = max(0, first_p - 1000) + last_div_open

# For the end: find where the article content ends
# Look for the share buttons section or "Recent Posts"
recent_posts = html.find("Recent Posts", body_start)
if recent_posts == -1:
    recent_posts = html.find("recent-posts", body_start)
print(f"Recent Posts at: {recent_posts}")

# The content section ends somewhere between share buttons and recent posts
# Let's find the closing </article> tag
article_end = html.find("</article>", body_start)
print(f"</article> at: {article_end}")

# APPROACH: Instead of surgical replacement, we'll split the page into 3 parts:
# 1. Everything before the blog body (header, nav, title, author bar)
# 2. The blog body (to be replaced with our content)
# 3. Everything after (share buttons, recent posts, footer)

# Split point 1: right after the title H1 closes
# The body content div starts right after the author/title section
# Let's find the specific div that contains the paragraphs

# Find all <p tags near the first paragraph
# The first meaningful paragraph starts at body_start - some offset
# Let's capture from after the H1 title to before the share buttons

# Find the </h1> after the title
h1_end = html.find('</h1>', title_idx) + 5
print(f"</h1> at: {h1_end}")

# After the H1, there's the author info, then the content div
# The content starts in a div with specific Wix classes
# Let's use the text itself as boundary

# FINAL APPROACH: simple text markers
# PART A: everything from start to just before first body paragraph
# Insert marker: {{BLOG_TITLE}} for the title
# Insert marker: {{BLOG_BODY}} for the body content
# Insert marker: {{BLOG_AUTHOR_DATE}} for the date

# Replace the title text with placeholder
template = html.replace(title_text, '{{BLOG_TITLE}}')

# Replace the body content: from first paragraph to share buttons
# Find the first body paragraph in the template
first_para_text = "sitting on the fence"
fp_idx = template.find(first_para_text)

# Go back to find the opening tag of the containing div
# We need to find where the rich text content starts
# Look for the data container div
search_back = template[max(0, fp_idx - 5000):fp_idx]

# Find the parent div that wraps all the rich text paragraphs
# It's a div right after the author section that contains all <p, <h2 tags
# Let's find the </div> pattern that ends the author section, then the next <div

# Simpler: find "data-hook" near the content area
data_hooks = [(m.start(), m.group()) for m in re.finditer(r'data-hook="[^"]*"', search_back)]
print(f"\nData hooks near content: {len(data_hooks)}")
for start, hook in data_hooks[-5:]:
    print(f"  {hook}")

# Save what we have so far as analysis
print(f"\nTemplate length: {len(template)}")
print("Saving template approach...")

# The cleanest approach for production:
# Don't try to surgically edit the Wix HTML.
# Instead, save the FULL page HTML and load it in an iframe,
# or build a clean HTML page that copies the EXACT CSS from Wix.

# Let's extract just the CSS we need and the structural HTML
# for header and footer, then build a clean template.

# Save the header HTML (from page start to blog area)
header_section = template[:actual_h1_start]
# Save the footer HTML (from after article to end)
footer_section = template[article_end + 10:]

with open('template-header.html', 'w', encoding='utf-8') as f:
    f.write(header_section)
print(f"Saved header section: {len(header_section)} chars")

with open('template-footer.html', 'w', encoding='utf-8') as f:
    f.write(footer_section)
print(f"Saved footer section: {len(footer_section)} chars")
