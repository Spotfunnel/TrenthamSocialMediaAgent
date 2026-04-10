# Social Media Agent - Build Design
## Trentham Electrical & Solar | April 2026

---

## Decisions Made

- **Platform:** n8n (self-hosted at trentham.app.n8n.cloud)
- **FB/IG publishing:** Buffer API (not Meta Graph API directly)
- **GBP publishing:** Google Business Profile API (native OAuth2 credential in n8n)
- **Blog publishing:** Wix Blog API (Draft -> Publish flow)
- **AI content generation:** Claude API (Anthropic)
- **Approval channel:** Telegram group with bot

---

## Credentials Status

### Already in n8n:
- Telegram API
- Airtable Personal Access Token
- Gmail OAuth2 (x2)
- Google Calendar OAuth2

### Waiting on Mick:
- Google Drive OAuth2 credential (he sets up in n8n)
- Google Business Profile OAuth2 credential (he sets up in n8n)
- Claude (Anthropic) API key
- Buffer API key + confirm FB/IG connected
- Wix API key

---

## What We Can Build Before Mick's APIs Arrive

| Phase | Blocked by Mick? | Notes |
|-------|-------------------|-------|
| Phase 1a: Scrape all public content | No | All content is publicly accessible |
| Phase 1b: Generate brand style guides | Yes - needs Claude API key | Could draft prompts in advance |
| Phase 1c: Review and refine guides | Yes - depends on 1b | |
| Phase 2a: Telegram bot + n8n trigger | No | Telegram credential already exists |
| Phase 2b: AI content generation | Yes - needs Claude API key | |
| Phase 2c: Multi-platform output test | Yes - needs Claude API key | |
| Phase 3a: Full plumbing (no live publish) | Yes - needs Claude + Drive + Airtable config | |
| Phase 3b: Connect live APIs | Yes - needs all credentials | |

**Immediate work (no blockers):** Phase 1a (scrape everything) and Phase 2a (Telegram trigger setup). We can also pre-build the Google Drive folder structure, Airtable config schema, and draft all Claude prompts - just can't test them until the API key arrives.

---

## Phase 1: Brand Intelligence

### 1a. Scrape All Existing Content

One-time data collection from all public channels:

- **Instagram** - scrape all posts (captions, hashtags, post dates, engagement if visible)
- **Facebook** - scrape all page posts (text, post type, dates)
- **Google Business Profile** - scrape all GBP posts visible in search/maps
- **Wix blog** - scrape all published blog posts (title, body, headings, meta descriptions)

No APIs from Mick required - all public content. Use web scraping (Firecrawl or similar).

### 1b. Generate Brand Style Guides

Feed all scraped content into Claude. Recent posts weighted higher than older ones. Both images and captions must be analysed - posts are a package of visual + text + format choice.

**These guides are the single most important deliverable.** They are the foundation the agent uses for months of autonomous content generation. Front-load the work here - more detail is always better. Every data point becomes a constraint that prevents drift.

**Output: 4 documents**

**1. Master Brand Guide**
The overarching brand identity that applies everywhere:
- Voice and tone (professional but approachable, local Macedon Ranges flavour)
- Core vocabulary and phrases he uses repeatedly
- Language he avoids (jargon, corporate speak, etc.)
- Topics and themes he covers
- Values he communicates (quality, reliability, long-term value)
- How he talks about the region (Macedon Ranges references, suburb name-dropping)
- How he talks about customers (first name? "our client"? "the homeowner"?)
- How he positions the business (premium? affordable? reliable local?)
- Emotional register - does he use humour, pride, urgency, education?
- Sentence structure patterns - short and punchy or longer and explanatory?
- First person vs third person usage
- How he handles CTAs - soft ("give us a call") vs direct ("book now")
- Seasonal/topical awareness - does he tie posts to weather, energy prices, government rebates?
- Visual identity - consistent colours, angles, framing across platforms?
- What does he photograph? Finished jobs, in-progress work, team, equipment, before/after?
- Does he show faces (team, customers) or just the work?
- Branding visibility in photos - uniforms, vehicle wraps, signage

**2. Facebook/Instagram Guide** (shared - content is identical for both)
Built on top of master guide, specific to social:
- Post type mix breakdown with percentages (single image, carousel, reel, text-only, link share)
- Caption length distribution (short <50 words, medium 50-150, long 150+) with examples of each
- Image-caption relationship patterns - does caption describe, complement, or add unseen context?
- Opening line patterns - hook with question, statement, location, emoji?
- Closing patterns - CTA, question to audience, nothing?
- Hashtag strategy - how many, which ones, branded vs generic vs location
- Emoji usage - which ones, where, frequency
- Tagging behaviour - locations, other businesses, suppliers, team members
- Carousel strategy - sequence logic, slide count, before/after vs multi-angle
- How he handles job spotlight posts vs educational/filler posts differently
- Engagement patterns - does he reply to comments? What tone?
- Posting frequency and spacing patterns
- What makes his best-performing posts different from average ones
- Image composition - angles (ground up, aerial, straight on), framing (wide shot, detail, team in frame)
- Visual consistency - colour palette, brightness, filters or raw
- What's in the frame - finished work only, in-progress, tools, vehicles, signage, team, customers?
- Before/after usage
- Time of day in photos - daylight, sunset, interior lighting

