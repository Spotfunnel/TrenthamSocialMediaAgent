# V2 Social Media Agent — Design Document

## 1. Overview

Complete rebuild of the Trentham Electrical & Solar social media agent. Replaces the v1 system (7 workflows, 150+ nodes, manual IF routing) with a single AI Agent-based workflow. Designed for multi-client scalability from day one.

**Key decisions:**
- New Telegram bot (@TrenthamSocialsV2bot) — v1 stays untouched
- New Airtable base — no data overlap with v1
- Single n8n workflow with AI Agent node + sub-workflow tools
- Multi-tenant: one Airtable row per client, same workflows serve all
- gpt-5.4-mini for all AI (agent routing, content generation, judging)
- Buffer for social publishing (IG + FB + GBP)
- Wix for blog publishing
- Google Drive as image library (search + read only)

---

## 2. Architecture

```
Trigger 1: Telegram (user messages)
Trigger 2: Schedule Trigger (Monday 2pm AEST cron)
    │
    ├─→ Load Client Config (Code node: query V2 Config by chat_id)
    │
    ├─→ Photo Collector (3 nodes)
    │     Extract Metadata → Wait 5s (if media group) → Collect Photos
    │
    ├─→ AI Agent (Tools Agent, gpt-5.4-mini, Buffer Window Memory 15)
    │     │
    │     ├── Tool: create_social_post    → Call V2-Social-Generator sub-workflow
    │     ├── Tool: create_blog_post      → Call V2-Blog-Generator sub-workflow
    │     ├── Tool: edit_draft            → Custom Code (GPT targeted edit + Airtable update)
    │     ├── Tool: search_drive_folder   → Custom Code (Drive API via n8n credential)
    │     ├── Tool: lookup_drafts         → HTTP Request (Airtable query)
    │     ├── Tool: publish_post          → Call V2-Publisher sub-workflow
    │     ├── Tool: send_telegram         → Custom Code (Telegram sendMessage API)
    │     └── Tool: plan_weekly_posts     → Custom Code (read schedule config, generate briefs)
    │
    └─→ Photo Archive (parallel branch)
          Download from Telegram → Upload to Drive → Share publicly → Update draft image_url

Sub-workflows (called as tools):
  V2-Social-Generator: examples + GPT generation + judge + save draft + preview
  V2-Blog-Generator:   brand guide + GPT generation + SEO validation + judge + images + save + preview
  V2-Publisher:         Buffer publish (social) OR Wix publish (blog) + post history log
```

