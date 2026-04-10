# Stress Test Plan — SMA Trentham (Playwright + Telegram Web)

## Overview
End-to-end stress test via Telegram Web (web.telegram.org) using Playwright browser automation. Tests every user-facing feature as Mick would use it — sending messages, replying to bot responses, sending photos, and verifying previews.

## Prerequisites
- Log into Telegram Web as the test user (Kye Walker)
- Navigate to the TrenthamSocials bot chat
- All tests send real messages through Telegram → WF1 → WF2/WF5/WF6

---

## TEST 1: Simple Post Creation
**What:** Send a plain text post request, verify draft is created with preview
**Steps:**
1. Send: "Create a post about our latest 10kW solar install in Woodend with Fronius inverter"
2. Wait for bot response (ack + draft preview)
3. Verify: bot sends preview message with preview URL
4. Fetch preview URL → verify IG + FB + GBP content exists
5. Verify: auto-selected image from Solar folder
**Pass criteria:** Draft created, preview URL works, image from Solar folder, all 3 platforms have content

## TEST 2: Platform Filtering (IG + FB only)
**What:** Request specific platforms, verify GBP is excluded
**Steps:**
1. Send: "Do a post about the crew BBQ for Instagram and Facebook only"
2. Wait for bot response
3. Fetch preview API → verify `gbp: null`
4. Verify: only IG + FB tabs shown, image from Team folder
**Pass criteria:** No GBP content generated, preview shows 2 platforms only

## TEST 3: Edit Caption (Reply to Draft)
**What:** Reply to a draft preview with an edit request
**Steps:**
1. Use draft from TEST 1 or 2
2. Reply to the preview message: "make it shorter and mention the purple van"
3. Wait for bot response with updated preview
4. Fetch preview → verify caption changed
5. Verify: telegram_message_id updated (for chaining)
**Pass criteria:** Caption edited in-place, preview URL same draft ID, TG msg ID updated

## TEST 4: Second Chained Edit
**What:** Reply to the bot's edit response with another edit
**Steps:**
1. Reply to the bot's response from TEST 3: "also add a call to action at the end"
2. Wait for bot response
3. Fetch preview → verify second edit applied
**Pass criteria:** Second edit works, proves chaining is functional

## TEST 5: Remove Platform (Edit)
**What:** Reply to a draft to remove a platform
**Steps:**
1. Create a new post (all 3 platforms)
2. Reply: "remove GBP"
3. Verify: GBP content nulled, preview shows only IG + FB
**Pass criteria:** Platform removed, preview updated

## TEST 6: Carousel (Multiple Photos)
**What:** Send multiple photos with a caption to create a carousel post
**Steps:**
1. Send 3 photos as a media group with caption: "New battery install at the Smith property in Daylesford"
2. Wait for bot response with preview
3. Fetch preview → verify multiple photos in the response
4. Verify: all photos uploaded to Drive, image_url has multiple URLs
**Pass criteria:** 3 photos combined, carousel preview, correct photo order

## TEST 7: Single Photo Post
**What:** Send one photo with caption
**Steps:**
1. Send 1 photo with caption: "Team photo from the Kyneton job today"
2. Wait for bot response
3. Verify: photo uploaded to Drive (Uploads folder), draft has image
**Pass criteria:** Photo appears in preview, uploaded to Drive

## TEST 8: Reply to Non-Draft Message (New Post)
**What:** Reply to a bot message that ISN'T a draft (e.g. the job spotlight prompt)
**Steps:**
1. Wait for or trigger a non-draft bot message (e.g. weekly summary, Q&A response)
2. Reply: "yes create a post about the Daylesford switchboard upgrade"
3. Verify: treated as NEW post (not "draft not found" error)
4. Verify: draft created and preview sent
**Pass criteria:** No error message, new post created successfully

## TEST 9: Conversational Q&A
**What:** Ask the bot a question (not a post request)
**Steps:**
1. Send: "what posts have we done this week?"
2. Wait for bot response
3. Verify: intelligent conversational response (not a draft, not an error)
**Pass criteria:** Bot responds with relevant info, no draft created

## TEST 10: Educational Post Uniqueness
**What:** Request same topic twice, verify different angles
**Steps:**
1. Send: "Educational post about battery storage benefits"
2. Wait for draft
3. Send: "Educational post about battery storage benefits" (same exact text)
4. Wait for draft
5. Compare: opening lines should be DIFFERENT
**Pass criteria:** Two drafts with genuinely different angles/openings

