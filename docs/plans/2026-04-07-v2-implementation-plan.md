# V2 Social Media Agent — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild the Trentham social media agent as a single AI Agent workflow with multi-client Airtable config, replacing 7 fragile v1 workflows.

**Architecture:** One main n8n workflow with AI Agent node (Tools Agent, gpt-5.4-mini, Buffer Window Memory 15). Sub-workflows called as tools for heavy content generation (social, blog) and publishing. All config from Airtable per-client row. New Telegram bot, new Airtable base — v1 untouched.

**Tech Stack:** n8n cloud, Airtable API, OpenAI (gpt-5.4-mini), Telegram Bot API, Google Drive API (via n8n node), Buffer GraphQL API, Wix REST API, Vercel (preview apps)

**Design Doc:** `docs/plans/2026-04-07-v2-rebuild-design.md`

**V2 Bot Token:** 8684524385:AAFHYQiMG_XE0VkhBSAt8wsok4wSceYyO68 (@TrenthamSocialsV2bot)

**V1 stays untouched.** Different bot, different Airtable base, different workflow IDs.

---

## Phase 1: Foundation (Airtable + Main Workflow Shell)

### Task 1: Create V2 Airtable Base + Tables

**What:** Create the new Airtable base with all 5 tables and populate the Trentham config row.

**Steps:**

1. Create new Airtable base named "SMA V2"
2. Create table: **V2 Config** with fields:
   - client_name (Text)
   - active (Checkbox)
   - telegram_chat_id (Text)
   - telegram_bot_token (Text)
   - buffer_api_key (Text)
   - buffer_ig_channel (Text)
   - buffer_fb_channel (Text)
   - buffer_gbp_channel (Text)
   - wix_api_key (Text)
   - wix_site_id (Text)
   - wix_member_id (Text)
   - openai_api_key (Text)
   - google_drive_folder_id (Text)
   - brand_voice (Long text)
   - preview_base_url (URL)
   - blog_preview_base_url (URL)
   - posts_per_week (Number)
   - post_time (Text)
   - topic_rotation (Text)
   - last_topic_index (Number)
   - crisis_pause (Checkbox)
3. Create table: **V2 Drafts** with fields per design doc Section 5
4. Create table: **V2 Post History** with fields per design doc Section 5
5. Create table: **V2 Example Bank** with fields: client_id (Link), content (Long text), post_type (Single select: job_spotlight/educational/team_brand/product_spotlight/community/seasonal)
6. Create table: **V2 Used Images** with fields: client_id (Link), drive_file_id (Text), used_date (DateTime), draft_id (Link), usage_type (Single select: social/blog_cover/blog_hero/blog_body)
7. Populate V2 Config row for Trentham with all existing keys/IDs from v1 Master Config
8. Copy 30+ Example Bank entries from v1 (set client_id to Trentham row)

**Verify:** Query each table via Airtable API, confirm fields exist and Trentham config row returns all values.

**Commit:** Save table IDs to `scripts/v2/airtable_ids.json`

---

### Task 2: Create Main V2 Workflow Shell

**What:** Create the n8n workflow with Telegram trigger, config loader, and placeholder AI Agent node. No tools yet — just verify the trigger fires and config loads.

**Files:**
- Create: `scripts/v2/create_main_workflow.py`

**Steps:**

1. Create n8n workflow "SMA-V2 Agent" via API with nodes:
   - **V2 Telegram Trigger** (telegramTrigger, V2 bot token credential)
   - **V2 Test Webhook** (webhook, path: `sma-v2-agent`)
   - **V2 Load Config** (code node: query V2 Config by `$json.message.chat.id`, return config object)
   - **V2 Agent** (AI Agent placeholder — just echoes "V2 agent received: {message_text}")
2. Wire: Both triggers → V2 Load Config → V2 Agent
3. Activate workflow
4. Fire test via webhook: `{"message": {"text": "hello", "chat": {"id": "8541854415"}, "message_id": 1}}`
5. Verify: execution succeeds, config loaded, Trentham row returned

**Verify:** Check n8n execution API — V2 Load Config output has all Trentham config fields.

---

### Task 3: Add Photo Collector (Media Group Handling)

**What:** Add the 3-node photo collection chain between triggers and agent. Handles carousel (multiple photos sent as media group).

**Files:**
- Create: `scripts/v2/v2_extract_metadata.js`
- Create: `scripts/v2/v2_collect_photos.js`

**Steps:**

