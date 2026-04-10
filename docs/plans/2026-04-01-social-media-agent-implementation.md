# Social Media Agent - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Social Media & Marketing Agent for Trentham Electrical & Solar that automates content creation, approval, and publishing across Facebook, Instagram, Google Business Profile, and Wix blog via Telegram.

**Architecture:** n8n workflows orchestrate the agent. Claude API handles all AI reasoning (message classification, content generation, approval parsing). Airtable stores all config, state, and history. Telegram is the sole user interface. Publishing goes through Buffer (FB/IG), GBP API, and Wix Blog API.

**Tech Stack:** n8n (self-hosted), Claude API (Anthropic), Airtable, Telegram Bot API, Buffer API, Google Business Profile API, Google Drive API, Wix Blog API

**Design doc:** `docs/plans/2026-04-01-social-media-agent-design.md`

---

## Dependency Map

```
Task 1 (Scrape content) ─────────────────────┐
Task 2 (Airtable schema) ──── no dependency   │
Task 3 (Telegram trigger) ──── no dependency   ├── Task 5 (Brand guides) ── Task 6 (Prompts) ── Task 7+ (all remaining)
Task 4 (Draft prompts) ──────────────────────┘
```

Tasks 1-4 can run in parallel. Task 5 requires Task 1 + Claude API key. Task 6 requires Task 5. Everything after requires Task 6.

---

## Phase 1: Brand Intelligence

### Task 1: Scrape All Existing Content

**No blockers. Can start immediately.**

**Files:**
- Create: `data/scraped/instagram.json`
- Create: `data/scraped/facebook.json`
- Create: `data/scraped/gbp.json`
- Create: `data/scraped/wix-blog.json`

**Step 1: Find Mick's social media URLs**

Search for "Trentham Electrical & Solar" across:
- Instagram (business page)
- Facebook (business page)
- Google Business Profile (search Google Maps)
- Wix website/blog

Record all URLs.

**Step 2: Scrape Instagram**

Use Firecrawl or similar to scrape all posts from the Instagram business page. For each post capture:
- Caption text
- Hashtags (extracted separately)
- Post date
- Post type (image, carousel, reel)
- Engagement (likes, comments if visible)

Save to `data/scraped/instagram.json` as an array of objects, ordered newest first.

**Step 3: Scrape Facebook**

Scrape all posts from the Facebook business page. For each post capture:
- Post text
- Post date
- Post type (photo, link, text, video)
- Engagement if visible

Save to `data/scraped/facebook.json`.

**Step 4: Scrape Google Business Profile**

Scrape all GBP posts visible in Google Search or Maps for the business. For each post capture:
- Post text
- Post date
- Post type (update, offer, event)
- CTA button text if present

Save to `data/scraped/gbp.json`. Note: there may be very few or no GBP posts.

**Step 5: Scrape Wix Blog**

Scrape all published blog posts from the Wix site. For each post capture:
- Title
- Full body text (preserving heading structure H1/H2/H3)
- Meta description
- Publication date
- URL slug
- Categories/tags if present
- Featured image description

Save to `data/scraped/wix-blog.json`. Note: there may be very few or no blog posts.

**Step 6: Verify scrape completeness**

Review each JSON file. Confirm post counts match what's visible on each platform. Flag any gaps.

---

### Task 2: Set Up Airtable Schema

**No blockers. Can start immediately.**

**Step 1: Create the Airtable base**

In Mick's Airtable account (using the existing credential in n8n), create a new base called "Social Media Agent".

**Step 2: Create Master Config table**

Create the table with these fields:

| Field Name | Field Type | Default Value |
|------------|-----------|---------------|
| config_key | Single line text | |
| config_value | Long text | |