**3. Google Business Profile Guide**
Built on top of master guide, specific to GBP:
- Post type distribution (Update vs Offer vs Event)
- Text length patterns (characters used vs truncation point)
- Character constraints (~150 visible before truncation)
- CTA button choices and frequency (Call Now, Learn More, Book)
- How sales-oriented vs informational
- Photo usage - always, sometimes, never?
- Photo style compared to social (same photos recycled or different?)
- How service descriptions differ from social captions
- Local SEO signals - suburb names, service area mentions
- Urgency/timeliness in messaging
- Post structure for the short format

**4. Blog Guide**
Built on top of master guide, specific to long-form:
- Article structure patterns - intro length, section count, conclusion style
- Heading hierarchy usage (H1/H2/H3)
- Keyword placement patterns - title, first paragraph, headings, throughout
- Meta description style
- SEO patterns (title structure, heading hierarchy, keyword density)
- Internal linking patterns - how many, to what pages
- Featured image style - job photo, stock, graphic?
- In-body images - frequency, placement, captions
- Paragraph length patterns
- How technical content is simplified for homeowners
- Use of lists, bullet points, numbered steps
- Job spotlight format vs full article format (structural differences)
- Tone shift from social to blog (more formal? same?)
- How he handles pricing/cost discussions
- FAQ-style content patterns
- Content length distribution with examples
- Slug/URL structure patterns
- Intro/outro patterns
- Two content types: full articles (600-1200 words) vs job spotlights (200-400 words)

### 1c. Review and Refine

Human review of all four guides. Iterate with Claude until they accurately reflect Mick's voice. This is the quality gate - nothing proceeds until the guides are right.

Final approved guides go into Airtable config for the agent to read at runtime.

---

## Phase 2: Core Loop (Prove the Concept)

### 2a. Telegram Integration

- Connect the existing Telegram bot to an n8n workflow via Telegram Trigger node
- Handle incoming messages: text, photos, files
- Handle incoming replies (for future approval flow)
- Bot sends formatted responses back to the group
- Test: send a message, confirm n8n receives it and can reply

### 2b. Message Classification

Every incoming Telegram message hits Claude for intent classification before any other logic runs:

1. **Draft reply** - message is a reply to a bot message -> route to approval flow (matched via `reply_to_message.message_id`). This is checked first at the n8n level before even calling Claude.
2. **Content request** - "Do a post about this solar install" / photo upload with description -> triggers content generation
3. **Agent question** - "What did we post last week?" / "When's the next scheduled post?" -> Claude answers directly using Airtable data, no content generated
4. **Not for the agent** - casual chat, message to another person in the group -> agent ignores, no response

If Claude is unsure whether a message is a content request or not, it asks: "Did you want me to create a post from this?" rather than guessing wrong.

### 2c. AI Content Generation