1. Create **V2 Extract Metadata** code node:
   - Parse Telegram message JSON (text, caption, photo array, media_group_id, reply context)
   - Store secondary photos (no caption) to V2 temp storage or in-memory
   - Return: message_text, photo_file_ids, media_group_id, is_reply, reply_to_message_id, chat_id, message_id
   - If secondary photo in media group: return `{skip: true}`
2. Create **V2 Is Not Skip?** IF node: check `message_text !== ""`
3. Create **V2 Has Media Group?** IF node: check `needs_photo_collect === true`
4. Create **V2 Wait 5s** wait node
5. Create **V2 Collect Photos** code node: query temp storage for all photos with same media_group_id, combine file_ids, sort by message_id, clean up
6. Wire: Triggers → V2 Extract Metadata → V2 Is Not Skip? → V2 Has Media Group?
   - Media group true: → Wait 5s → Collect Photos → V2 Load Config → V2 Agent
   - Media group false: → V2 Load Config → V2 Agent

**Verify:** Fire webhook with single photo, verify it passes through. Fire 3 messages with same media_group_id, verify Collect Photos combines all 3.

---

### Task 4: Configure AI Agent Node with Memory

**What:** Replace the placeholder agent with a real Tools Agent node connected to OpenAI and Buffer Window Memory.

**Steps:**

1. Replace V2 Agent placeholder with `n8n-nodes-langchain.agent` (Tools Agent type)
2. Connect OpenAI Chat Model sub-node (gpt-5.4-mini, credential from V2 Config)
3. Connect Buffer Window Memory sub-node (context length: 15, session key: `={{ $json.chat_id }}`)
4. Set system prompt from design doc Section 3 (with `{client_name}`, `{brand_voice}` placeholders filled from V2 Load Config)
5. Add **V2 Send Telegram** tool (Custom Code Tool):
   - Sends message to Telegram via bot API
   - Input: text, reply_to_message_id (optional)
   - Uses config.telegram_bot_token and config.telegram_chat_id

**Verify:** Send "hello, what can you do?" via webhook. Agent should respond intelligently via Telegram using the send_telegram tool. Check memory works: send "my name is Leo", then "what's my name?" — agent should remember.

---

## Phase 2: Social Post Creation

### Task 5: Build V2-Social-Generator Sub-Workflow

**What:** Create the sub-workflow that generates social post content (IG + FB + GBP) with examples, judge, and preview.

**Files:**
- Create: `scripts/v2/v2_social_generator.js` (main generation logic)
- Create: `scripts/v2/v2_social_judge.js` (quality judge)
- Create: `scripts/v2/v2_social_preview.js` (Telegram preview message)

**Steps:**

1. Create n8n workflow "SMA-V2 Social Generator" with:
   - **Trigger**: executeWorkflowTrigger (called as tool)
   - **Fetch Examples**: Code node — query V2 Example Bank (random 30, matching client_id)
   - **Fetch Recent Posts**: Code node — query V2 Drafts (last 20 IG captions for anti-repetition)
   - **Smart Image Select**: Code node — GPT classifies brief → folder → search Drive → LRU pick → stamp V2 Used Images
   - **Build Prompt**: Code node — assemble examples + recent posts + brief into user message
   - **Generate Content**: OpenAI node (gpt-5.4-mini, temp 0.7, max 2000 tokens)
   - **Parse Output**: Code node — extract IG/FB/GBP, respect platform filter, null unwanted platforms
   - **Judge**: OpenAI node (gpt-5.4-mini, temp 0.2) — score voice_match, relevance, clarity, engagement, formatting
   - **Pass/Fail**: IF node — avg >= 3.0 passes, else retry (up to 3)
   - **Save Draft**: Airtable create in V2 Drafts
   - **Send Preview**: Code node — send Telegram message with preview URL, store telegram_message_id
2. Return to calling agent: draft_id, preview_url, score

**Verify:** Call sub-workflow with brief "10kW solar install in Woodend, Fronius inverter". Check: draft created in V2 Drafts, preview URL works, image from Solar folder, IG/FB/GBP content exists, score > 3.0.

---

### Task 6: Add create_social_post Tool to Agent

**What:** Connect the V2-Social-Generator as a Call n8n Workflow Tool on the AI Agent.

**Steps:**

1. Add "Call n8n Workflow Tool" sub-node to V2 Agent
2. Name: "create_social_post"
3. Description: "Create a social media post for Instagram, Facebook, and Google Business Profile. Use when the user asks to create, write, or make a social post. Input: brief (the user's description), platforms (array of platforms to include, default all), photo_file_ids (comma-separated Telegram file IDs if user sent photos)"
4. Point to V2-Social-Generator workflow ID
5. Pass inputs: brief, platforms, photo_file_ids, image_url, client_config (full config object from V2 Load Config)