Add the following rows:
- google_drive_folder_id (leave empty - populated later)
- post_frequency: "2"
- post_days: "Tuesday, Friday"
- post_time: "09:00"
- filler_topics: "Battery benefits, blackouts, EV charging, solar ROI, energy savings, VEU program"
- last_filler_topic: (leave empty)
- buffer_profile_ids: (leave empty - populated later)
- gbp_location_id: (leave empty - populated later)
- wix_site_id: (leave empty - populated later)
- telegram_group_id: (leave empty - populated later)
- brand_voice_master: (leave empty - populated after Phase 1)
- brand_voice_social: (leave empty - populated after Phase 1)
- brand_voice_gbp: (leave empty - populated after Phase 1)
- brand_voice_blog: (leave empty - populated after Phase 1)

**Step 3: Create Pending Drafts table**

| Field Name | Field Type |
|------------|-----------|
| draft_id | Autonumber |
| telegram_message_id | Single line text |
| trigger_type | Single select (telegram / drive / autonomous) |
| platforms_requested | Multiple select (fb_ig / gbp / blog) |
| status_fb_ig | Single select (pending / approved / redrafting / skipped / published) |
| status_gbp | Single select (pending / approved / redrafting / skipped / published) |
| status_blog | Single select (pending / approved / redrafting / skipped / published) |
| content_fb_ig | Long text |
| content_gbp | Long text |
| content_blog | Long text |
| image_url | URL |
| revision_count | Number (default 0) |
| created_at | Created time |
| published_at | Date |

**Step 4: Create Conversation Messages table**

| Field Name | Field Type |
|------------|-----------|
| message_id | Autonumber |
| draft_id | Link to Pending Drafts |
| telegram_message_id | Single line text |
| sender | Single select (user / agent) |
| message_text | Long text |
| timestamp | Created time |

**Step 5: Create Post History table**

| Field Name | Field Type |
|------------|-----------|
| post_id | Autonumber |
| draft_id | Link to Pending Drafts |
| platform | Single select (fb / ig / gbp / blog) |
| content | Long text |
| image_id | Link to Image Library |
| topic | Single line text |
| published_at | Date |
| platform_url | URL |

**Step 6: Create Image Library table**

| Field Name | Field Type |
|------------|-----------|
| image_id | Autonumber |
| google_drive_file_id | Single line text |
| google_drive_url | URL |
| folder | Single select (Solar / Air Conditioning / Electrical / EV Charging / Batteries / Team / General) |
| description | Long text |
| uploaded_at | Created time |
| source | Single select (telegram_upload / manual / pre-existing) |
| used_in_fb | Date |
| used_in_ig | Date |
| used_in_gbp | Date |
| used_in_blog | Date |

**Step 7: Verify all tables**

Open each table, confirm field types and linked records are correct. Test creating and deleting a dummy row in each.

---

### Task 3: Set Up Telegram Trigger Workflow

**No blockers. Can start immediately.**

**Step 1: Create a new n8n workflow**

In Mick's n8n instance (trentham.app.n8n.cloud), create a new workflow called "Social Media Agent - Telegram Trigger".

**Step 2: Add Telegram Trigger node**

- Add a Telegram Trigger node
- Use the existing Telegram API credential
- Set trigger on: "message" (catches text, photos, files, and replies)
- Set updates: ["message"]

**Step 3: Add a debug response**

Add a Telegram Send Message node after the trigger:
- Chat ID: `{{ $json.message.chat.id }}`
- Text: `Received: {{ $json.message.text || '[photo/file]' }}`

This confirms the round-trip works.

**Step 4: Test the trigger**

- Activate the workflow
- Send a text message to the Telegram group
- Confirm n8n receives it and sends the echo back
- Send a photo with a caption
- Confirm n8n receives both the photo and caption text
- Reply to the bot's message
- Confirm n8n receives the reply and the `reply_to_message` field is populated

**Step 5: Document the Telegram payload structure**

Save the raw JSON payloads from each test (text message, photo, reply) to `data/telegram-payload-samples.json` for reference when building later workflows.

**Step 6: Record the Telegram group chat ID**

From the test payload, extract the `chat.id` value and add it to the Airtable Master Config table as the `telegram_group_id` value.

---

### Task 4: Draft All Claude Prompts

**No blockers. Can start immediately. Cannot test until Claude API key arrives.**

**Files:**
- Create: `prompts/brand-guide-generator.md`
- Create: `prompts/message-classifier.md`
- Create: `prompts/content-generator.md`
- Create: `prompts/approval-parser.md`

