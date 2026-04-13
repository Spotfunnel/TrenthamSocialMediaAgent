# Trentham Social Media Agent

Conversational AI assistant for end-to-end social media and blog operations for **Trentham Electrical & Solar**. Built on n8n Cloud with an AI Agent architecture (GPT-5.4-mini) driving 17 tool workflows.

Users interact through Telegram (`@TrenthamSocialsV2bot`) in plain English. No commands, no slash syntax, no magic words.

**If you are an AI agent reading this with zero context, read this entire file before touching anything.** This is the single source of truth for the system architecture, design decisions, dead ends, and rules.

---

## Table of Contents

1. [What It Does](#1-what-it-does)
2. [Stack](#2-stack)
3. [Why V2 Exists (The V1 Problem)](#3-why-v2-exists)
4. [V2 Architecture](#4-v2-architecture)
5. [The Classifier Pattern (Most Important Section)](#5-the-classifier-pattern)
6. [Airtable Schema](#6-airtable-schema)
7. [Social vs Blog Pipelines](#7-social-vs-blog-pipelines)
8. [Scheduling System](#8-scheduling-system)
9. [Drive Image System](#9-drive-image-system)
10. [Preview Apps](#10-preview-apps)
11. [Dead Ends and Mistakes](#11-dead-ends-and-mistakes)
12. [n8n-Specific Traps](#12-n8n-specific-traps)
13. [Hardcoded Values](#13-hardcoded-values)
14. [Rules for Future Work](#14-rules-for-future-work)
15. [Decision History (Why X Over Y)](#15-decision-history)
16. [Message Lifecycle (Full Execution Flow)](#16-message-lifecycle)
17. [How to Extend the System](#17-how-to-extend-the-system)
18. [Testing Evidence and Known Gaps](#18-testing-evidence-and-known-gaps)
19. [Repo Contents](#19-repo-contents)
20. [Operational Reference](#20-operational-reference)

---

## 1. What It Does

- **Create social posts** — IG + FB + GBP (3 platform-specific captions per run, images from Drive)
- **Create blog posts** — 900-1200 word SEO-optimized Wix articles with 4 image slots
- **Edit drafts** — text tone, image swaps/reorders/adds/removes, platform toggles, revert to any prior version — all via natural-language replies to draft messages
- **Schedule posts** — "Schedule for Wed 3pm" → Buffer handles IG/FB/GBP; custom hourly cron handles Wix blogs (Wix API has no native scheduling)
- **Auto-draft weekly** — configurable weekly planner runs on a cron, generates drafts for each content bucket, sends them to Telegram for review
- **Delete from schedule** — pull scheduled posts out of Buffer or unpublish Wix blogs
- **Image management** — browse Drive folders, pick bulk images, swap individual slots, carousel reorder, md5 dedup

---

## 2. Stack

| Layer | Service | Notes |
|---|---|---|
| Orchestration | n8n Cloud (`trentham.app.n8n.cloud`) | All workflows live here. No self-hosted infra. |
| LLM | OpenAI `gpt-5.4-mini` | Temperature 0.3 for agent, 0 for classifiers |
| User interface | Telegram Bot API | `@TrenthamSocialsV2bot`, webhook mode |
| Social publishing | Buffer V2 GraphQL API | `createPost` mutation, `customScheduled` mode for scheduling |
| Blog publishing | Wix Blog v3 API | `/blog/v3/draft-posts` for create, `/blog/v3/posts` for publish |
| Image library | Google Drive API | Parent folder per client, subfolders by topic |
| State | Airtable REST API | 5 tables in base `app3fWPgMxZlPYSgA` |
| Preview pages | Vercel (free tier) | 2 apps: social preview + blog preview |

---

## 3. Why V2 Exists

V1 was 7 chained n8n workflows totaling 152 nodes. It worked, but the routing layer was the problem.

### V1's Architecture

| Workflow | Nodes | IF Nodes | Purpose |
|---|---|---|---|
| WF1 Router | 45 | 14 | Keyword-match every Telegram message to decide which workflow handles it |
| WF2 Social Generator | 27 | 1 | Generate IG/FB/GBP captions |
| WF3 Blog Generator | 25 | 1 | Generate Wix blog posts |
| WF4 Approval Handler | 20 | 3 | Handle edits, approvals, deletions |
| WF5 Q&A | 2 | 0 | Answer questions about drafts |
| WF6 Scheduler | 10 | 1 | Weekly cron for autonomous drafts |
| WF7 Publisher | 23 | 3 | Push to Buffer / Wix |

### What Went Wrong

WF1 Router had 14 IF nodes checking for keywords: if message contains "blog" → blog branch; if "adjust" OR "change" → edit branch; if "delete" → delete branch.

**Problems:**
1. **Phrasing had to match keywords.** "Make it punchier" didn't contain "edit" or "adjust" — the message was silently dropped.
2. **Switch nodes silently dropped unmatched cases.** No error, no reply, nothing.
3. **Edit intent was impossible to keyword-classify.** "Swap the second image", "reverse them", "undo", "remove GBP", "make it shorter" all need completely different handlers but look similar to a keyword matcher.
4. **Every new phrase needed a new IF branch.** Adding support for "write up that job" meant editing the 45-node router, adding another case, reconnecting wires, testing.
5. **Cross-workflow debugging.** Tracing a message required checking execution logs across all 7 workflows.

V1 used AI for content generation but not for routing. V2 replaces the routing layer with an AI Agent.

### V1 Status

V1 is still active (different bot: `@TrenthamSocialsbot`). It stays untouched as a fallback. Same Airtable base, separate tables.

---

## 4. V2 Architecture

**1 main workflow** (`SMA-V2 Agent`) containing a LangChain AI Agent node with 9 tool sub-workflows. 8 additional utility workflows are called internally.

### All 17 V2 Workflows

| Workflow | ID | Nodes | Agent Tool? | Purpose |
|---|---|---|---|---|
| SMA-V2 Agent | `joOvKKDolWpOTLdP` | 24 | — | Main AI agent. Receives Telegram messages, picks the right tool. |
| SMA-V2 Social Generator | `eIWk6RjvYP2lgDlI` | 7 | Yes | Generate IG + FB + GBP captions from a brief |
| SMA-V2 BlogGenerator | `uHELgth7y2dIq3Ft` | 13 | Yes | Generate SEO blog post for Wix |
| SMA-V2 EditDraft | `YZq8YMqeaHxht5Xk` | 2 | Yes | Edit any draft (text, images, platforms, revert) |
| SMA-V2 Publisher | `RKbtyZ6AMO5sYYjx` | 2 | Yes | Publish to Buffer (social) or Wix (blog) |
| SMA-V2 LookupDrafts | `quswMumV1Ks7UK0B` | 2 | Yes | Query drafts by status, type, date |
| SMA-V2 WeeklyPlanner | `kGSN5w3lzNsncE37` | 2 | Yes | Generate one draft per content bucket |
| SMA-V2 DeleteBlog | `mcHV28IQbqXLG2ZH` | 2 | Yes | Delete a blog from Wix |
| DeleteScheduledPosts | `pw1nSD3wci2vCv6u` | 2 | Yes | Delete posts from Buffer schedule |
| SMA-V2 DriveSearchProxy | `LNNdWgoytdln4Dws` | 2 | Yes | Agent-facing proxy to Drive search |
| SMA-V2 SendTelegram | `fS2F2MiHdiBfAtnB` | 2 | No | Send Telegram messages (internal utility) |
| SMA-V2 DriveImageSearch | `B9aee5u4h9UTzBcM` | 8 | No | Search Drive + fuzzy folder match + md5 dedup |
| SMA-V2 ListDriveFolders | `pGYuk5UAzPpRQCsj` | 4 | No | Webhook: return live subfolder list from Drive |
| SMA-V2 UploadToDrive | `F93MGaoXeZZoNPyJ` | 5 | No | Upload Telegram photos to Drive for permanent URLs |
| SMA-V2 Scheduler | `Ru14lsjNsxNt8R8u` | 3 | No | Self-updating weekly cron that triggers WeeklyPlanner |
| SMA-V2 BlogSchedulePublisher | `PLMsHfWePzh8XDrh` | 2 | No | Hourly cron: publishes blogs where `scheduled_publish_date <= now` |
| SMA-V2 Draft Cleanup | `mO2MRyvyM9zTeKIM` | 2 | No | Old draft cleanup |

**Total: 84 nodes across 17 workflows.** All active, all wired to error workflow `udKAhf29RLRxVd6T` (SMA - Error Reporting, emails `mick@trenthamelectrical.com`).

### Agent Configuration

| Property | Value |
|---|---|
| Agent node type | `@n8n/n8n-nodes-langchain.agent` |
| Model | `gpt-5.4-mini` |
| Temperature | 0.3 |
| Tools registered | 9 (listed above) |
| Intent routing IF/Switch nodes | 0 |
| Bot | `@TrenthamSocialsV2bot` |
| Telegram group | `Trenthams SMA - Handover` (chat_id: `-5103631480`) |

### How the Agent Routes

The agent reads the user's plain-English message and picks which tool to call via GPT tool-calling. There are zero IF or Switch nodes for user-intent routing anywhere in V2. Adding a new capability = add a sub-workflow + describe it to the agent in the system prompt.

---

## 5. The Classifier Pattern

**This is the most important architectural pattern in V2. Read this section carefully.**

### The Rule

Every routing decision — what the user wants, which slot to target, whether to use an attached photo or fetch from Drive, whether to revert or edit — goes through a GPT classifier call. **Never use keyword matching, regex, indexOf, or IF nodes to decide user intent.**

### Why This Rule Exists (The History)

EditDraft originally had 3 stacked layers of keyword detection:
1. **Revert detection** — `if (text.indexOf('revert') >= 0 || text.indexOf('restore this') >= 0)`
2. **Image swap detection** — regex for "swap", "change", "replace" + "image", "photo", "cover", "hero"
3. **Platform removal detection** — regex for "remove", "drop", "just", "no" + platform names

Plus 2 regex branches:
4. **pickMatch** — `/pick\s+(\d+)\s+(?:images?|photos?)\s+(?:from\s+)?(\w+)/`
5. **useMatch** — `/(?:image|photo|number|#)\s*(\d+)\s*(?:please|only|just)?/`

**What went wrong on 2026-04-10:**

Mick (the client) said `"swap out body image 1"` in a demo.

- The too-loose useMatch regex (line 5 above) matched "image 1" in "body image 1"
- This hijacked the message into the "select image from batch" branch
- The bot responded "Selected image 1." and did nothing
- The actual swap branch (which correctly fetches from Drive and targets blog slots) was never reached
- This happened during the client handover demo

**The fix:** All 5 keyword layers were ripped out and replaced with a single GPT classifier call. EditDraft went from 52,105 chars to 30,354 chars (−42%). Zero keyword gates remain.

### How the Classifier Works Now

One GPT call at the top of EditDraft. Receives:

```
DRAFT TYPE: social | blog
CURRENT IMAGES: N (4 slots: 1=cover 2=hero 3=body1 4=body2  OR  carousel 1-N)
USER ATTACHED N NEW PHOTO(S)
AVAILABLE DRIVE FOLDERS: Solar, General, Team, ...
INSTRUCTION: <cleaned text with photo URLs stripped>
```

Plus ~30 diverse examples covering every operation.

Returns exactly ONE operation:

| Operation | Extra fields | Purpose |
|---|---|---|
| `revert` | — | Restore snapshot at `replyToMsgId` |
| `reorder` | `new_order: [N]` | Rearrange existing images |
| `add` | `source`, optional `drive_folder` | Add 1 image |
| `add_all` | `source` | Add all attached photos |
| `remove` | `target_index` | Remove one image |
| `replace` | `target_index`, `source`, optional `drive_folder` | Swap one slot |
| `replace_all` | `source` | Replace entire carousel |
| `pick_bulk` | `count`, `drive_folder` | Show batch from folder |
| `use_from_batch` | `target_index` | Pick from displayed batch |
| `platform_remove` | `platforms: ["ig","fb","gbp"]` | Drop platform(s) |
| `text_edit` | — | Edit caption/blog body |
| `none` | — | Fallthrough to text_edit |

Each operation dispatches to a self-contained handler. No fallthrough, no keyword re-checking.

### Blog Slot Mapping

For blog drafts, the classifier maps natural language to 1-indexed positions:

| User says | `target_index` | Slot |
|---|---|---|
| "cover", "cover image" | 1 | Cover |
| "hero", "hero image" | 2 | Hero |
| "body 1", "body image 1", "first body image" | 3 | Body 1 |
| "body 2", "body image 2", "second body image" | 4 | Body 2 |

### Source Detection

| Scenario | `source` |
|---|---|
| User attached photo(s) | `"attached"` |
| User wants a different image but attached nothing | `"drive"` |
| User mentions a specific folder ("use a solar photo") | `"drive"` + `drive_folder: "Solar"` |

### When the Classifier Gets It Wrong

If Mick says something that misroutes, the fix is to **add an example to the classifier prompt** — not to add a keyword check. Each example is one line in the prompt. Deploy takes 30 seconds via the n8n API PUT.

---

## 6. Airtable Schema

**Base:** `app3fWPgMxZlPYSgA` (shared with V1)

### V2 Tables

| Table | ID | Purpose |
|---|---|---|
| V2 Config | `tbleVI4pkVedNuQth` | Per-client configuration (1 row per client) |
| V2 Drafts | `tblhwcZsM7wh85HFq` | All drafts with edit history and version snapshots |
| V2 Post History | `tblSEGhWxj3xRHKvC` | Published post log |
| V2 Example Bank | `tblOHBbTZG0cSyeCc` | Real past posts for voice matching (50 per generation) |
| V2 Used Images | `tblesyONTANz0axVG` | Drive image usage tracking for rotation |

### V2 Config Fields (29 total)

| Category | Fields |
|---|---|
| Identity | `client_name`, `active`, `brand_voice`, `website_url` |
| Telegram | `telegram_chat_id`, `telegram_bot_token` |
| Buffer | `buffer_api_key`, `buffer_ig_channel`, `buffer_fb_channel`, `buffer_gbp_channel` |
| Wix | `wix_api_key`, `wix_site_id`, `wix_member_id` |
| OpenAI | `openai_api_key` |
| Drive | `google_drive_folder_id` |
| n8n | `n8n_api_key` (for Scheduler self-update) |
| Previews | `preview_base_url`, `blog_preview_base_url` |
| Schedule | `post_day`, `post_time`, `posts_per_week`, `blogs_per_week` |
| Content | `scheduled_posts`, `context_required`, `topic_rotation`, `last_topic_index`, `blog_topics`, `last_blog_topic_index` |
| Safety | `crisis_pause` |

### How Config is Loaded

Every Code node starts with:
```js
var configResp = await this.helpers.httpRequest({
  method: 'GET',
  url: 'https://api.airtable.com/v0/' + BASE + '/tbleVI4pkVedNuQth',
  qs: { filterByFormula: "{active}=TRUE()", maxRecords: 1 },
  headers: { 'Authorization': 'Bearer ' + PAT }
});
config = (configResp.records || [])[0].fields || {};
```

Change any field in Airtable → the next workflow execution picks it up. No redeploys.

### Access Control

`V2 Load Config` in the main Agent workflow filters by `{telegram_chat_id}='{chatId}'`. Messages from chats that don't match any config row get `client_not_found` and zero response. This is also the multi-tenant routing mechanism — onboard a second client by adding their row.

---

## 7. Social vs Blog Pipelines

### Social Generator (`eIWk6RjvYP2lgDlI`, 7 nodes)

- Input: brief + optional photos
- GPT call in `ClassifyFolder`: picks Drive folder from topic (using live folder list)
- `PreparePrompt`: pulls 50 examples from V2 Example Bank via `slice(0, 50)`, shuffles them
- Generates 3 outputs: Instagram (hashtags + emojis), Facebook (longer, fewer hashtags), GBP (professional)
- Images selected from Drive folder via DriveImageSearch (LRU rotation, md5 dedup)

**Voice matching strategy:** 50 real past posts injected as examples beats a long style guide. Rules flatten voice into generic corporate-AI; examples teach the actual human voice.

### Blog Generator (`uHELgth7y2dIq3Ft`, 13 nodes)

- Input: topic idea + optional keywords/photos
- GPT call in `ClassifyFolder`: picks Drive folder
- `AssembleBlogPrompt`: references brand guide + blog examples (still from 2 V1 tables: `tbldq60sDBBgyGv6y`, `tblnUnX1rLQ8iqgvE`)
- Output: 900-1200 word article, meta description, focus keyword, alt text per image
- 4 image slots: cover, hero, body 1, body 2

---

## 8. Scheduling System

### Buffer Scheduling (IG / FB / GBP)

Publisher Code node contains a GPT call that converts natural language ("Wed 3pm", "next Thursday 5pm AEST") to an ISO 8601 `dueAt` timestamp. Posts are sent to Buffer with `mode: customScheduled`. Buffer handles the actual timed publishing.

### Wix Blog Scheduling

Wix Blog v3 API has no native scheduling. Custom solution:
1. Publisher stores `status=scheduled` + `scheduled_publish_date` on the draft
2. `SMA-V2 BlogSchedulePublisher` runs every hour (`{field: hours, hoursInterval: 1}`)
3. Each run: finds drafts where `status=scheduled AND scheduled_publish_date <= now`
4. Publishes via Wix API, updates status to `published`

Blog publish times round up to the next hour boundary.

### Dynamic Scheduler

`SMA-V2 Scheduler` reads `config.post_day` + `config.post_time` on every run. If config has changed since the last run, it uses the n8n API to `PUT` its own workflow with a new Schedule Trigger rule. Change `post_day` from "Monday" to "Thursday" in Airtable → next run, the Scheduler rewrites itself.

---

## 9. Drive Image System

### Folder Structure

One parent folder per client (from `config.google_drive_folder_id`). Inside: subfolders by topic (Solar, Heat Pump, EV Chargers, Team, etc.). The client adds/renames/deletes subfolders — no code changes needed.

### Live Folder Discovery

`SMA-V2 ListDriveFolders` webhook returns the current subfolder list. Called every time a generator or editor needs to pick a folder. New folders are usable immediately.

### Fuzzy Folder Matching

`PickFolder` node in DriveImageSearch scores folder name matches:
- Exact match → score 100
- Substring match (`name.indexOf(requested) >= 0`) → score 80
- Reverse substring (`requested.indexOf(name) >= 0`) → score 60
- Picks highest score

### Image Rotation

`V2 Used Images` table tracks which Drive file IDs were used in which drafts. Next generation filters out recently-used images (LRU). If all images in a folder have been used recently, falls back to oldest first.

### Duplicate Protection

`FilterAndReturn` in DriveImageSearch dedups by `md5Checksum` from the Drive API. Same file content uploaded from multiple devices → only one copy used.

---

## 10. Preview Apps

Both hosted on Vercel (free tier). URLs stored in config so they're swappable per client.

| App | URL Pattern | Renders |
|---|---|---|
| Social preview | `{preview_base_url}?id={draftId}` | IG-style carousel mockup + FB + GBP tabs |
| Blog preview | `{blog_preview_base_url}/?id={recordId}` | Full Wix-styled blog article |

Preview pages fetch the draft from Airtable by ID on page load. They always reflect the current draft state, including after edits.

The preview URL is included in every Telegram draft message. The user taps the link on their phone to see the draft before approving.

---

## 11. Dead Ends and Mistakes

### Keyword Routing (V1 and early V2)

V1 used 14 IF nodes to route by keyword. This was the reason V2 was built. But early V2 still had keyword routing inside EditDraft (revert detection, image swap detection, useMatch regexes). These were the source of the worst bugs — "swap out body image 1" → "Selected image 1" during the client demo. **Lesson: never use keyword matching for intent routing when an LLM is available.**

### Switch Nodes

n8n's Switch node silently drops messages that don't match any case. No error, no log. V1 used them; V2 avoids them entirely. **Lesson: Switch nodes are a silent failure factory.**

### Code Tools (`toolCode`) Inside AI Agents

n8n's `toolCode` node type (inline JavaScript as an agent tool) looks convenient but `this.helpers.httpRequest` fails silently inside them. The agent gets no tool output and loops. **Lesson: always use `toolWorkflow` (a separate sub-workflow) instead of `toolCode`.**

### Buffer Memory Poisoning

If the AI Agent enters a bad reasoning loop, n8n's buffer memory feeds the bad output back as context on every subsequent message. The agent gets stuck repeating the same mistake. **Lesson: use fresh session keys or disable memory entirely.**

### Hardcoded Customer IDs

Early V2 had Wix site IDs, Drive folder IDs, and Buffer channel IDs hardcoded in Code nodes. If a second client was onboarded with wrong IDs, content would publish to the wrong Wix site silently. All values were moved to Airtable config. If a config field is missing, the workflow throws an error rather than falling back to a hardcoded default. **Lesson: better to fail loudly than publish to the wrong account.**

### `saveToDraft: false` Accident

During heavy testing, `saveToDraft` was set to `false` (live publish) and test posts leaked to Mick's real Facebook and Instagram. Multiple copies of the same draft published because a syntax error in the Publisher prevented status updates. **Lesson: lock `saveToDraft: true` during all automated testing; flip to `false` only for go-live.**

### Buffer Rate Limits

Buffer's V2 GraphQL API has key-level rate limits: 15-minute and 24-hour windows. Heavy stress testing burned through the quota and blocked all Buffer operations for 24 hours. **Lesson: never run parallel automated tests that hit Buffer. Test one at a time.**

### Too-Loose Regex

The regex `/(?:image|photo|number|#)\s*(\d+)/` was meant to catch "use image 3" after displaying a batch. It also matched "body image 1" inside any message. This caused "swap out body image 1" to silently misroute during the client demo. **Lesson: don't use regex for intent classification. Use the classifier.**

### Drive Thumbnails

During development, 10 low-resolution thumbnails were accidentally uploaded to Drive. The image selection pipeline started grabbing them for posts. Fix: delete them from Drive. The pipeline pulls from Drive as truth — garbage in, garbage out. **Lesson: keep the Drive image library clean.**

### Media Group Race Condition

Telegram sends each photo in a multi-photo message as a separate webhook event with a shared `media_group_id`. Without a gate, each photo triggers a separate full workflow execution. Fix: `MediaGroupGate` node waits ~1.5s to collect all events in the same media group before proceeding. **Lesson: Telegram media groups are not atomic; you must dedup and batch.**

---

## 12. n8n-Specific Traps

These are hard-won lessons. Each one cost debugging time.

| Trap | What Happens | Solution |
|---|---|---|
| `toolCode` inside AI Agent | `this.helpers.httpRequest` fails silently | Use `toolWorkflow` sub-workflows |
| Switch node unmatched case | Message silently dropped, no error | Use IF chains or push routing into GPT |
| Buffer memory poisoning | Agent loops on its own bad output | Fresh session keys or disable memory |
| `$fromAI` input format | Sub-workflow receives `{query: "..."}`, not named fields | Always read from `input.query \|\| input.brief \|\| ''` |
| Node names with spaces | Telegram webhook URLs break | Use camelCase: `TelegramTriggerV2` not `V2 Telegram Trigger` |
| Duplicate node names | n8n resolves connections by name; duplicates corrupt routing | Always unique names |
| `returnIntermediateSteps` | May break tool observation relay in AI Agent | Test with it off first |
| Sub-workflow must be active | `executeWorkflow` fails silently on inactive targets | Always verify target is active |

---

## 13. Hardcoded Values

### What's Hardcoded

Only the Airtable PAT: `patCPDDJo1eNTzzO5...`

It appears in **12 Code nodes** across: SocialGen (3), BlogGen (3), EditDraft (1), Publisher (1), BlogSchedulePublisher (1), Scheduler (1), WeeklyPlanner (1), ListDriveFolders (1).

### Why

Workflows fetch config from Airtable. To fetch config, they need the PAT. But the PAT can't live in the config it's trying to fetch. This is the chicken-and-egg bootstrap problem.

### Post-Launch Options

| Option | Approach |
|---|---|
| n8n credential store | Register PAT as a native credential, read via `$credentials` |
| Environment variable | Set `AIRTABLE_PAT` on the instance, read via `process.env` |
| Multi-tenant router | Route by `telegram_chat_id` → lookup which base + PAT to use |

### Everything Else is Config-Driven

All other credentials (OpenAI key, Buffer key, Wix key, Drive folder ID, Telegram bot token, Buffer channels, Wix site/member IDs) are read from the Airtable config row at runtime. Change them in Airtable; next execution picks them up.

---

## 14. Rules for Future Work

These are non-negotiable project conventions.

### 1. No keyword routing for intent

Every intent decision goes through a GPT classifier. No `indexOf`, no regex, no IF chains for user intent. If a phrasing misroutes, add an example to the classifier prompt — don't add a keyword check. See [Section 5](#5-the-classifier-pattern).

### 2. No hardcoded customer values

Every customer-specific value comes from `V2 Config`. If a field is missing at runtime, throw an error. Never fall back to a hardcoded default — that's how one customer's content publishes to another customer's account.

### 3. Never publish to Buffer during testing

`saveToDraft` is currently `false` (live). Do NOT call the `publish_post` tool or Publisher workflow during automated tests unless the client explicitly approves. Blog publishing to Wix is OK for testing but delete immediately after inspection.

### 4. Verify every fact against a live source

When writing docs, reports, or presentations, every number must come from an API response or a grep result. No estimates, no "approximately", no dramatization. If you can't verify it, don't write it.

### 5. Examples over rules for voice

The Social Generator uses 50 real past posts as examples, not a detailed style guide. Rules flatten voice into generic corporate-AI; examples teach the actual human patterns. Don't replace the examples with a rule-based prompt.

---

## 15. Decision History

Every major design choice had a reason. Another agent touching this system needs to understand not just what was built, but what was tried and rejected.

### Why n8n Cloud Over Railway / Self-Hosted

The client (Mick) wanted a visual workflow builder he could inspect, not a code-deployed backend. n8n's canvas UI lets him see the flow, check execution logs, and understand what the system is doing. Railway would have been faster to build on and cheaper to run, but it would have been a black box to the client. n8n Cloud was chosen over self-hosted n8n because Mick doesn't want to maintain infrastructure.

### Why Buffer Over Meta Graph API

Meta's Graph API requires separate OAuth flows per platform, doesn't support Google Business Profile, and requires an approved Facebook App with Business Verification for publishing. Buffer's API handles IG + FB + GBP from a single API key with a single `createPost` GraphQL mutation. The tradeoff: Buffer doesn't support CTA buttons on GBP posts, and its rate limits are strict (15-min and 24-hour windows at the key level). We accepted both tradeoffs because Buffer cut integration time from weeks to hours.

### Why GPT-5.4-mini Over Claude

The client already had an OpenAI API key and preferred it. When GPT-4o was retired, gpt-5.4-mini was the replacement — 400K context window, $0.20-0.55/month in projected usage at Mick's volume. Claude was considered but would have required a separate API key and billing relationship. The system is model-agnostic in principle (the model name is just a string in the Code nodes), but switching would require editing the `model` field in every GPT call across 7 Code nodes.

### Why Examples Over Prompt Rules for Voice Matching

Both approaches were tested. A 500-line style guide ("be professional, use Australian English, avoid corporate speak, include relevant emojis, use 3-5 hashtags...") produced output that sounded like every other AI-generated social media post — correct but generic. Injecting 50 real posts from Mick's Facebook page as examples (shuffled to avoid recency bias) produced output that matched his actual voice — the sentence structures, the emoji placement, the way he talks about jobs. The `PreparePrompt` node in Social Generator does `slice(0, 50)` on the shuffled Example Bank. Adding more examples or changing voice = update the Airtable table, not the prompt.

### Why No Agent Memory (Buffer Memory Disabled)

n8n's AI Agent supports buffer memory (conversation history). It was enabled early in V2 development. During testing, the agent entered a bad reasoning loop — it hallucinated a tool call, got an error back, and then on every subsequent message, the buffer memory fed the bad reasoning back as context, reinforcing the loop. The agent got stuck repeating the same wrong tool call indefinitely. Clearing the memory fixed it, but the risk of poisoning was too high for a production system where Mick might not notice for days. Memory was disabled. If re-enabled, use a fresh session key per conversation or implement a sliding window that drops old turns.

### Why a Separate Error Workflow

The n8n instance had an existing error workflow ("Steve's Error Reporting") that emailed `steve@...`. Wiring V2 workflows to it would have sent Mick's errors to Steve. A new workflow `SMA - Error Reporting` (`udKAhf29RLRxVd6T`) was created — identical logic but emails `mick@trenthamelectrical.com`. All 17 V2 workflows have `settings.errorWorkflow` set to this ID.

### Why Wix Blog Scheduling is a Custom Cron

Wix Blog v3 API supports `createDraftPost` and `publishDraftPost` but has no `scheduleDraftPost` endpoint. There is no way to tell Wix "publish this at 3pm Thursday." The solution: the Publisher stores `status=scheduled` + `scheduled_publish_date` on the Airtable draft, and a separate hourly cron (`SMA-V2 BlogSchedulePublisher`) checks for due posts and publishes them. This means blog publish times round up to the next hour boundary. The cron interval can be reduced to 15 minutes if more precision is needed.

### Why the Dynamic Self-Updating Scheduler

The weekly planner needs to run at a specific day and time (e.g., Monday 6pm AEST). Hardcoding the cron means editing the workflow if Mick wants to change his posting day. The Scheduler workflow reads `config.post_day` and `config.post_time` on every run. If the config values differ from the current Schedule Trigger settings, it uses the n8n API to `PUT` its own workflow JSON with a new trigger rule. Mick changes `post_day` from "Monday" to "Thursday" in Airtable → next run, the Scheduler rewrites itself → now fires Thursdays. Zero workflow edits.

---

## 16. Message Lifecycle

This is the step-by-step execution flow for every message Mick sends.

### Text Message (No Photos)

```
TelegramTriggerV2
  ↓ (raw Telegram Update JSON)
MediaGroupGate
  ↓ (checks media_group_id — none for text, passes through)
SkipGate (IF node)
  ↓ (no photo → skip photo branch)
V2 Load Config
  ↓ (fetches Airtable config row matching incoming chat_id)
  ↓ (outputs: config object, message_text, chat_id, message_id,
  ↓  is_reply, reply_to_message_id, has_photo=false, from_name)
V2 InjectReplyId
  ↓ (if is_reply, appends [DRAFT_MSG:{reply_to_message_id}] to message_text)
V2 Agent (LangChain AI Agent)
  ↓ (reads system prompt + message, picks tool via GPT tool-calling)
  ↓ (calls one of 9 sub-workflows as toolWorkflow)
  ↓ (sub-workflow does work, sends Telegram message, returns "DONE")
V2 Always Reply
  ↓ (if agent output = "DONE" → skip, tool already replied)
  ↓ (if agent output is text → send to Telegram as the response)
  ↓ (if empty → skip)
```

### Photo Message (Single or Multi-Photo)

```
TelegramTriggerV2
  ↓ (Telegram sends one webhook per photo, each with media_group_id)
MediaGroupGate
  ↓ (stores photo_file_id to Airtable buffer table, keyed by media_group_id)
  ↓ (first photo in group: passes through with is_first=true)
  ↓ (subsequent photos: stored but execution stops — SkipGate catches them)
SkipGate (IF node)
  ↓ (is_first=true → continue; is_secondary=true → NoOp, stop)
PhotoGate (IF node)
  ↓ (has photo → Wait5s, then ResolvePhotos)
  ↓ (no photo → V2 Load Config directly)
Wait5s
  ↓ (waits 1.5 seconds for remaining media group photos to arrive in buffer)
ResolvePhotos
  ↓ (reads all buffered photos for this media_group_id from Airtable)
  ↓ (downloads each from Telegram API using bot token)
  ↓ (uploads each to Google Drive via upload-to-drive webhook)
  ↓ (outputs resolved_image_url: comma-separated Drive URLs)
  ↓ (clears the buffer)
V2 Load Config
  ↓ (same as text flow, but now has resolved_image_url)
V2 InjectReplyId
  ↓ (appends [PHOTOS:url1,url2,...] to message text)
V2 Agent → tool → Always Reply (same as text flow)
```

### Cron-Triggered (Weekly Planner)

```
V2ScheduleTrigger (Schedule Trigger node)
  ↓ (fires on configured day/time — currently weekly)
V2 Cron Input (Code node)
  ↓ (reads config, builds a synthetic input matching the agent's expected shape)
  ↓ (message_text: "plan_weekly_posts", chat_id from config)
  ↓ (also runs self-update: checks if config.post_day/post_time changed,
  ↓  PUTs own workflow with new trigger if different)
V2 Agent → V2 Plan Weekly tool → sends drafts to Telegram
```

### Key Node Behaviors

**V2 Load Config** — Acts as both config fetcher AND access control. Filters by `{telegram_chat_id}='{chatId}'`. No matching row = `client_not_found`, execution effectively stops. This is why random users who find the bot get silence.

**V2 InjectReplyId** — When Mick replies to a draft message, Telegram includes `reply_to_message.message_id`. This node appends `[DRAFT_MSG:{id}]` to the message text so sub-workflows can find the target draft. This tag must be passed through verbatim by the agent — the system prompt explicitly says `PRESERVE TAGS`.

**V2 Always Reply** — The "catch-all" response node. If a tool sub-workflow already sent a Telegram message (returned "DONE"), this node skips. If the agent produced conversational text (for greetings, questions, capability queries), this node sends it. If the agent produced nothing, this node skips. Response codes: `{sent: true, message_id: N}` (sent conversational reply), `{sent: false, reason: "tool_sent"}` (tool handled it), `{sent: false, reason: "empty"}` (nothing to send).

### Reply Tracking System (How the Bot Knows Which Draft to Edit)

Every time a sub-workflow sends a Telegram message about a draft (creation confirmation, edit confirmation, preview link), it appends the new Telegram `message_id` to the draft's `telegram_message_id` field in Airtable. This field is a comma-separated list of all Telegram messages associated with that draft.

When Mick replies to any of those messages and says "make it shorter", the agent receives `reply_to_message.message_id` from Telegram, which InjectReplyId turns into `[DRAFT_MSG:123]`. EditDraft then searches V2 Drafts for any record where `FIND('123', {telegram_message_id}) > 0` — finding the draft regardless of which specific message in the chain Mick replied to.

### Versioned Revert System

Before every edit, EditDraft saves a snapshot of the current draft state under `versions[replyToMsgId]`:
- Blog snapshot: `{ content_blog, image_url }`
- Social snapshot: `{ content_ig, content_fb, content_gbp, image_url, platforms }`

The `versions` field is a JSON object keyed by Telegram message ID. Each key represents "what the draft looked like when this message was the latest." When Mick replies to an older message and says "revert to this version", EditDraft reads `versions[replyToMsgId]` and PATCHes the draft back to that state.

This means Mick can reply to any past draft message in the Telegram thread — even one from 5 edits ago — and revert to the exact state at that point. He doesn't need to "undo" sequentially.

---

## 17. How to Extend the System

### Adding a New Agent Tool

1. **Create a sub-workflow** in n8n with a `Execute Workflow Trigger` node and a Code node
2. The Code node receives `{ query: "..." }` from the agent — parse with `var input = $input.first().json; var instruction = input.query || '';`
3. The Code node must return `[{ json: { response: "DONE" } }]` when it sends its own Telegram message, or `[{ json: { response: "some data" } }]` for the agent to relay
4. **Register it on the agent** — add a `toolWorkflow` node in the main Agent workflow, point it at the sub-workflow, write a `description` that tells the agent when to use it
5. **Activate the sub-workflow** — inactive workflows fail silently when called via `executeWorkflow`
6. **Test via the test webhook** — POST to `https://trentham.app.n8n.cloud/webhook/sma-v2-agent` with a Telegram-shaped body

### Deploying a Code Node Change

Workflows live in n8n Cloud. There's no git-based deploy pipeline. Changes are made via the n8n REST API:

```python
# 1. Fetch current workflow
GET /api/v1/workflows/{workflowId}
# 2. Parse JSON, find the target node by name, edit parameters.jsCode
# 3. PUT the full workflow back
PUT /api/v1/workflows/{workflowId}
body: { name, nodes, connections, settings }
```

**For the main Agent workflow:** PUT without deactivating — deactivating drops the Telegram webhook registration, and re-registering requires re-auth.

**For sub-workflows:** Can safely deactivate → PUT → reactivate if needed.

**Always syntax-check before deploying:**
```python
with open("check.js", "w") as f:
    f.write("(async function(){\n" + code + "\n})();")
subprocess.run(["node", "-c", "check.js"])
```

### Adding a Classifier Example

When a user phrasing misroutes (e.g., "swap out body image 1" was classified as `use_from_batch` instead of `replace`), the fix is to add one line to the classifier's user prompt examples:

```
'"swap out body image 1" with 0 attached → {"operation":"replace","target_index":3,"source":"drive"}'
```

Then redeploy the EditDraft Code node via the API. Takes 30 seconds.

**Do NOT add a keyword check instead.** See [Section 5](#5-the-classifier-pattern) and [Section 14 Rule 1](#14-rules-for-future-work).

### The `$fromAI` Input Shape

When the agent calls a `toolWorkflow`, the sub-workflow's trigger receives the input wrapped as `{ query: "user's message" }`. Not named parameters, not structured fields. Every sub-workflow must parse from:

```js
var input = $input.first().json;
var body = input.body || input;
var instruction = body.query || body.brief || input.query || input.brief || '';
```

This triple-fallback pattern exists because the webhook trigger and the executeWorkflow trigger produce slightly different JSON shapes.

### The Ricos Content Format (Wix Blogs)

Wix's blog editor uses Ricos — a rich content JSON format. The blog body in Airtable's `content_blog` field is stored as a JSON string with structure:

```json
{
  "title": "...",
  "body": "## Heading\n\nParagraph text...",
  "meta_description": "...",
  "focus_keyword": "...",
  "tags": ["solar", "energy"],
  "cover_image_alt": "..."
}
```

The Publisher Code node converts the markdown `body` into Ricos nodes (paragraphs, headings, images) for the Wix API. The conversion happens inside the Publisher — generators just write markdown.

---

## 18. Testing Evidence and Known Gaps

### What Was Tested (Automated)

**24-case subset** (fake chat_id, read-only): 24/24 HTTP complete, 30 recent n8n agent executions all success, 0 errors.

**50-case unique edge case run** (real group chat `-5103631480`): 50/50 HTTP complete. 32 workflow successes, 18 OpenAI 429 rate limits (parallel testing artifact, not a production issue). 0 real bugs.

Categories covered: 8 creates (varied angles/constraints), 5 lookups (temporal/status/platform/aggregation filters), 5 drive queries (metadata/filename/cross-folder), 5 schedule parse edge cases (past/invalid/ambiguous), 3 edits without reply context, 4 multi-intent compounds, 5 system/meta introspection, 5 hostile/security (prompt injection/secret extraction/persona attack), 5 format variants (abbreviations/caps/punctuation/French), 3 delete scopes, 2 planner variants.

Full results: `docs/v2-stress-test-50-unique.md` and `docs/v2-stress-test-results.md`

### What Was NOT Tested (Requires Manual Sequencing)

These tests require human-in-the-loop sequencing because they depend on reply context:

| Test | Why Manual |
|---|---|
| Create → edit text → edit image → revert chain | Each step requires replying to the previous bot message |
| Multi-version revert (reply to message from 3 edits ago) | Requires a real conversation thread with multiple bot responses |
| Buffer delete (remove from schedule) | Was blocked by 24-hour Buffer rate limit during testing |
| Blog schedule → hourly cron publish → verify on Wix | Requires waiting for the hourly cron to fire |
| Carousel bulk pick → "use image 3" selection flow | Requires two-turn conversation |

### Known Failure Modes

| Condition | What Happens | Severity |
|---|---|---|
| 6+ concurrent agent calls | OpenAI 429 rate limit, workflow returns `{"message":"Error in workflow"}` | Low — only happens in parallel testing, not real usage |
| Buffer heavy testing | 24-hour key-level rate limit blocks all Buffer operations | Medium — clears after 24 hours |
| Agent memory poisoning | Agent loops on bad reasoning if buffer memory is enabled | Avoided — memory is disabled |
| Telegram media group with >10 photos | Untested — buffer table may not collect all before gate releases | Low — Mick rarely sends >5 photos |
| Drive folder with 0 images | `fetchDriveImage` returns empty string, replace fails gracefully with "Could not find a replacement" message | Low |

### Error Monitoring

All 17 V2 workflows are wired to `SMA - Error Reporting` (`udKAhf29RLRxVd6T`). Any workflow error triggers an email to `mick@trenthamelectrical.com` with the error details and workflow name. Verified via n8n API that all 17 have `settings.errorWorkflow` = `udKAhf29RLRxVd6T`.

---

## 19. Repo Contents

| Path | What's in it |
|---|---|
| `README.md` | This file — full system context for zero-context agents |
| `CLAUDE.md` | Operational quick-reference (workflow IDs, deploy patterns, n8n patterns) |
| `docs/` | Session logs, stress test plans/results, presentation brief, architecture docs |
| `docs/presentation-brief.md` | Fact-verified 9-slide brief for client walkthrough |
| `docs/session-log-2026-04-10-handover.md` | Full handover session log (the most recent comprehensive record) |
| `docs/v2-stress-test-100.md` | 100-case edge case plan |
| `docs/v2-stress-test-50-unique.md` | 50-case real-chat stress test results |
| `brand-guides/` | Brand voice guides and LLM prompt templates |
| `preview-app/`, `v2-preview-app/` | Social post preview app (Vercel) |
| `preview-site/` | Blog post preview site (Vercel) |

### What's NOT in This Repo

- **n8n workflows** — they live in the client's n8n Cloud instance (`trentham.app.n8n.cloud`)
- **Deploy scripts** (`scripts/`) — throwaway Python/JS files used to push code into n8n during development. All contain hardcoded API keys from rapid iteration. Gitignored.
- **Screenshots and test data** — large binary files, gitignored

---

## 20. Operational Reference

For quick-reference IDs, deploy patterns, and n8n conventions, see `CLAUDE.md`. It is auto-loaded by Claude Code at session start.

### Key IDs (for quick lookup)

| Resource | ID |
|---|---|
| n8n Cloud | `trentham.app.n8n.cloud` |
| Airtable base | `app3fWPgMxZlPYSgA` |
| V2 Config table | `tbleVI4pkVedNuQth` |
| V2 Drafts table | `tblhwcZsM7wh85HFq` |
| V2 Example Bank table | `tblOHBbTZG0cSyeCc` |
| Main Agent workflow | `joOvKKDolWpOTLdP` |
| EditDraft workflow | `YZq8YMqeaHxht5Xk` |
| Publisher workflow | `RKbtyZ6AMO5sYYjx` |
| Error reporting workflow | `udKAhf29RLRxVd6T` |
| Telegram group chat_id | `-5103631480` |
| GitHub repo | `Spotfunnel/TrenthamSocialMediaAgent` (private) |