**Verify:** Send via Telegram: "Create a post about our latest solar install in Daylesford". Agent should:
1. Send ack ("On it...")
2. Call create_social_post tool
3. Draft appears in V2 Drafts
4. Preview message sent to Telegram with link

Then test platform filtering: "Do a post about the crew BBQ for IG and FB only" — verify no GBP content.

---

### Task 7: Add Photo Archive Branch

**What:** Parallel branch that downloads Telegram photos, uploads to Drive, shares publicly, and updates draft with permanent URLs.

**Files:**
- Create: `scripts/v2/v2_download_photos.js`
- Create: `scripts/v2/v2_update_draft_image.js`

**Steps:**

1. Add **V2 Has Photo?** IF node after V2 Extract Metadata (parallel to agent path)
2. Add **V2 Download Photos** code node: iterate all photo_file_ids, download each from Telegram API, return binary
3. Add **V2 Upload to Drive** Google Drive node: upload to client's `google_drive_folder_id` + "/Uploads" subfolder
4. Add **V2 Share File** Google Drive node: share with anyone (reader)
5. Add **V2 Update Draft Image URL** code node: find draft by photo_file_id match, set image_url to `lh3.googleusercontent.com/d/{driveFileId}`

**Verify:** Send photo via Telegram with caption. Check: photo uploaded to Drive Uploads folder, draft has permanent image_url, preview shows the photo.

---

## Phase 3: Draft Editing & Q&A

### Task 8: Add edit_draft Tool

**What:** Agent tool for targeted edits when user replies to a draft preview.

**Files:**
- Create: `scripts/v2/v2_edit_draft.js`

**Steps:**

1. Add "Custom Code Tool" to V2 Agent
2. Name: "edit_draft"
3. Description: "Edit an existing draft post. Use when the user replies to a draft preview asking for changes. Supports: caption edits, platform removal, image swap, full redraft. Input: draft_id or telegram_message_id (to find the draft), edit_instruction (what to change)"
4. Implementation:
   - Look up draft by telegram_message_id in V2 Drafts
   - Determine type (social vs blog)
   - For social: GPT edit IG caption, replicate to FB (strip hashtags) + GBP (consultative)
   - For remove_platform: null the content field
   - For image_swap: search Drive → pick new LRU image → update draft
   - For full_redraft: return flag for agent to call create_social_post again
   - Update V2 Drafts record
   - Send updated preview to Telegram (update telegram_message_id for chaining)
5. Return: action_taken, updated draft_id

**Verify:** Create a post, then reply "make it shorter". Check: caption changed, preview updated. Reply again "remove GBP" — check GBP nulled. Reply again "also add a CTA" — check chaining works (3rd edit on same draft).

---

### Task 9: Add lookup_drafts and Q&A Capability

**What:** Agent tool to query drafts, plus the agent's built-in conversational ability for Q&A.

**Steps:**

1. Add "HTTP Request Tool" to V2 Agent
2. Name: "lookup_drafts"
3. Description: "Look up pending or published drafts. Use when the user asks about their posts, what's pending, what's been published. Input: filter (e.g. 'pending', 'published', or a specific draft ID)"
4. URL: `https://api.airtable.com/v0/{baseId}/{draftsTableId}`
5. Headers: Authorization from config
6. Query params: filterByFormula from $fromAI("filter")

**Verify:** Send "what posts are pending?" — agent should call lookup_drafts and respond with draft summaries. Send "what did we publish this week?" — agent responds with post history.

No separate Q&A workflow needed — the agent handles conversational responses natively with its system prompt + memory.

---

## Phase 4: Drive Integration

### Task 10: Add search_drive_folder Tool

**What:** Agent tool to search Google Drive folders by name and list available images.

**Files:**
- Create: `scripts/v2/v2_search_drive.js`

**Steps:**

