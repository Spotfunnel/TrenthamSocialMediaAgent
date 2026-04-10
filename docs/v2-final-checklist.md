# V2 Final Checklist — Every Function End-to-End

**Progress: 21/33 verified (64%)**

```
[████████████████░░░░░░░░] 64%
```

Status: ✅ Verified | ⬜ Untested | ❌ Failed | 🔧 Known Issue

---

## SOCIAL POSTS

### ✅ F1: Create social post with detailed specs
- ✅ All specs preserved (9kW, Kyneton, SMA, Trina, Jake)
- ✅ 50-120 words before hashtags (91 words)
- ✅ Emojis present (3)
- ✅ FB different from IG (fewer hashtags, 6 vs 10)
- ✅ GBP: no hashtags, no emojis, consultative
- ✅ Image from Drive (lh3 URL)
- ✅ telegram_message_id saved
- ✅ Preview: 3 tabs (IG/Google/FB), image renders

### ✅ F2: Platform filter (IG + Facebook only)
- ✅ GBP content empty
- ✅ Platforms = fb_ig
- ✅ Preview: only 2 tabs (IG/FB, no Google)
- ✅ Different image from F1

### ✅ F3: No hashtags
- ✅ Zero # in IG caption
- ✅ Zero # in FB caption
- ✅ Different image from F1 and F2

### ⬜ F4: Remove IG and FB, keep only GBP
- ⬜ Reply: "Remove Instagram and Facebook, keep only Google Business"
- ⬜ IG empty, FB empty, GBP preserved
- ⬜ Preview: only Google tab

### ✅ F5: 3-photo carousel from Drive
- ✅ 3 images in draft (carousel)
- ✅ Preview: 1/3 counter, dots, swipeable
- ✅ 3 tabs (IG/Google/FB)

### ✅ F6: Image LRU — no repeats
- ✅ 3 social posts have 3 different image IDs
- ✅ Images logged to Used Images table

### ⬜ F7: Edit social — GBP removal via Telegram reply
- ⬜ Reply to F1's "Draft created!" message: "Remove GBP"
- ⬜ GBP removed from correct draft (reply tracking)
- ⬜ Other drafts untouched
- ⬜ Response shows "Platforms: IG + FB" (not "IG:")
- ⬜ Preview: Google tab removed

### ⬜ F8: Edit social — caption change via Telegram reply
- ⬜ Reply to same draft: "Mention the purple van"
- ⬜ "purple van" in caption
- ⬜ Correct draft edited (reply to LATEST bot message works)

### ⬜ F9: Edit chain — reply to edit RESPONSE message
- ⬜ Reply to F8's "Caption updated" response: "Make it shorter"
- ⬜ Same draft edited (telegram_message_id chain follows latest message)

---

## BLOG

### ✅ F10: Create blog with web search research
- ✅ 4 unique images (cover + hero + 2 body)
- ✅ 600-1200 words (906)
- ✅ 6-8 H2 headings (8)
- ✅ Web search performed (6 searches)
- ✅ Brand guide + examples in prompt
- ✅ SEO validation passed
- ✅ Judge loop ran (PassFail node)
- ✅ telegram_message_id saved
- ✅ Preview desktop: hero image, title, intro styled
- ✅ Preview mobile: headers readable, layout clean

### ⬜ F11: Edit blog text via Telegram reply
- ⬜ Reply to blog "Blog draft created!" message: "Make intro shorter, add CEC mention"
- ⬜ Blog body updated
- ⬜ Preview shows changes
- ⬜ Correct draft via reply tracking

### ⬜ F12: Blog photo swap via Telegram reply
- ⬜ Reply: "Swap the cover image"
- ⬜ Bot responds asking for replacement photo OR swaps from Drive
- ⬜ telegram_message_id updated on response

### ⬜ F13: Blog text edit — reply to edit response
- ⬜ Reply to F11's "Blog updated" response with another edit
- ⬜ Correct draft edited (chain follows latest message)

### ⬜ F14: Delete blog
- ⬜ Reply to blog: "Delete this blog"
- ⬜ Wix DELETE API called (if wix_post_id exists)
- ⬜ Draft status = "deleted"
- ⬜ Telegram confirms deletion

---

## LOOKUP + PLANNER