- Wire Claude API into n8n via HTTP Request node
- System prompt loads master brand guide + relevant platform guide(s) from Airtable
- System prompt also includes the last 20-30 posts from the Post History table so Claude avoids repeating topics, angles, or phrasing
- Input: Mick's Telegram message (photo + description, or just text)
- Images sent to Claude via vision API so the agent can see the photo and generate more accurate, detailed content (not just relying on Mick's description)
- Claude parses intent from the message to determine:
  - **Which platforms** to generate for (all, just social, just blog, specific ones)
  - **Content type** (job spotlight, educational, promotional)
  - **Subject matter and details**
- If Mick doesn't specify platforms, default to all (FB/IG + GBP + blog)
- Output: draft content for each requested platform format

### 2d. Multi-Platform Output Test

From a single Telegram input, generate and return to Telegram:
- Only the platforms Mick requested (or all by default)
- Each format clearly labelled so Mick can review per platform

All returned to Telegram for human review. **No publishing.** This is purely a content quality test.

Iterate on prompts until output quality is consistently good. This may take multiple rounds.

---

## Phase 3a: Full Plumbing (No Live Publishing)

Only begins once Phase 2 content quality is confirmed.

### Core Agent Behaviour

The agent should be **confident but not reckless**. It should:
- Make reasonable assumptions and act on them (don't ask for permission on every small decision)
- Ask for clarification when genuinely needed - vague descriptions ("do a post about the job today"), ambiguous feedback, multiple possible image matches
- Never fabricate details it doesn't know - if Mick says "solar install" but doesn't mention the suburb, the agent asks rather than guessing
- Not be overly cautious - if it has enough information to produce a good draft, just do it. Mick can always request changes in the approval flow.

The bar is: would a competent human assistant ask this question, or would they just get on with it?

### Agentic Telegram Interaction

The Telegram conversation must feel like chatting with an assistant, not issuing commands. Claude processes every incoming message with full conversation context and reasons about what Mick wants.

Examples of natural interactions the agent must handle:
- "Actually use the photo from last week's solar job instead"
- "Make it sound more casual"
- "Can you make the blog longer and add something about the VEU rebate"
- "Hold off on posting this until Friday"
- "What did we post last week?"
- "Approve all except the blog"
- "The Instagram one needs to be shorter, rest is fine"
- "Scrap the GBP one, approve the rest"

**Conversation history** is stored in Airtable keyed by draft ID. Each message from Mick and each agent response is appended to the thread. The full thread is passed to Claude on every message so the agent has context for multi-turn conversations.

### Approval Flow

The approval flow is conversational, not keyword-based. Claude interprets Mick's natural language reply and determines the action per platform:

- "Approve" -> publishes all requested platforms
- "Approve but skip the blog" -> publishes FB/IG + GBP, drops blog
- "The Instagram one needs to be shorter, rest is fine" -> publishes FB + GBP, redrafts IG only
- "Scrap the GBP one, approve the rest" -> drops GBP, publishes others
- Any change request -> Claude redrafts only the affected platform(s) and resends

**Per-platform tracking:** Each platform in a draft has its own status (pending / approved / redrafting / skipped). Mick can approve, reject, or request changes for each independently in a single message.

- State tracking in Airtable (pending drafts, message IDs, conversation history, per-platform status)
- Handle multiple concurrent pending drafts via `reply_to_message.message_id` matching
- Unlimited redraft cycles

### Google Drive Integration
- Create folder structure:
  ```
  Trentham Social Media/
  ├── Solar/
  ├── Air Conditioning/
  ├── Electrical/
  ├── EV Charging/
  ├── Batteries/
  ├── Team/
  └── General/
  ```
- Auto-save Telegram photo uploads to appropriate subfolder (agent categorises based on description)
- Image selection logic for autonomous posts:
  - Query relevant subfolder based on scheduled topic
  - Check Image Library table to avoid reusing images on the same platform
  - If all images in a subfolder have been used on the target platform(s), pick the least recently used
  - If the image library is running thin, proactively message Mick: "Running low on fresh solar photos - upload some new ones when you get a chance"
- Store all folder IDs in Airtable config

### Content Triggers (all three)
- **Telegram-triggered:** Photo + description -> draft -> approval -> (mock publish)
- **Google Drive-triggered:** User references folder -> retrieve images -> draft -> approval -> (mock publish)
- **Autonomous/scheduled:** n8n schedule trigger -> select topic from config -> select image from Drive -> draft -> approval -> (mock publish)

### Airtable Config
- All config fields from the brief (folder IDs, platform IDs, schedule, topics, brand guides)
- Five tables total: Master Config, Pending Drafts, Conversation Messages, Post History, Image Library
- See Airtable Schema section below for full structure

### Mock Publishing
- Every "publish" step sends the final approved content back to Telegram as a preview
- Formatted per platform (shows what would be posted to each)
- Includes the image that would be attached
- No actual API calls to Buffer, GBP, or Wix

### Stress Testing
- Multiple concurrent Telegram uploads
- Rapid-fire approval/redraft cycles
- Autonomous posts firing while manual posts are pending
- Edge cases: no images in Drive folder, empty descriptions, very long descriptions

---

## Phase 3b: Connect Live APIs (Last Step)

Only after Phase 3a is fully tested and stable.

- Replace mock publish with real API calls:
  - **Buffer API** -> Facebook and Instagram
  - **GBP API** -> Google Business Profile posts
  - **Wix Blog API** -> Draft post -> Publish draft
- Test each platform individually with a single post
- Confirm success messages return platform links to Telegram
- Get Mick's explicit sign-off before enabling scheduled/autonomous publishing
- Error handling: if one platform fails, don't re-post to platforms that succeeded. Report failure to Telegram with which platform failed and why.

---

## Google Drive Folder Structure

Created programmatically via Google Drive API once credential is available:

```
Trentham Social Media/
├── Solar/
├── Air Conditioning/
├── Electrical/
├── EV Charging/
├── Batteries/
├── Team/
└── General/
```

Agent auto-categorises Telegram uploads based on description keywords. Subfolder IDs stored in Airtable.

---

## Airtable Schema

Five tables within a single Airtable base.

### 1. Master Config Table

| Field | Value (example) |
|-------|-----------------|
| google_drive_folder_id | (root folder ID) |
| post_frequency | 2 |
| post_days | Tuesday, Friday |
| post_time | 09:00 |
| filler_topics | Battery benefits, blackouts, EV charging, solar ROI, energy savings, VEU program |
| last_filler_topic | Battery benefits (tracks rotation to avoid repeats) |
| buffer_profile_ids | (FB profile ID, IG profile ID from Buffer) |
| gbp_location_id | (fetched via API) |
| wix_site_id | (fetched via API) |
| telegram_group_id | (from existing credential) |
| brand_voice_master | (master brand guide text) |
| brand_voice_social | (FB/IG guide text) |
| brand_voice_gbp | (GBP guide text) |
| brand_voice_blog | (blog guide text) |

### 2. Pending Drafts Table

| Field | Purpose |
|-------|---------|
| draft_id | Unique identifier |
| telegram_message_id | For matching replies to drafts |
| trigger_type | telegram / drive / autonomous |
| platforms_requested | Which platforms were requested (e.g. fb_ig, gbp, blog) |
| status_fb_ig | pending / approved / redrafting / skipped / published |
| status_gbp | pending / approved / redrafting / skipped / published |
| status_blog | pending / approved / redrafting / skipped / published |
| content_fb_ig | Generated Facebook/Instagram caption (identical for both) |
| content_gbp | Generated GBP post |
| content_blog | Generated blog post (if applicable) |
| image_url | Google Drive image URL |
| revision_count | Number of redraft cycles |
| created_at | Timestamp |
| published_at | Timestamp |

### 3. Conversation Messages Table

| Field | Purpose |
|-------|---------|
| message_id | Unique identifier |
| draft_id | Linked record to Pending Drafts table |
| telegram_message_id | Telegram's message ID |
| sender | user / agent |
| message_text | Full message content |
| timestamp | When the message was sent |

One row per message. Full thread retrieved by querying all messages for a given draft_id, ordered by timestamp. Passed to Claude on every interaction for conversation context.

### 4. Post History Table

| Field | Purpose |
|-------|---------|
| post_id | Unique identifier |
| draft_id | Linked record to Pending Drafts table |
| platform | fb / ig / gbp / blog |
| content | The published content for this platform |
| image_id | Linked record to Image Library table |
| topic | Topic/theme of the post (e.g. solar ROI, job spotlight) |
| published_at | Timestamp |
| platform_url | Link to the live post (where available) |

One row per platform per publish. A single draft published to FB, IG, and GBP creates three rows. Last 20-30 entries fed into Claude's system prompt so the agent avoids repeating topics, angles, or phrasing.

### 5. Image Library Table

| Field | Purpose |
|-------|---------|
| image_id | Unique identifier |
| google_drive_file_id | File ID in Google Drive |
| google_drive_url | Direct URL to the image |
| folder | Which subfolder (Solar, Air Conditioning, etc.) |
| description | Auto-generated or from Telegram upload description |
| uploaded_at | When the image was added |
| source | telegram_upload / manual / pre-existing |
| used_in_fb | Date last used in a Facebook post (null if never) |
| used_in_ig | Date last used in an Instagram post (null if never) |
| used_in_gbp | Date last used in a GBP post (null if never) |
| used_in_blog | Date last used in a blog post (null if never) |

Populated initially by scanning existing Drive folders. Updated when new photos are uploaded via Telegram or used in published posts. Per-platform usage tracking means an image used on FB/IG can still be selected for a blog post.

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Brand voice doesn't match | High - client rejects all output | Phase 1 quality gate, scrape ALL existing content, iterate guides before building |
| Meta/Buffer API changes | Medium | Buffer abstracts this, but monitor |
| GBP API deprecation | Medium | API currently active, but Google has history of deprecating. Monitor. |
| Wix rich content format | Low | Well documented, just fiddly to build |
| Concurrent draft confusion | Medium | Airtable state tracking + message ID matching |
| n8n instance restart mid-approval | Medium | Airtable holds all state, workflow can resume |
| Airtable API rate limits | Medium | Multiple tables queried per interaction (config, drafts, messages, post history, image library). Airtable allows 5 requests/sec. Cache config at workflow start, batch reads where possible. |
| Claude vision API cost | Low | Sending images to vision API costs more per request. Monitor usage - only send images when present, not on every text-only message. |
| Conversation history token growth | Low | Long redraft threads increase Claude prompt size and cost. Cap at last 20 messages per thread if needed. |