1. Add "Custom Code Tool" to V2 Agent  
2. Name: "search_drive_folder"
3. Description: "Search Google Drive for a folder by name and list the images inside it. Use when the user says 'use photos from the Jones job' or 'grab images from the Solar folder'. Input: folder_name (the name to search for, fuzzy matching supported)"
4. Implementation:
   - Use n8n Google Drive fileFolder search (via sub-workflow with native Drive node, since Code nodes can't use Drive OAuth)
   - Actually: create a tiny **V2-Drive-Search** sub-workflow with 2 Drive nodes (search folder + search images in folder)
   - Call it via executeWorkflow from the tool
   - Cross-reference results with V2 Used Images
   - Return: folder_name, images[] with url, name, used_before flag
5. Wire as Call n8n Workflow Tool pointing to V2-Drive-Search

**Verify:** Send "use photos from the Solar folder for a post about panels". Agent should:
1. Call search_drive_folder("Solar")
2. Get list of images
3. Call create_social_post with selected image URLs
4. Draft created with Drive image

Then test fuzzy: "grab a photo from batteries" (lowercase) — should match "Batteries" folder.

---

## Phase 5: Blog Pipeline

### Task 11: Build V2-Blog-Generator Sub-Workflow

**What:** Sub-workflow for blog content generation with SEO validation, judging, 4-image selection, and Wix-format preview.

**Files:**
- Create: `scripts/v2/v2_blog_generator.js`
- Create: `scripts/v2/v2_seo_validation.js`
- Create: `scripts/v2/v2_blog_images.js`
- Create: `scripts/v2/v2_blog_preview.js`

**Steps:**

1. Create n8n workflow "SMA-V2 Blog Generator" with:
   - **Trigger**: executeWorkflowTrigger
   - **Fetch Context**: Code node — brand guide from V2 Config, last 3 blogs from V2 Drafts, examples from V2 Example Bank
   - **Blog Agent**: OpenAI node — generate blog (title, body, slug, meta, keyword, content_type)
   - **SEO Validation**: Code node — keyword density, meta length, H2 count, internal links, auto-fix stuffing
   - **Blog Judge**: OpenAI node — voice_match, local_specificity, technical_accuracy, engagement, structural_freshness
   - **Pass/Fail**: IF node — retry if < 3.0 (up to 3)
   - **Select 4 Images**: Code node — search Drive by topic, LRU, portrait for cover, landscape for rest
   - **Save Draft**: Airtable create (type=blog, content_blog JSON, blog_images JSON)
   - **Send Preview**: Code node — Vercel preview link + metadata to Telegram
2. Return: draft_id, preview_url, score, facts_to_verify

**Verify:** Send "Write a blog about home battery storage for Macedon Ranges homeowners". Check: blog draft in V2 Drafts, 4 images selected, preview renders on Vercel, SEO validation passed, score > 3.0.

---

### Task 12: Add create_blog_post Tool to Agent

**Steps:**

1. Add Call n8n Workflow Tool to V2 Agent
2. Name: "create_blog_post"
3. Description: "Create a blog post for the Wix website. Use when user asks to write a blog, article, or long-form content. Input: topic (the blog subject), photo_file_ids (if user sent photos)"
4. Point to V2-Blog-Generator workflow ID

**Verify:** Send "write a blog about EV charger installation for rural properties". Agent calls create_blog_post, blog draft created, preview sent.

---

## Phase 6: Publishing

### Task 13: Build V2-Publisher Sub-Workflow

**What:** Handles publishing approved drafts to Buffer (social) and Wix (blog).

**Files:**
- Create: `scripts/v2/v2_publisher.js`
- Create: `scripts/v2/v2_wix_publish.js`

**Steps:**

1. Create n8n workflow "SMA-V2 Publisher" with:
   - **Trigger**: executeWorkflowTrigger
   - **Fetch Draft**: Airtable get record from V2 Drafts
   - **Route Type**: IF node — social vs blog
   - **Social path**:
     - Buffer GraphQL publish to IG (if content_ig exists)
     - Buffer GraphQL publish to FB (if content_fb exists)
     - Buffer GBP publish (if content_gbp exists)
     - Log each to V2 Post History
     - Mark image as used in V2 Used Images
   - **Blog path**:
     - Convert markdown → Wix Ricos format
     - POST draft to Wix API
     - PATCH cover image
     - Publish or schedule
     - Store wix_post_id
     - Log to V2 Post History
   - **Update status**: PATCH V2 Drafts status → "published"
   - **Confirm**: Send Telegram confirmation

**Verify:** Create and approve a social post — verify it appears in Buffer queue (saveToDraft: true). Create and approve a blog — verify Wix draft created.

---

### Task 14: Add publish_post Tool to Agent

**Steps:**

1. Add Call n8n Workflow Tool to V2 Agent
2. Name: "publish_post"
3. Description: "Publish an approved draft to social media (Buffer) or Wix blog. Use when user says 'approve', 'publish', 'go ahead', 'looks good'. Input: draft_id (the draft to publish), scheduled_date (optional ISO date for scheduling)"
4. Point to V2-Publisher workflow ID

**Verify:** Send "Create a post about solar panels". Get preview. Reply "approve". Agent calls publish_post, draft status → published, Buffer queue has the post, Telegram confirms.

---

## Phase 7: Scheduler

### Task 15: Add Weekly Schedule Trigger + plan_weekly_posts Tool

**Steps:**

1. Add Schedule Trigger node to main workflow (cron: `0 4 * * 1` = Monday 2pm AEST)
2. Wire: Schedule Trigger → V2 Load Config (use default client for cron) → V2 Agent with special input "SYSTEM: Weekly schedule triggered. Plan this week's posts."
3. Add "Custom Code Tool" to V2 Agent:
   - Name: "plan_weekly_posts"
   - Description: "Plan and generate this week's scheduled posts. Reads config for posts_per_week, topic_rotation, etc. Use when the schedule trigger fires OR when user says 'plan this week' or 'schedule posts'."
   - Implementation:
     - Read V2 Config: posts_per_week, topic_rotation, last_topic_index
     - Check crisis_pause
     - Plan N posts across Mon/Wed/Fri
     - Generate unique GPT briefs per topic (fetch recent for anti-repetition)
     - For each autonomous: call create_social_post tool
     - For job_spotlights: send prompt to Telegram
     - Update last_topic_index
     - Send weekly summary

**Verify:** Fire schedule via webhook. Check: 3 posts planned, drafts created, summary sent to Telegram, topic index advances. Then send "plan this week's posts" via Telegram — same result.

---

## Phase 8: Preview Apps

### Task 16: Deploy V2 Social Preview App

**What:** New Vercel app for social post previews (IG/FB/GBP mockups).

**Files:**
- Create: `v2-preview-app/api/draft.js`
- Create: `v2-preview-app/index.html`
- Create: `v2-preview-app/vercel.json`

**Steps:**

1. Copy preview-app to v2-preview-app
2. Update API to read from V2 Airtable base + V2 Drafts table
3. Update env vars for new Airtable PAT
4. Deploy to Vercel as `v2-preview-social`
5. Update V2 Config preview_base_url to new Vercel URL

**Verify:** Create a draft, open preview URL — renders correctly with IG/FB/GBP tabs.

---

### Task 17: Deploy V2 Blog Preview App

**What:** New Vercel app for blog previews.

**Files:**
- Create: `v2-preview-site/server.js` (copy + update)
- Create: `v2-preview-site/vercel.json`

**Steps:**

1. Copy preview-site to v2-preview-site
2. Update to read from V2 Airtable base
3. Deploy to Vercel as `v2-preview-blog`
4. Update V2 Config blog_preview_base_url

**Verify:** Create a blog draft, open preview URL — renders with Wix fonts, images, SEO metadata.

---

## Phase 9: Integration Testing

### Task 18: End-to-End Stress Test via Playwright

**What:** Run the full stress test plan from `docs/stress-test-plan.md` against V2.

**Steps:**

1. Open Telegram Web, navigate to @TrenthamSocialsV2bot
2. Run all 17 tests from the stress test plan
3. For each test: verify Telegram response + n8n execution + Airtable record + preview URL
4. Log results: PASS/FAIL per test with notes
5. Fix any failures found

**Pass criteria:** All 17 tests pass. No routing bugs, no duplicate nodes, no broken previews.

---

## Phase 10: Cleanup & Documentation

### Task 19: Populate Example Bank from V1

**What:** Copy the 30+ real Trentham posts into V2 Example Bank with proper client_id linking.

---

### Task 20: Update CLAUDE.md for V2

**What:** Add V2-specific instructions, workflow IDs, table IDs, and the new architecture notes.

---

## Summary

| Phase | Tasks | What it delivers |
|-------|-------|-----------------|
| 1: Foundation | 1-4 | Airtable base, main workflow, photo collector, agent with memory |
| 2: Social Posts | 5-7 | Create posts, auto-images, photo archive |
| 3: Editing & Q&A | 8-9 | Edit drafts via reply, conversational Q&A |
| 4: Drive | 10 | Fuzzy folder search, carousel from Drive |
| 5: Blog | 11-12 | Blog generation with SEO, images, preview |
| 6: Publishing | 13-14 | Buffer + Wix publishing |
| 7: Scheduler | 15 | Weekly auto-posts |
| 8: Previews | 16-17 | Vercel preview apps |
| 9: Testing | 18 | Full stress test |
| 10: Cleanup | 19-20 | Examples, docs |

**Estimated total: 20 tasks across 10 phases.**