**Node count estimate:**
- Main workflow: ~15 nodes (2 triggers, config loader, photo collector, AI agent with 8 tools, photo archive)
- V2-Social-Generator: ~10 nodes
- V2-Blog-Generator: ~12 nodes
- V2-Publisher: ~8 nodes
- **Total: ~45 nodes across 4 workflows** (vs 150+ in v1's 7 workflows)

---

## 3. AI Agent Configuration

**Agent type:** Tools Agent (uses OpenAI function calling)
**Model:** gpt-5.4-mini (via OpenAI credential)
**Memory:** Buffer Window Memory, context length 15, session key = telegram chat_id
**Temperature:** 0.3 (focused routing, not creative)

**System prompt:**
```
You are the social media assistant for {client_name}. You manage social media posts 
across Instagram, Facebook, Google Business Profile, and the Wix blog.

You communicate via Telegram with the business owner. Be direct, helpful, concise.

CAPABILITIES (use the right tool for each):
- Create social posts: use create_social_post tool with the user's brief
- Create blog posts: use create_blog_post tool with the topic
- Edit a draft: use edit_draft tool when user replies to a draft with changes
- Search Drive photos: use search_drive_folder when user references a job/folder
- Look up drafts: use lookup_drafts to check pending/published posts
- Publish: use publish_post when user approves a draft
- Schedule posts: use plan_weekly_posts for batch content planning
- Reply to user: use send_telegram for any response

RULES:
- Always send an ack message before long operations ("On it...")
- When user sends photos, they're attached to the message — use them for the post
- When user replies to a draft preview, treat it as an edit request
- "approve" means publish the draft
- "IG and FB only" means exclude GBP
- If the brief is too vague (<5 words, no topic), ask for more detail
- Never publish without explicit approval
- Reference {brand_voice} for tone guidance

CONFIG:
Client: {client_name}
Platforms: {buffer_ig_channel}, {buffer_fb_channel}, {buffer_gbp_channel}
Drive folder: {google_drive_folder_id}
Brand voice: {brand_voice}
```

---

## 4. Tool Specifications

### 4.1 create_social_post
**Type:** Call n8n Workflow (V2-Social-Generator)
**Input:** brief (string), platforms (array), photo_file_ids (string), image_url (string), client_config (object)
**What it does:**
1. Fetch 30 random examples from V2 Example Bank (matching client_id)
2. Fetch last 20 drafts to avoid repetition
3. If no photo: GPT classifies brief → Drive folder → search Drive → pick LRU image
4. GPT generates IG + FB + GBP captions (respecting platform filter)
5. Judge scores 1-5. If < 3.0, retry with feedback (up to 3 attempts)
6. Save to V2 Drafts table
7. Send preview message to Telegram with preview URL
**Output:** draft_id, preview_url, score

### 4.2 create_blog_post
**Type:** Call n8n Workflow (V2-Blog-Generator)
**Input:** topic (string), photo_file_ids (string), client_config (object)
**What it does:**
1. Fetch brand guide + last 3 blogs + examples + anti-examples
2. GPT generates 600-1200 word blog (title, body, meta, slug, keyword)
3. SEO validation (keyword density, meta length, H2 count, internal links)
4. Judge scores 1-5. Retry if < 3.0
5. Select 4 images (cover portrait, hero landscape, 2 body) from Drive via LRU
6. Save to V2 Drafts (type=blog, blog_images JSON)
7. Send Vercel preview link to Telegram
**Output:** draft_id, preview_url, score, facts_to_verify

### 4.3 edit_draft
**Type:** Custom Code Tool
**Input:** draft_id (string), edit_instruction (string), client_config (object)
**What it does:**
1. Fetch draft from V2 Drafts by ID or telegram_message_id
2. Determine draft type (social vs blog)
3. For social: GPT edits IG caption → replicate to FB (strip hashtags) + GBP (consultative tone)
4. For blog: GPT edits body with targeted instruction (preserve everything else)
5. Special actions: remove_platform, swap_image (pick new from Drive), change_title
6. Update draft in Airtable
7. Send updated preview to Telegram
**Output:** updated draft_id, action_taken

### 4.4 search_drive_folder
**Type:** Custom Code Tool (uses n8n Google Drive credential internally)
**Input:** folder_name (string)
**What it does:**
1. Search Drive for folders matching name (fuzzy match)
2. List all image files in matched folder
3. Cross-reference with V2 Used Images table
4. Return available images sorted by least recently used
**Output:** folder_name, folder_id, images[] (url, name, used_before)

### 4.5 lookup_drafts
**Type:** HTTP Request Tool (Airtable API)
**Input:** filter (string — e.g. "status=pending", "type=social", or specific draft_id)
**What it does:**
1. Query V2 Drafts table with filter
2. Return draft summaries (brief, type, status, score, platforms)
**Output:** drafts[] array

### 4.6 publish_post
**Type:** Call n8n Workflow (V2-Publisher)
**Input:** draft_id (string), client_config (object), scheduled_date (optional)
**What it does:**
1. Fetch draft from V2 Drafts
2. If type=social: publish to Buffer (IG + FB + GBP) per platform config
3. If type=blog: convert to Wix Ricos format, publish/schedule to Wix
4. Log to V2 Post History
5. Mark image as used in V2 Used Images
6. Update draft status to "published"
7. Send confirmation to Telegram
**Output:** published_platforms[], post_ids

### 4.7 send_telegram
**Type:** Custom Code Tool
**Input:** text (string), reply_to_message_id (optional)
**What it does:** Send a message to the client's Telegram chat. Used for acks, responses, error messages.
**Output:** message_id

### 4.8 plan_weekly_posts
**Type:** Custom Code Tool
**Input:** (none — reads from V2 Config)
**What it does:**
1. Read V2 Config: posts_per_week, topic_rotation, last_topic_index
2. Check crisis_pause flag
3. Plan N posts across the week (Mon/Wed/Fri spread)
4. Generate unique GPT briefs per topic (avoids recent angles)
5. For each: call create_social_post tool
6. For job_spotlights: send Telegram prompt asking for photos
7. Update last_topic_index
8. Send weekly summary to Telegram
**Output:** planned_count, generated_count, prompted_count

---

## 5. Airtable Schema (New Base)

### V2 Config (one row per client)
| Field | Type | Purpose |
|-------|------|---------|
| client_name | Text | Business name |
| active | Checkbox | Is this client active? |
| telegram_chat_id | Text | Identifies which client is messaging |
| telegram_bot_token | Text | Bot token for this client |
| buffer_api_key | Text | Buffer API key |
| buffer_ig_channel | Text | Buffer Instagram channel ID |
| buffer_fb_channel | Text | Buffer Facebook channel ID |
| buffer_gbp_channel | Text | Buffer GBP channel ID |
| wix_api_key | Text | Wix REST API key |
| wix_site_id | Text | Wix site ID |
| wix_member_id | Text | Wix blog author member ID |
| openai_api_key | Text | OpenAI API key |
| google_drive_folder_id | Text | Root Drive folder for image library |
| brand_voice | Long text | Brand tone description for system prompt |
| preview_base_url | URL | Vercel preview app URL |
| blog_preview_base_url | URL | Vercel blog preview URL |
| posts_per_week | Number | How many auto-posts per week |
| post_time | Text | HH:MM for scheduled posts |
| topic_rotation | Text | Comma-separated topic list |
| last_topic_index | Number | Current position in rotation |
| crisis_pause | Checkbox | Emergency stop for all auto-content |

### V2 Drafts (all content — social + blog)
| Field | Type | Purpose |
|-------|------|---------|
| client_id | Link to V2 Config | Which client |
| type | Select: social / blog | Content type |
| content_brief | Text | Original user request |
| content_ig | Long text | Instagram caption |
| content_fb | Long text | Facebook caption |
| content_gbp | Long text | GBP text |
| content_blog | Long text (JSON) | Blog object: title, body, slug, meta, keyword |
| status | Select | pending / approved / published / skipped |
| platforms | Text | fb_ig, gbp (comma-separated) |
| photo_file_ids | Text | Telegram file IDs (comma-separated) |
| image_url | Text | Permanent Drive URLs (comma-separated) |
| blog_images | Long text (JSON) | 4-slot array [{url, alt_text, isPortrait}] |
| wix_post_id | Text | Wix post ID (after blog publish) |
| judge_score | Number | Quality score 0-5 |
| judge_attempts | Number | Retry count |
| telegram_message_id | Text | For reply chaining |
| chat_id | Text | Telegram chat ID |
| scheduled_date | DateTime | For scheduled publishing |

### V2 Post History
| Field | Type | Purpose |
|-------|------|---------|
| client_id | Link to V2 Config | Which client |
| platform | Select | instagram / facebook / gbp / wix |
| content | Long text | Published content |
| draft_id | Link to V2 Drafts | Source draft |
| published_date | DateTime | When published |
| post_id | Text | Platform-specific post ID |

### V2 Example Bank
| Field | Type | Purpose |
|-------|------|---------|
| client_id | Link to V2 Config | Which client's examples |
| content | Long text | Real post text |
| post_type | Select | job_spotlight / educational / team_brand / product_spotlight / community / seasonal |

### V2 Used Images
| Field | Type | Purpose |
|-------|------|---------|
| client_id | Link to V2 Config | Which client |
| drive_file_id | Text | Google Drive file ID |
| used_date | DateTime | When used |
| draft_id | Link to V2 Drafts | Which draft used it |
| usage_type | Select | social / blog_cover / blog_hero / blog_body |

---

## 6. Photo & Image Flow

### User sends photo via Telegram:
```
Telegram photo → Extract file_id → Photo Collector (media group handling)
    │
    ├─→ AI Agent receives photo metadata (file_ids in message context)
    │     Agent calls create_social_post or create_blog_post with photo_file_ids
    │
    └─→ Photo Archive (parallel)
          Download from Telegram API → Upload to Drive (Uploads folder) → Share publicly
          → Update draft's image_url with permanent lh3.googleusercontent.com/d/{id} URL
```

### Autonomous post (no user photo):
```
Agent calls create_social_post with brief only (no photos)
    │
    └─→ V2-Social-Generator:
          GPT classifies brief → folder name (Solar, Batteries, Team, etc.)
          → Search Drive for folder → List images
          → Check V2 Used Images → Pick least recently used
          → Set image_url on draft
          → Log to V2 Used Images
```

### Blog images (4 slots):
```
Agent calls create_blog_post
    │
    └─→ V2-Blog-Generator:
          Analyze blog topic → determine folder
          → Search Drive for folder → List images
          → Check V2 Used Images → Pick 4 LRU images
            Slot 0 (cover): portrait orientation preferred
            Slot 1 (hero): landscape
            Slot 2-3 (body): landscape, different from hero
          → Store as blog_images JSON in draft
          → Log all 4 to V2 Used Images
```

### Drive folder reference ("use photos from 21 Trentham St"):
```
Agent calls search_drive_folder("21 Trentham St")
    │
    └─→ Fuzzy match folder name in Drive
          → List all images in folder
          → Agent decides: carousel (multiple) or single
          → Calls create_social_post with selected image URLs
```

---

## 7. Multi-Client Scalability

**How to onboard a new client:**
1. Add a row to V2 Config with their details (API keys, channel IDs, brand voice)
2. Create a Telegram bot for them via BotFather
3. Set the bot's webhook to point at the same n8n workflow
4. Add their real posts to V2 Example Bank (client_id linked)
5. Create their Drive folder structure
6. Done — the workflow reads config by matching telegram_chat_id

**What's shared across clients:**
- n8n workflows (identical for all)
- Vercel preview apps (reads from Airtable, client-agnostic)
- AI models (same gpt-5.4-mini, or per-client key if they want their own)

**What's per-client:**
- V2 Config row
- V2 Example Bank entries
- V2 Drafts records (filtered by client_id)
- Google Drive folder
- Telegram bot
- Buffer account + channels
- Wix site

---

## 8. What V2 Eliminates from V1

| V1 Component | Why eliminated |
|---|---|
| 8 IF routing nodes | Agent handles routing via tool calling |
| Separate classifier GPT call | Agent IS the classifier |
| Parse Classification node | Agent handles internally |
| Check Draft Type node | Agent queries Airtable and decides |
| Is Social Draft? IF node | Agent knows from draft lookup |
| Route Redraft? IF node | Agent decides based on edit result |
| Conversation Messages table | Agent has Buffer Window Memory (15 messages) |
| Master Config in Airtable (for API keys only) | Merged into V2 Config per-client |
| Separate WF5 Q&A workflow | Agent handles Q&A natively |
| WF6 as separate workflow | Schedule trigger + plan_weekly_posts tool in main workflow |
| Duplicate nodes | Clean build, no cruft |
| 7 separate workflows | 1 main + 2-3 sub-workflows |
| Brief richness check (extra GPT call) | Agent asks for detail naturally |
| Telegraph preview (backup) | Vercel only |

---

## 9. Naming Convention

Everything prefixed with "V2" or "SMA-V2":
- Workflow: `SMA-V2 Agent`
- Sub-workflows: `SMA-V2 Social Generator`, `SMA-V2 Blog Generator`, `SMA-V2 Publisher`
- Airtable base: `SMA V2`
- Tables: `V2 Config`, `V2 Drafts`, `V2 Post History`, `V2 Example Bank`, `V2 Used Images`
- Webhook paths: `/sma-v2-agent`
- Telegram bot: @TrenthamSocialsV2bot
- Preview apps: `v2-preview-social`, `v2-preview-blog` (new Vercel deploys)

---

## 10. Risk & Rollback

- V1 stays completely untouched (different bot, different Airtable base, different workflows)
- If v2 fails, switch Mick back to v1 bot — zero downtime
- V2 can be deleted entirely with no impact on v1
- Both can run simultaneously during testing