**Step 1: Write the brand guide generator prompt**

File: `prompts/brand-guide-generator.md`

This prompt takes all scraped content as input and produces brand style guides. It should:
- Accept a JSON dump of all scraped posts across all platforms
- Weight recent posts higher (last 6 months = high weight, 6-12 months = medium, older = low)
- Output four separate guides: Master, Social (FB/IG), GBP, Blog
- For each guide, analyse the patterns listed in the design doc (voice, vocabulary, structure, etc.)
- Include specific examples from actual posts to ground each observation
- Note any inconsistencies across platforms

**Step 2: Write the message classifier prompt**

File: `prompts/message-classifier.md`

This prompt classifies incoming Telegram messages. It should:
- Accept the message text (and image flag if photo attached)
- Return a JSON object: `{ "classification": "content_request" | "agent_question" | "not_for_agent", "platforms": ["fb_ig", "gbp", "blog"] | null, "content_type": "job_spotlight" | "educational" | "promotional" | null, "details": "extracted subject matter" }`
- Default platforms to all if not specified
- Include examples of each classification type in the prompt
- Be confident but ask for clarification if genuinely ambiguous

Note: "draft_reply" classification is handled at the n8n level (checking `reply_to_message`) before this prompt is called.

**Step 3: Write the content generator prompt**

File: `prompts/content-generator.md`

This is the main content generation prompt. It should:
- Accept: message text, image (via vision), platform list, content type, brand guides (master + relevant platform guides), last 20-30 posts from Post History
- Generate content for each requested platform in the correct format
- Return structured JSON:
```json
{
  "fb_ig": { "caption": "...", "hashtags": "..." },
  "gbp": { "text": "...", "cta_button": "CALL_NOW | LEARN_MORE | BOOK" },
  "blog": { "title": "...", "meta_description": "...", "slug": "...", "body": "...", "content_type": "full_article | job_spotlight" }
}
```
- Only include keys for requested platforms
- Follow each platform's specific guide for length, tone, structure
- Never repeat topics, angles, or phrasing from recent Post History
- Never fabricate details not present in the input - ask if needed
- Include the image description from vision in the content where relevant

**Step 4: Write the approval parser prompt**

File: `prompts/approval-parser.md`

This prompt interprets Mick's replies to draft posts. It should:
- Accept: Mick's reply text, current draft state (which platforms, their content), conversation history
- Return structured JSON:
```json
{
  "actions": {
    "fb_ig": "approve" | "redraft" | "skip",
    "gbp": "approve" | "redraft" | "skip",
    "blog": "approve" | "redraft" | "skip"
  },
  "redraft_instructions": {
    "fb_ig": "make it shorter",
    "gbp": null,
    "blog": "add section about VEU rebate"
  },
  "agent_response": "Optional natural language response to Mick"
}
```
- Only include keys for platforms that are currently in play
- Handle partial approvals ("approve all except the blog")
- Handle per-platform feedback ("IG is good, rewrite the GBP one")
- Handle general feedback applied to all ("make it more casual" = redraft all)
- If unclear, set agent_response to a clarifying question

**Step 5: Review all four prompts**

Read through each prompt file. Verify they're consistent with each other and with the design doc. Check that the JSON structures are compatible (content generator output feeds into approval parser input).

---

## Phase 1b-1c: Brand Guides (Blocked by Claude API Key)

### Task 5: Generate Brand Style Guides

**Blocked by: Claude API key from Mick**

**Files:**
- Read: `data/scraped/*.json` (from Task 1)
- Read: `prompts/brand-guide-generator.md` (from Task 4)
- Create: `brand-guides/master.md`
- Create: `brand-guides/social-fb-ig.md`
- Create: `brand-guides/gbp.md`
- Create: `brand-guides/blog.md`

**Step 1: Prepare the scraped data**

Combine all four scraped JSON files into a single input. Add a `recency_weight` field to each post based on date:
- Last 6 months: "high"
- 6-12 months: "medium"
- Older than 12 months: "low"