### ✅ F15: Lookup drafts
- ✅ Correct count of pending drafts
- ✅ Lists social + blog types with briefs
- ✅ Sent directly to Telegram (tool_sent)

### ✅ F16: Weekly planner
- ✅ 3 posts planned with topic descriptions
- ✅ Briefs not truncated (200 chars visible)
- ✅ "Say 'generate all'" hint shown
- ✅ Topic rotation advances

### ✅ F17: Vague brief
- ✅ Agent asks for topic/detail
- ✅ Doesn't create empty post

### ✅ F18: Conversational
- ✅ Single response listing capabilities
- ✅ No duplicate messages

### ⬜ F19: Search Drive folder
- ⬜ Send: "Search the Solar folder"
- ⬜ Returns image list from Solar folder

---

## TELEGRAM PHOTO TESTS (Leo sends photos to bot)

### ✅ T1: Single photo + caption
- ✅ Send 1 photo with caption — post uses Telegram photo
- ✅ Leo verified manually

### ✅ T2: 3-photo carousel via Telegram
- ✅ Send 3 photos as album — all 3 captured
- ✅ MediaGroupGate → Wait5s → ResolvePhotos chain works
- ✅ Leo verified manually

### ✅ T3: 2 photos for blog
- ✅ Send 2 photos with blog request — blog created
- ✅ Leo verified manually

### ✅ T4: 4 photos for blog
- ✅ All 4 slots from Telegram photos
- ✅ Leo verified manually

---

## PREVIEW PAGES

### ✅ PR1: Social carousel preview
- ✅ 1/3 counter visible
- ✅ Dots at bottom
- ✅ 3 tabs (IG/Google/FB)

### ✅ PR2: GBP More button
- ✅ Leo verified manually — text expands on click

### ✅ PR3: Blog preview desktop
- ✅ Hero image at top
- ✅ Title large and clear
- ✅ Intro paragraph styled (bold, distinct)

### ✅ PR4: Blog preview mobile (390px)
- ✅ Title readable
- ✅ H2 headings visible
- ✅ Images render

### ✅ PR5: Blog card list page
- ✅ 6 cards visible
- ✅ Full-width single column on mobile
- ✅ Title below image (not overlaid on gradient)
- ✅ Clean white background

### ✅ PR6: Deleted draft fallback
- ✅ "DRAFT NOT FOUND" shown
- ✅ No fake demo content

---

## PUBLISH + DELETE (requires live API keys)

### ⬜ P1: Approve blog → Wix publish
- ⬜ Reply "Approve" to a blog draft
- ⬜ Wix API: POST draft + PATCH cover + publish
- ⬜ wix_post_id stored on draft
- ⬜ Status = "published"
- ⬜ Telegram shows published URL
- ⬜ Blog visible on trenthamelectrical.com/insights

### ⬜ P2: Delete published blog from Wix
- ⬜ Reply "Delete this blog" to published blog
- ⬜ Wix DELETE API called
- ⬜ Status = "deleted"
- ⬜ Blog removed from live site

### ⬜ P3: Approve social → Buffer draft
- ⬜ Reply "Approve" to social post
- ⬜ Buffer API called (saveToDraft: true)
- ⬜ Status = "published"

### ⬜ P4: Weekly scheduled trigger
- ⬜ Cron fires Monday 4AM UTC
- ⬜ Agent calls plan_weekly_posts
- ⬜ Plan sent to Telegram

---

## SUMMARY

| Category | Verified | Untested | Total |
|----------|----------|----------|-------|
| Social posts | 6 | 3 | 9 |
| Blog | 1 | 4 | 5 |
| Lookup/Plan/Chat | 4 | 1 | 5 |
| Telegram photos | 0 | 4 | 4 |
| Preview pages | 5 | 1 | 6 |
| Publish/Delete | 0 | 4 | 4 |
| **Total** | **16** | **17** | **33** |

### What's needed to complete:
- **F4, F7-F9, F11-F14, F19:** Telegram reply tests (need Playwright or Leo manual)
- **T1-T4:** Photo sends (Leo must send actual photos to bot)
- **P1-P4:** Live publish/delete (requires Wix API key in V2 Config + Buffer key active)
- **PR2:** GBP More button (need a draft with long GBP text)
