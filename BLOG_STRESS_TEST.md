# Blog Agent — Comprehensive Stress Test Plan

All tests via Telegram (Playwright on Telegram Web). No publishing to Wix.

---

## SECTION A: Core Blog Generation

### A1. New blog — clear topic
**Send:** "Write a blog about solar panel cleaning tips for Macedon Ranges homes"
**Success:** Ack within 5s → preview within 90s → 4 images → judge score shown → preview link works → no duplicate heading under title

### A2. New blog — vague topic
**Send:** "Write a blog"
**Success:** Bot asks for more detail, halts processing. No blog generated.

### A3. New blog — very short topic
**Send:** "Blog about batteries"
**Success:** Blog generates (doesn't refuse). Topic inferred correctly. Content is about battery storage.

### A4. New blog — off-topic (should still generate)
**Send:** "Write a blog about degradation"
**Success:** Blog generates about solar panel degradation (not refused). Previous bug: "degradation" was blocked as off-topic.

### A5. New blog — completely unrelated
**Send:** "Write a blog about jujutsu kaisen"
**Success:** Blog generates (we removed topic blocking). Content may be off-topic but system doesn't crash.

### A6. New blog — with Drive folder reference
**Send:** "Write a blog about the install at Solar folder, use photos from there"
**Success:** Ack says "searching Drive for 'Solar' photos..." → blog uses images from Solar Drive folder → preview shows Drive-sourced images.

---

## SECTION B: Targeted Edits (reply to draft)

### B1. Add content
**Reply to preview:** "Add a paragraph about the Victorian battery rebate being $2,950"
**Success:** Preview updates with new paragraph. Rest of blog unchanged. Images unchanged.

### B2. Remove section
**Reply:** "Remove the section about maintenance"
**Success:** Section count reduced by 1. Other sections intact. Images unchanged.

### B3. Title change
**Reply:** "Change the title to 'Solar Done Right in Trentham'"
**Success:** Title updates in preview. Slug updates. Body unchanged.

### B4. Make shorter/longer
**Reply:** "Make the intro shorter and punchier"
**Success:** Intro changes. Other sections untouched.

### B5. Repeating header removal
**Reply:** "Remove the header under the title that's repeating the main header"
**Success:** Duplicate H2 that echoes the title is removed.

### B6. Vague edit instruction
**Reply:** "Fix it"
**Success:** Bot asks "I'm not sure what to do with that. You can: edit the text, swap an image, or approve."

### B7. Rapid back-to-back edits
**Reply edit 1:** "Add a line about Fronius inverters"
**Reply edit 2 (immediately after):** "Also mention the 25-year warranty"
**Success:** Both edits apply. Second edit doesn't overwrite first. Reply chain intact.

### B8. Edit after long silence
**Reply to a 10+ minute old preview:** "Make the conclusion stronger"
**Success:** Edit applies. `telegram_message_id` FIND() lookup works on old message.

---

## SECTION C: Image Operations

### C1. Image swap — unspecified
**Reply:** "Swap the image"
**Success:** Bot asks "Which image?" with numbered list (1-4). Sets `pending_action: image_swap`.

### C2. Image swap — answer with number
**Reply to "Which image?":** "2"
**Success:** Hero image swapped. New image different from old. Preview updates.

### C3. Image swap — answer with name
**Reply to "Which image?":** "hero"
**Success:** Same as C2.

### C4. Image swap — specific
**Reply:** "Change the cover image"
**Success:** Cover (index 0) swapped directly. No "Which image?" prompt.

### C5. Image swap — natural language
**Reply:** "That photo's rubbish, use a different one for the top"
**Success:** GPT router understands "top" = hero. Swaps hero image.

### C6. Single photo upload
**Reply with 1 photo + caption:** "Use this as the hero"
**Success:** Photo imported to Wix. Hero slot updated. Preview shows uploaded photo.

### C7. Multi-photo upload (media group)
**Send 3 photos as album replying to draft**
**Success:** All 3 photos imported. GPT maps to slots. Preview shows uploaded photos. Message: "3 photos uploaded (Hero, Body #1, Body #2)."

### C8. Photo upload — no caption
**Send 2 photos as album replying to draft (no text)**
**Success:** Default mapping applied (hero + body #1). Photos import successfully.

### C9. Replace all images
**Reply with 4 photos:** "Replace all images with these"
**Success:** All 4 slots updated. Preview shows all new images.

---

## SECTION D: Approval & Lifecycle

### D1. Approve
**Reply:** "Approve"
**Success:** Status set to "approved". Bot says "Blog approved! Publishing to Wix." (Publish node fires but we're testing the approval path, not the publish.)

### D2. Scrap
**Reply:** "Bin it"
**Success:** Status set to "skipped". Bot says "Blog scrapped."

### D3. Scrap — varied language
**Reply:** "Trash this one" / "Delete it" / "Scrap"
**Success:** All recognized as scrap intent.

### D4. Schedule — future date
**Reply:** "Schedule for next Monday 10am"
**Success:** GPT parses date correctly. Displayed in AEST. Status set to "approved".

### D5. Schedule — relative time
**Reply:** "Schedule in 30 minutes"
**Success:** Date parsed as 30 min from now. Correct AEST display.

### D6. Schedule — vague
**Reply:** "Schedule it for sometime next week"
**Success:** GPT extracts best-guess date. Or asks for clarification.

### D7. Re-approve already published
**Reply "approve" to a published blog**
**Success:** Bot says "This blog is already published. No changes can be made here." (if status is published). If status allows, re-publishes.

### D8. Delete published blog
**Reply:** "Delete this blog"
**Success:** Bot asks "This will permanently remove the blog from the live site. Reply 'yes' to confirm." Then on "yes": deletes via Wix API if `wix_post_id` exists.

### D9. Delete — cancel
**Reply "no" to delete confirmation**
**Success:** "Delete cancelled." Draft unchanged.

---

## SECTION E: Reply Chain Integrity

### E1. Reply to original preview
**Reply to the first BLOG PREVIEW message**
**Success:** Draft found. Action executed.

### E2. Reply to edit confirmation
**Reply to "Edit applied. Preview: ..." message**
**Success:** Draft found (message ID appended to `telegram_message_id`).

### E3. Reply to swap confirmation
**Reply to "Hero swapped. Preview: ..." message**
**Success:** Draft found.

### E4. Reply to "Which image?" prompt
**Reply:** "3"
**Success:** `pending_action: image_swap` detected. Slot 2 (Body #1) swapped.

### E5. Reply to error message
**Reply to "Something went wrong..." message**
**Success:** Draft found (error message ID was tracked). User can retry.

### E6. Reply to very old message (10+ messages ago)
**Success:** FIND() in comma-separated `telegram_message_id` finds it.

---

## SECTION F: Classifier Edge Cases

### F1. Casual / non-content message
**Send (not as reply):** "Hey what's the status of everything?"
**Success:** Bot responds helpfully (Q&A agent or similar). Never ignores a message.

### F2. Reply to bot = always draft reply
**Reply to any bot message:** "2"
**Success:** Treated as draft reply, NOT as not_for_agent. Previous bug: short replies classified as not_for_agent.

### F3. Multi-intent
**Send:** "Approve the blog and also write a new post about heat pump installs"
**Success:** Blog approved AND new social post generated.

### F4. Drive folder reference extraction
**Send:** "Write a blog about the 21 Trentham St install, use those photos"
**Success:** `drive_folder_ref: "21 Trentham St"` extracted. Ack mentions searching Drive.

### F5. Scheduling via classifier
**Send:** "Write a blog about solar battery rebates and schedule it for next Friday"
**Success:** Intent = new_blog_content, urgency = scheduled, target_date extracted.

---

## SECTION G: Preview Site Rendering

### G1. Full blog render
**Open preview URL in Playwright**
**Check:**
- Title renders (40px, Myriad Pro font)
- Hero image present (740×463, top-crop)
- Body text (18px, 27px line-height)
- H2 headings present
- Body images distributed between sections
- SEO preview box (title in blue, URL in green, description)
- Judge score displayed
- "Facts to verify" section if applicable
- No duplicate title heading
- "View All Drafts" link works

### G2. Drafts list page
**Open preview root URL**
**Check:**
- Cards show with cover images (3:4 aspect ratio)
- Titles visible on gradient overlay
- Read time badges
- Click navigates to individual draft

### G3. Mobile responsive
**Resize to 390×844**
**Check:**
- Container collapses gracefully
- Text readable (16px on mobile)
- Images fill width
- No horizontal overflow

### G4. Missing images
**Create a draft with 0 images in tags_ig**
**Check:** Page renders without errors. No broken image icons.

### G5. Corrupted tags_ig
**Manually set tags_ig to "not json"**
**Check:** Page renders. Falls back to empty images.

---

## SECTION H: Image Selection Logic

### H1. Drive category matching
**Generate blog about "battery storage"**
**Check Airtable:** Images sourced from Batteries Drive folder (not Solar).

### H2. Drive folder reference
**Generate blog with `drive_folder_ref: "Solar"`**
**Check:** Images come from Solar folder in Drive.

### H3. Telegram photos + Drive fill
**Send 2 photos + "write a blog about solar"**
**Check:** First 2 images are uploaded photos. Remaining 2 from Drive Solar folder.

### H4. No images in Drive folder
**Reference an empty Drive folder**
**Check:** Falls back to General folder. Blog still generates with images.

### H5. Image usage tracking
**Generate 2 blogs about solar back-to-back**
**Check Airtable:** Second blog uses DIFFERENT images (least-recently-used rotation).

### H6. All images exhausted
**Mark all images as recently used**
**Check:** System still picks images (re-uses oldest). No crash.

---

## SECTION I: Bulk & Special Flows

### I1. Bulk blog plan
**Send:** "Plan 3 blogs for this month"
**Success:** Bot sends a plan with 3 blog topics. Topics are distinct and relevant.

### I2. Approve bulk plan
**Reply:** "Approve all"
**Success:** Blogs start generating one by one. Each preview arrives separately.

### I3. Full rewrite request
**Reply to draft:** "Rewrite the whole thing from scratch"
**Success:** Falls through to full WF3 regeneration (not targeted edit).

---

## SECTION J: Error Handling

### J1. Bot reports errors, never silent
**Trigger any error path (bad file ID, Wix failure, etc.)**
**Check:** User ALWAYS gets a message explaining what went wrong. Never silence.

### J2. No matching draft
**Reply to a message not linked to any draft**
**Check:** "I couldn't find the draft you're replying to. Try replying directly to the latest preview message."

### J3. Partial photo upload failure
**Send 3 photos where 1 has expired/invalid file_id**
**Check:** 2 photos upload successfully. Error noted for the failed one.

### J4. GPT router returns "unclear"
**Reply with something ambiguous:** "hmm maybe"
**Check:** Bot asks for clarification: "I'm not sure what you mean. You can: edit the text, swap an image, or approve."

---

## Pass Criteria
- All A-J sections pass
- No silent failures (every error path sends a message)
- Reply chain works across 10+ messages in a conversation
- Preview site renders correctly on desktop and mobile
- Images are unique within each blog (no duplicates)
- Drive-sourced images import to Wix successfully
- No orphan Wix posts/drafts left after testing