**Step 2: Run the brand guide generator**

Send the combined data + the brand-guide-generator prompt to Claude API. Use a large context model to fit all content.

**Step 3: Save the four guides**

Save each guide to its own file in `brand-guides/`. These are working drafts.

**Step 4: Human review - Master guide**

Review `brand-guides/master.md`. Check:
- Does the voice description sound like Mick?
- Are the vocabulary examples accurate?
- Are there observations that feel wrong or forced?

Iterate with Claude until it's right.

**Step 5: Human review - Social guide**

Review `brand-guides/social-fb-ig.md`. Check:
- Do the caption length observations match his actual posts?
- Is the hashtag strategy accurate?
- Does the post structure analysis hold up?

Iterate until right.

**Step 6: Human review - GBP guide**

Review `brand-guides/gbp.md`. Note: if there are very few or no existing GBP posts, this guide will need to be constructed from the master guide + GBP best practices rather than scraped data. That's fine - flag it.

**Step 7: Human review - Blog guide**

Review `brand-guides/blog.md`. Same caveat as GBP - if few blog posts exist, construct from master guide + SEO best practices.

**Step 8: Upload guides to Airtable**

Copy the final approved text of each guide into the corresponding Airtable Master Config fields:
- brand_voice_master
- brand_voice_social
- brand_voice_gbp
- brand_voice_blog

---

## Phase 2: Core Loop

### Task 6: Wire Up Content Generation in n8n

**Blocked by: Task 5 (brand guides in Airtable) + Claude API key**

**Step 1: Add Claude API credential to n8n**