## TEST 11: Image Folder Selection
**What:** Verify the right image folder is selected for different topics
**Steps:**
1. Send: "Post about battery backup during blackouts" → verify Batteries folder image
2. Send: "Post about the team and the purple vans" → verify Team folder image
3. Send: "Post about solar ROI" → verify Solar folder image
4. Check each draft's image_url points to different Drive folders
**Pass criteria:** Each post picks from the correct category folder

## TEST 12: Drive Image Discovery
**What:** Test that WF-ImageSync can find and index images from Drive folders
**Steps:**
1. Trigger WF-ImageSync with folder_name "Solar"
2. Verify: returns available images from the Solar Drive folder
3. Verify: new images indexed in Airtable Image Library
**Pass criteria:** Drive search works, images returned with correct URLs

## TEST 12B: Drive Fuzzy Folder Match
**What:** Test fuzzy matching — user says "batteries" not "Batteries"
**Steps:**
1. Send: "use photos from the batteries folder for a post about backup power"
2. Verify: finds Batteries folder despite lowercase
3. Verify: draft has image from Batteries folder
**Pass criteria:** Fuzzy match works, correct folder found

## TEST 12C: Drive Reference — "grab from Solar folder"
**What:** User explicitly tells the bot to use a Drive folder image
**Steps:**
1. Send: "create a post about solar panels and use an image from the Solar folder in Drive"
2. Verify: classified as drive_reference intent
3. Verify: image pulled from Solar Drive folder
**Pass criteria:** Drive folder referenced, image used in draft

## TEST 12D: Drive Carousel from Folder
**What:** Create a carousel using multiple images from a Drive folder
**Steps:**
1. Send: "create a carousel post about solar installations using 3 photos from the Solar folder"
2. Verify: multiple images selected from Solar folder
3. Verify: preview shows carousel with multiple photos
4. Verify: image_url contains comma-separated Drive URLs
**Pass criteria:** Multiple images from Drive folder combined into carousel

## TEST 12E: Empty Drive Folder Fallback
**What:** Request images from an empty folder, verify fallback to General
**Steps:**
1. Send: "create a post about EV charging" (EV Charging folder is empty)
2. Verify: GPT classifies as EV Charging folder
3. Verify: falls back to General folder for image
4. Verify: draft still created with an image (not broken)
**Pass criteria:** Empty folder handled gracefully, General fallback works

## TEST 12F: Image Non-Repetition
**What:** Create multiple posts from same folder, verify no image repeats
**Steps:**
1. Send: "post about solar panels" → note which image selected
2. Send: "another post about solar installation" → note which image selected
3. Send: "educational post about solar ROI" → note which image selected
4. Verify: all 3 images are DIFFERENT (different Drive file IDs)
5. Verify: each selected image has last_used timestamp set
**Pass criteria:** No duplicate images across 3 posts, LRU ordering works

## TEST 13: Weekly Scheduler
**What:** Trigger the weekly scheduler and verify it creates varied posts
**Steps:**
1. Fire WF6 via webhook
2. Wait for Telegram messages (weekly summary + draft previews)
3. Verify: 3 posts planned with different topics
4. Verify: GPT-generated briefs are unique (not static templates)
5. Verify: topic rotation index advances
**Pass criteria:** 3 varied posts, unique briefs, rotation advances

---

## Execution Order
Run tests in this order to build on each other:
1. TEST 9 (Q&A — warm up, verify basic flow)
2. TEST 1 (Simple post — core functionality)
3. TEST 2 (Platform filtering)
4. TEST 3 + 4 (Edit + chain)
5. TEST 5 (Remove platform)
6. TEST 8 (Reply to non-draft)
7. TEST 7 (Single photo)
8. TEST 6 (Carousel — multiple Telegram photos)
9. TEST 10 (Uniqueness — same brief, different output)
10. TEST 11 (Image folder classification)
11. TEST 12 (Drive discovery)
12. TEST 12B (Drive fuzzy match)
13. TEST 12C (Drive reference from Telegram)
14. TEST 12D (Drive carousel from folder)
15. TEST 12E (Empty folder fallback)
16. TEST 12F (Image non-repetition)
17. TEST 13 (Weekly scheduler)

## Verification Method
After each test message:
1. Wait for bot response in Telegram (visual confirmation)
2. Check n8n execution via API (no errors)
3. Check Airtable draft record (correct fields)
4. Fetch preview URL (content renders correctly)

## Known Limitations
- Carousel test requires real photos (can't fake Telegram media groups via web)
- Drive discovery test uses webhook, not Telegram
- Scheduler test uses webhook trigger, not cron