Add a new Header Auth credential in n8n:
- Name: "Claude API"
- Header Name: `x-api-key`
- Header Value: (Mick's Claude API key)

**Step 2: Build the classification sub-workflow**

Create a new n8n workflow: "Social Media Agent - Message Classifier"

Nodes:
1. **Webhook** (input) - receives message data from the main trigger workflow
2. **IF** node - check if `reply_to_message` exists
   - Yes -> return `{ "classification": "draft_reply", "original_message_id": reply_to_message.message_id }`
   - No -> continue to Claude
3. **Airtable** node - fetch Master Config (brand guides for system prompt context)
4. **HTTP Request** node - call Claude API
   - URL: `https://api.anthropic.com/v1/messages`
   - Method: POST
   - Headers: x-api-key (from credential), anthropic-version: 2023-06-01, content-type: application/json
   - Body: message-classifier prompt + incoming message text
   - If photo attached: include image in message content array (vision)
5. **Parse JSON** node - extract Claude's classification response
6. **Respond to Webhook** - return the classification result

**Step 3: Build the content generation sub-workflow**

Create a new n8n workflow: "Social Media Agent - Content Generator"

Nodes:
1. **Webhook** (input) - receives classified message data + platform list
2. **Airtable** node - fetch brand guides from Master Config (master + relevant platform guides based on platforms_requested)
3. **Airtable** node - fetch last 30 rows from Post History (ordered by published_at desc)
4. **HTTP Request** node - call Claude API
   - Body: content-generator prompt + brand guides + post history + message text + image (if present)
5. **Parse JSON** node - extract generated content per platform
6. **Airtable** node - create new row in Pending Drafts with generated content, set all requested platform statuses to "pending"
7. **Airtable** node - create first row in Conversation Messages (agent's draft message)
8. **Respond to Webhook** - return the draft content + draft_id

**Step 4: Update the main Telegram trigger workflow**

Modify "Social Media Agent - Telegram Trigger" workflow:

1. **Telegram Trigger** (existing)
2. **Execute Sub-Workflow** - call Message Classifier with the message data
3. **Switch** node on classification:
   - "draft_reply" -> (placeholder for Task 8 - approval flow)
   - "content_request" -> Execute Sub-Workflow: Content Generator
   - "agent_question" -> (placeholder for Task 9 - agent questions)
   - "not_for_agent" -> No Operation (ignore)
4. After Content Generator returns:
   - **Telegram Send Message** - format and send each platform's draft back to the group, clearly labelled
   - Reply to Mick's original message so the thread is linked

**Step 5: Test the full flow**

- Send a text message: "Do a post about a solar install we just finished in Kyneton, 6.6kW system"
- Verify: classifier returns "content_request", platforms default to all
- Verify: content generator returns drafts for FB/IG, GBP, and blog
- Verify: drafts appear in Telegram group as a reply to the original message
- Verify: Airtable has a new Pending Drafts row and a Conversation Messages row

- Send a photo with caption: "Aircon install at 5 Smith St Woodend"
- Verify: image is sent to Claude vision API
- Verify: generated content references details visible in the photo

- Send: "Just do a Facebook post about our new EV charger service"
- Verify: classifier extracts platform = fb_ig only, no GBP or blog generated

- Send: "Hey mate how's it going"
- Verify: classified as not_for_agent, no response from bot

**Step 6: Iterate on content quality**

This is the critical quality gate. Review generated content against the brand guides:
- Does FB/IG caption match his voice?
- Is GBP post appropriately short and action-oriented?
- Is blog content well structured with proper SEO?
- Does the content sound like Mick wrote it?

Adjust prompts in `prompts/content-generator.md` and re-test until quality is consistently good. This may take multiple rounds. Do not proceed until satisfied.

---

## Phase 3a: Full Plumbing

### Task 7: Set Up Google Drive Folder Structure

**Blocked by: Google Drive OAuth2 credential from Mick**

**Step 1: Create a one-time setup workflow**

Create n8n workflow: "Social Media Agent - Drive Setup (one-time)"

Nodes:
1. **Manual Trigger**
2. **Google Drive** node - Create Folder: "Trentham Social Media" (root)
3. **Google Drive** node x6 - Create subfolders: Solar, Air Conditioning, Electrical, EV Charging, Batteries, Team, General (parent = root folder)
4. **Airtable** node - Write root folder ID to Master Config
5. **Airtable** node - Write each subfolder ID to Master Config (add new config rows for each subfolder)

**Step 2: Run the setup workflow**

Execute once. Verify folders exist in Google Drive. Verify IDs stored in Airtable.

**Step 3: Scan for existing images**

If Mick already has photos in Drive, create a workflow that:
1. Lists all files in each subfolder
2. For each image, creates a row in the Image Library table with google_drive_file_id, folder, and source = "pre-existing"

---

### Task 8: Build Approval Flow

**Blocked by: Task 6 working**

**Step 1: Build the approval parser sub-workflow**

Create n8n workflow: "Social Media Agent - Approval Parser"

Nodes:
1. **Webhook** (input) - receives reply message text + draft_id
2. **Airtable** node - fetch the Pending Draft by draft_id
3. **Airtable** node - fetch all Conversation Messages for this draft_id (ordered by timestamp)
4. **HTTP Request** node - call Claude API with approval-parser prompt + draft state + conversation history + Mick's reply
5. **Parse JSON** node - extract per-platform actions
6. **Respond to Webhook** - return parsed actions

**Step 2: Build the redraft sub-workflow**

Create n8n workflow: "Social Media Agent - Redraft"

Nodes:
1. **Webhook** (input) - receives draft_id + which platforms to redraft + instructions
2. **Airtable** node - fetch current draft content
3. **Airtable** node - fetch brand guides from Master Config
4. **Airtable** node - fetch conversation history
5. **HTTP Request** node - call Claude API with content-generator prompt + original content + redraft instructions
6. **Airtable** node - update Pending Draft with new content for affected platforms, set statuses to "pending", increment revision_count
7. **Airtable** node - add agent's new draft message to Conversation Messages
8. **Respond to Webhook** - return updated draft

**Step 3: Wire approval flow into main trigger workflow**

Update "Social Media Agent - Telegram Trigger":

In the "draft_reply" branch of the Switch node:
1. **Airtable** node - look up Pending Draft by matching `reply_to_message.message_id` to `telegram_message_id`
2. **Airtable** node - log Mick's reply to Conversation Messages
3. **Execute Sub-Workflow** - call Approval Parser with reply + draft_id
4. **Switch** node on actions:
   - Any platform has "redraft" -> Execute Sub-Workflow: Redraft for those platforms -> Telegram Send Message with updated drafts
   - All remaining platforms "approve" -> proceed to mock publish
   - All platforms "skip" -> Telegram Send Message: "Got it, scrapped."
5. **Mock publish branch:**
   - **Telegram Send Message** - "Here's what would be published:" + formatted preview per approved platform
   - **Airtable** node - update approved platform statuses to "published"
   - **Airtable** node - create Post History rows for each published platform
   - **Airtable** node - update Image Library usage dates for the image

**Step 4: Test the approval flow**

Test cases:
- Reply "approve" to a draft -> all platforms mock published, Post History rows created
- Reply "make it shorter" -> all platforms redrafted, new draft sent back
- Reply "approve the social, redo the blog" -> FB/IG + GBP published, blog redrafted
- Reply "scrap the GBP one, rest is good" -> GBP skipped, others published
- Reply "actually can you use a different photo" -> agent asks for clarification
- Multiple rapid replies -> each matched to correct draft
- Send two content requests, get two drafts, reply to each separately -> correct matching

---

### Task 9: Build Agent Question Handler

**Blocked by: Task 6 working**

**Step 1: Wire into main trigger workflow**

In the "agent_question" branch of the Switch node:
1. **Airtable** node - fetch Post History (last 30 rows)
2. **Airtable** node - fetch Master Config (schedule info)
3. **HTTP Request** node - call Claude API with the question + relevant data
4. **Telegram Send Message** - reply with Claude's answer

**Step 2: Test**

- "What did we post last week?" -> agent checks Post History, summarises
- "When's the next scheduled post?" -> agent checks config, answers
- "How many posts have we done this month?" -> agent counts Post History rows

---

### Task 10: Build Telegram Photo Upload to Drive

**Blocked by: Google Drive credential**

**Step 1: Add to main trigger workflow**

When the classifier identifies a content_request with a photo attached, before content generation:
1. **Telegram Get File** node - download the photo
2. **HTTP Request** node - call Claude API with just the image + description to classify which subfolder it belongs in (Solar, Air Conditioning, etc.)
3. **Google Drive** node - upload the file to the classified subfolder
4. **Airtable** node - create a new row in Image Library with the file details, folder, description, source = "telegram_upload"

**Step 2: Test**

- Upload a photo of a solar install with description "solar install Kyneton" -> saved to Solar/ folder, Image Library row created
- Upload a photo of an aircon with "split system install" -> saved to Air Conditioning/ folder
- Upload a photo with vague description "job today" -> agent asks which category, or uses Claude vision to classify

---

### Task 11: Build Google Drive-Triggered Content

**Blocked by: Google Drive credential**

**Step 1: Add Drive reference handling to classifier**

Update the message classifier prompt to recognise Drive references:
- "Photos from the Smith St job are in Drive" -> content_request with trigger_type = "drive"
- "Use the photos in the Solar folder for a post" -> content_request with trigger_type = "drive"

**Step 2: Build the Drive retrieval logic**

When trigger_type is "drive", before content generation:
1. **Airtable** node - fetch Drive folder IDs from Master Config
2. **Google Drive** node - list files in the referenced folder (or search by keyword if Mick references a job name)
3. Select image(s) - check Image Library for per-platform usage, pick unused or least recently used
4. Pass image(s) to content generator

**Step 3: Test**

- "The photos from the Kyneton solar job are in Drive, do a post" -> agent finds photos in Solar folder, generates content
- "Use something from the EV folder for a post" -> agent picks an unused image from EV Charging folder

---

### Task 12: Build Autonomous Scheduled Posts

**Blocked by: Google Drive credential + Tasks 6, 8 working**

**Step 1: Create the autonomous post workflow**

Create n8n workflow: "Social Media Agent - Autonomous Post"

Nodes:
1. **Schedule Trigger** - cron expression built from Airtable config (post_days + post_time)
2. **Airtable** node - fetch Master Config (filler_topics, last_filler_topic, folder IDs)
3. **Code** node - select next topic in rotation (skip last_filler_topic)
4. **Airtable** node - query Image Library for images in the relevant folder, filter by per-platform usage dates
5. **Code** node - select image (unused preferred, least recently used as fallback)
6. **IF** node - check if image library is running thin (< 3 unused images in folder)
   - Yes -> **Telegram Send Message**: "Running low on fresh [topic] photos - upload some new ones when you get a chance"
7. **Google Drive** node - download selected image
8. **Execute Sub-Workflow** - call Content Generator with topic + image + trigger_type = "autonomous"
9. **Telegram Send Message** - send draft to group for approval (enters same approval flow as manual posts)
10. **Airtable** node - update last_filler_topic in Master Config

**Step 2: Test**

- Manually trigger the workflow -> verify topic rotation works
- Verify image selection avoids previously used images per platform
- Verify draft enters approval flow correctly
- Trigger multiple times -> verify topics rotate and images don't repeat

---

### Task 13: Stress Testing

**Blocked by: All previous tasks complete**

**Step 1: Concurrent drafts test**

Send 3 content requests in rapid succession. Verify:
- All three create separate Pending Draft rows
- All three return separate drafts to Telegram
- Replying to each draft matches the correct one
- Approving one doesn't affect the others

**Step 2: Rapid redraft test**

Start a draft, request 5 consecutive changes. Verify:
- Each redraft updates the correct draft
- Conversation history grows correctly
- Revision count tracks accurately
- Final approve publishes correctly

**Step 3: Mixed trigger test**

Simultaneously:
- Send a Telegram photo request
- Trigger an autonomous post manually
- Reference a Drive folder

Verify all three are handled independently without interference.

**Step 4: Edge case test**

- Send empty message (no text, no photo) -> agent ignores or asks for clarification
- Send very long description (500+ words) -> agent handles gracefully
- Send message when no images exist in Drive -> agent notifies, doesn't crash
- Reply to a very old draft that was already published -> agent responds appropriately

---

## Phase 3b: Connect Live APIs

### Task 14: Connect Buffer (Facebook + Instagram)

**Blocked by: Buffer API key from Mick + all Phase 3a tests passing**

**Step 1: Add Buffer credential to n8n**

Add Header Auth credential:
- Name: "Buffer API"
- Header Name: `Authorization`
- Header Value: `Bearer {buffer_api_key}`

**Step 2: Fetch Buffer profile IDs**

Create a one-time workflow to call Buffer's profiles endpoint:
- GET `https://api.bufferapp.com/1/profiles.json`
- Extract FB and IG profile IDs
- Store in Airtable Master Config: buffer_profile_ids

**Step 3: Build the Buffer publish node sequence**

In the approval flow, replace mock publish for FB/IG with:
1. **HTTP Request** node - POST to Buffer create update endpoint
   - Profile IDs: from Airtable config
   - Text: content_fb_ig from the draft
   - Media: image URL from Google Drive (must be publicly accessible - may need to generate a sharing link)
2. **IF** node - check for errors
   - Success -> extract post URL, log to Post History
   - Failure -> Telegram Send Message: "Failed to publish to Facebook/Instagram: [error]. The other platforms were not affected."

**Step 4: Test with a single post**

Publish one test post to FB and IG via Buffer. Verify it appears correctly on both platforms. Verify Post History is logged. Verify Image Library usage dates updated.

---

### Task 15: Connect Google Business Profile API

**Blocked by: GBP OAuth2 credential from Mick + all Phase 3a tests passing**

**Step 1: Fetch GBP location ID**

Create a one-time workflow:
- GET `https://mybusiness.googleapis.com/v4/accounts` (using GBP OAuth2 credential)
- GET `https://mybusiness.googleapis.com/v4/accounts/{accountId}/locations`
- Extract location ID
- Store in Airtable Master Config: gbp_location_id

**Step 2: Build the GBP publish node sequence**

In the approval flow, replace mock publish for GBP with:
1. **HTTP Request** node - POST to `https://mybusiness.googleapis.com/v4/accounts/{accountId}/locations/{locationId}/localPosts`
   - Body: `{ "summary": content_gbp, "media": { "sourceUrl": image_url, "mediaFormat": "PHOTO" }, "topicType": "STANDARD", "callToAction": { "actionType": cta_button, "url": website_url } }`
   - Auth: GBP OAuth2 credential
2. **IF** node - check for errors
   - Success -> log to Post History
   - Failure -> Telegram Send Message with error

**Step 3: Test with a single post**

Publish one test post to GBP. Verify it appears in Google Search/Maps. Verify Post History logged.

---

### Task 16: Connect Wix Blog API

**Blocked by: Wix API key from Mick + all Phase 3a tests passing**

**Step 1: Add Wix credential to n8n**

Add Header Auth credential:
- Name: "Wix API"
- Header Name: `Authorization`
- Header Value: (Wix API key)

**Step 2: Fetch Wix site ID and existing categories**

Create a one-time workflow:
- Call Wix API to list sites, extract site ID
- Call Wix Blog API to list existing categories
- Store site ID in Airtable Master Config
- Note available categories for content generator prompt

**Step 3: Build the Wix publish node sequence**

In the approval flow, replace mock publish for blog with:
1. **Code** node - convert content_blog (markdown) to Wix rich content format
   - This requires mapping headings, paragraphs, images to Wix's `richContent` JSON structure
2. **HTTP Request** node - POST to Wix Draft Posts API to create draft
   - Body: `{ "draftPost": { "title": title, "excerpt": meta_description, "richContent": converted_content, "featured_image": image_url, "categoryIds": [matching_category_ids] } }`
3. **HTTP Request** node - POST to Wix Publish Draft endpoint with the draft ID
4. **IF** node - check for errors
   - Success -> extract post URL, log to Post History
   - Failure -> Telegram Send Message with error

**Step 4: Test with a single blog post**

Publish one test blog post. Verify:
- Title, body, headings render correctly on Wix site
- Meta description is set
- Featured image appears
- URL slug is SEO-friendly
- Post History logged

---

### Task 17: Enable Live Publishing + Final Verification

**Blocked by: Tasks 14-16 all passing**

**Step 1: End-to-end test per trigger type**

- Telegram trigger: photo + description -> draft -> approve -> verify published on all platforms
- Drive trigger: reference folder -> draft -> approve -> verify published
- Autonomous: manual trigger -> draft -> approve -> verify published

**Step 2: Verify error handling**

- Temporarily use invalid credentials for one platform -> verify partial publish works (others succeed, failed one reports error, no duplicate posts)

**Step 3: Get Mick's sign-off**

Send a message to Mick via Telegram:
- Show him the test posts on each platform
- Walk him through the approval flow
- Confirm he's happy with content quality
- Get explicit approval to enable autonomous scheduling

**Step 4: Activate autonomous scheduling**

Enable the Schedule Trigger in the autonomous post workflow. The agent is now live.

---

## Task Dependency Summary

| Task | Name | Depends On | Blocked By Mick? |
|------|------|-----------|-------------------|
| 1 | Scrape content | None | No |
| 2 | Airtable schema | None | No |
| 3 | Telegram trigger | None | No |
| 4 | Draft prompts | None | No |
| 5 | Brand guides | Task 1, 4 | Claude API key |
| 6 | Content generation in n8n | Task 2, 3, 5 | Claude API key |
| 7 | Google Drive folders | None | Drive credential |
| 8 | Approval flow | Task 6 | No |
| 9 | Agent question handler | Task 6 | No |
| 10 | Photo upload to Drive | Task 6, 7 | Drive credential |
| 11 | Drive-triggered content | Task 6, 7 | Drive credential |
| 12 | Autonomous posts | Task 6, 7, 8 | Drive credential |
| 13 | Stress testing | Tasks 6-12 | No |
| 14 | Connect Buffer | Task 13 | Buffer API key |
| 15 | Connect GBP API | Task 13 | GBP credential |
| 16 | Connect Wix API | Task 13 | Wix API key |
| 17 | Go live | Tasks 14-16 | Mick sign-off |
