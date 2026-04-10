# Presentation Brief — Trentham Social Media Agent Walkthrough

**Audience:** Mick Trentham (1-on-1 walkthrough)
**Duration:** 15–30 minutes
**Date:** April 2026

**Purpose of this document:** Structured, fact-verified content for each slide in the presentation deck. Every number, ID, and claim has been verified against the live n8n Cloud instance and Airtable metadata API. Designed to be consumed by another agent for illustration and diagram generation.

---

## Slide 1 — Title

| Field | Value |
|---|---|
| Title | Trentham's Social Media Agent |
| Subtitle | Conversational AI assistant for end-to-end content operations |
| Bot | @TrenthamSocialsV2bot |
| Build | V2 rebuild on n8n Cloud |
| Date | April 2026 |
| Presented by | Leo |
| Presented to | Mick Trentham |

**Diagram suggestion:** Simple cover with Trentham Electrical & Solar branding, phone mockup showing a Telegram chat.

---

## Slide 2 — V1 vs V2 (Why the Pivot)

### V1 Architecture

| Workflow | ID | Total Nodes | IF Nodes | Switch Nodes | Code Nodes |
|---|---|---|---|---|---|
| WF1 Router | `4p3NQbRQpRwCBZzG` | 45 | 14 | 0 | 16 |
| WF2 Social Generator | `3jxUdiGw049BLCVh` | 27 | 1 | 1 | 9 |
| WF3 Blog Generator | `bHoB1SprYKbSjInk` | 25 | 1 | 0 | 5 |
| WF4 Approval Handler | `OykBD1JVgJAK3dcj` | 20 | 3 | 0 | 5 |
| WF5 Q&A | `FEPuOJHELAObLuxD` | 2 | 0 | 0 | 1 |
| WF6 Scheduler | `EDQFZF6vViRvh6gC` | 10 | 1 | 0 | 5 |
| WF7 Publisher | `2suYnYb764NmhtQr` | 23 | 3 | 0 | 6 |
| **TOTAL** | — | **152** | **23** | **1** | **47** |

**V1 Routing pattern:** Every Telegram message hit WF1 Router. 14 IF nodes checked for keywords (e.g., "blog", "delete", "adjust") in the message text to decide which downstream workflow to call. Messages that didn't match any IF branch were not routed anywhere.

**V1 Bot:** @TrenthamSocialsbot (still active as fallback)

### V2 Architecture

| Workflow | ID | Nodes |
|---|---|---|
| SMA-V2 Agent | `joOvKKDolWpOTLdP` | 24 |
| SMA-V2 Social Generator | `eIWk6RjvYP2lgDlI` | 7 |
| SMA-V2 BlogGenerator | `uHELgth7y2dIq3Ft` | 13 |
| SMA-V2 EditDraft | `YZq8YMqeaHxht5Xk` | 2 |
| SMA-V2 Publisher | `RKbtyZ6AMO5sYYjx` | 2 |
| SMA-V2 BufferDelete | `pw1nSD3wci2vCv6u` | 2 |
| SMA-V2 DeleteBlog | `mcHV28IQbqXLG2ZH` | 2 |
| SMA-V2 LookupDrafts | `quswMumV1Ks7UK0B` | 2 |
| SMA-V2 SendTelegram | `fS2F2MiHdiBfAtnB` | 2 |
| SMA-V2 DriveImageSearch | `B9aee5u4h9UTzBcM` | 8 |
| SMA-V2 DriveSearchProxy | `LNNdWgoytdln4Dws` | 2 |
| SMA-V2 ListDriveFolders | `pGYuk5UAzPpRQCsj` | 4 |
| SMA-V2 UploadToDrive | `F93MGaoXeZZoNPyJ` | 5 |
| SMA-V2 WeeklyPlanner | `kGSN5w3lzNsncE37` | 2 |
| SMA-V2 Scheduler | `Ru14lsjNsxNt8R8u` | 3 |
| SMA-V2 BlogSchedulePublisher | `PLMsHfWePzh8XDrh` | 2 |
| SMA-V2 Draft Cleanup | `mO2MRyvyM9zTeKIM` | 2 |
| **TOTAL** | — | **84** |

**V2 Main workflow:** `SMA-V2 Agent` contains a LangChain AI Agent node.
**V2 Model:** `gpt-5.4-mini`, temperature 0.3
**V2 Bot:** @TrenthamSocialsV2bot

**Tools registered on the agent (9):**
1. Lookup Drafts
2. Create Social Post
3. Edit Draft
4. Search Drive
5. Create Blog
6. Publish
7. Plan Weekly
8. Delete Blog
9. DeleteScheduledPosts

The other 8 V2 workflows are internal utilities called by other workflows, not directly by the agent.

**Intent routing in V2:** 0 IF or Switch nodes for user-intent routing anywhere. The agent uses GPT tool-calling to select which sub-workflow to invoke.

### Why V1 was the wrong UX

| Problem | Impact |
|---|---|
| Keyword-based routing via IF nodes | Phrases had to match magic words; "make it punchier" didn't map to "edit" |
| Switch nodes silently drop unmatched cases | Messages could disappear with no reply and no error |
| Edit intent is inherently semantic | "Swap the second image" / "reverse them" / "undo" all look the same to keyword matchers |
| Adding new phrasings meant editing WF1 | Every new feature required editing the 45-node router |
| Cross-workflow debugging | Tracing a single message required checking logs across all 7 workflows |

V1 used AI inside workflows (content generation, image classification) but the *routing layer* — deciding what Mick wanted — was keyword-based. V2 replaces that routing layer entirely with an AI Agent that reads messages in natural language.

### Head-to-Head Comparison

| Metric | V1 | V2 |
|---|---|---|
| Workflows | 7 | 17 |
| Total nodes | 152 | 84 |
| Nodes in routing layer | 45 (WF1) | 0 (agent handles it) |
| Routing IF/Switch nodes | 14 + 1 | 0 |
| Intent classification | Keyword match | GPT tool-calling |
| Bot handle | @TrenthamSocialsbot | @TrenthamSocialsV2bot |

**Diagram suggestion:** Two side-by-side flow diagrams. Left: V1 showing 7 boxes connected via WF1 Router with IF branches fanning out. Right: V2 showing 1 central Agent hexagon surrounded by 9 tool boxes radiating outward.

---

## Slide 3 — Live Airtable Config (Multi-Client Ready)

### Config Table

| Property | Value |
|---|---|
| Base ID | `app3fWPgMxZlPYSgA` (shared with V1) |
| Table name | V2 Config |
| Table ID | `tbleVI4pkVedNuQth` |
| Filter used in workflows | `{active}=TRUE()` |
| Max records per fetch | 1 |

### Complete Field List (29 fields)

| Category | Fields |
|---|---|
| Identity & branding | `client_name`, `active`, `brand_voice`, `website_url` |
| Telegram | `telegram_chat_id`, `telegram_bot_token` |
| Buffer | `buffer_api_key`, `buffer_ig_channel`, `buffer_fb_channel`, `buffer_gbp_channel` |
| Wix | `wix_api_key`, `wix_site_id`, `wix_member_id` |
| OpenAI | `openai_api_key` |
| Drive | `google_drive_folder_id` |
| n8n (for self-update) | `n8n_api_key` |
| Previews | `preview_base_url`, `blog_preview_base_url` |
| Schedule | `post_day`, `post_time`, `posts_per_week`, `blogs_per_week` |
| Content strategy | `scheduled_posts`, `context_required`, `topic_rotation`, `last_topic_index`, `blog_topics`, `last_blog_topic_index` |
| Safety | `crisis_pause` |

### Other V2 Tables in the same base

| Table | ID | Purpose |
|---|---|---|
| V2 Drafts | `tblhwcZsM7wh85HFq` | All drafts with edit history and version snapshots |
| V2 Post History | `tblSEGhWxj3xRHKvC` | Published post log |
| V2 Example Bank | `tblOHBbTZG0cSyeCc` | Real past posts for voice matching |
| V2 Used Images | `tblesyONTANz0axVG` | Drive image usage tracking (rotation) |

### How "live" works

Every workflow starts with a `FetchConfig` step that pulls this row via the Airtable API before running. No redeploys required to change any setting. To onboard a second client, add a second row with their keys and point a separate workflow instance at their row.

**Diagram suggestion:** Airtable row at the top, with arrows fanning down to each V2 workflow showing they all read from the same source on every execution.

---

## Slide 4 — Social vs Blog Pipelines

### Social Generator

| Property | Value |
|---|---|
| Workflow ID | `eIWk6RjvYP2lgDlI` |
| Node count | 7 |
| GPT calls inside workflow | 1 (in `ClassifyFolder` node) |
| Example source table | V2 Example Bank (`tblOHBbTZG0cSyeCc`) |
| Examples per generation | 50 (verified: `slice(0, 50)` in `PreparePrompt`) |
| Outputs | Instagram caption, Facebook caption, GBP caption (3 per run) |

**Key pattern:** Voice is taught through 50 real past posts injected into the prompt as examples, rather than a long rule-based style guide.

### Blog Generator

| Property | Value |
|---|---|
| Workflow ID | `uHELgth7y2dIq3Ft` |
| Node count | 13 |
| GPT calls inside workflow | 1 (in `ClassifyFolder` node) |
| Tables referenced in `AssembleBlogPrompt` | 4 |
| Output | SEO blog post (markdown body, meta description, 4 images) |

**Tables referenced:**

| Table ID | Role |
|---|---|
| `tbldq60sDBBgyGv6y` | V1 table still in use (blog brand guide / examples) |
| `tblnUnX1rLQ8iqgvE` | V1 table still in use (blog brand guide / examples) |
| `tbleVI4pkVedNuQth` | V2 Config |
| `tblhwcZsM7wh85HFq` | V2 Drafts |

**Known state:** Blog Generator still reads from 2 V1 tables for brand guide and blog examples. Works, but not yet fully migrated to V2-only tables.

### Pipeline Comparison

| Aspect | Social | Blog |
|---|---|---|
| Platforms | IG, FB, GBP (3 outputs) | Wix blog (1 output) |
| Length | ~100–300 chars per platform | 900–1200 words |
| Images | 1–5 carousel from Drive | 4 slots (cover, hero, body1, body2) |
| Voice source | 50 shuffled example posts | Brand guide + example blog bank |
| Publish target | Buffer API | Wix Blog v3 API |

**Diagram suggestion:** Two parallel vertical pipelines — Social on the left, Blog on the right — showing input (brief + photos) flowing through Classify → Fetch Examples → Generate → Draft with an emoji or icon at each stage.

---

## Slide 5 — What's Hardcoded (and Why)

### The Single Hardcoded Value

| Property | Value |
|---|---|
| What | Airtable PAT |
| Where | Inside Code nodes as `var PAT = 'patCPDDJo...'` |
| Why | Workflows fetch config from Airtable on every run. The PAT must exist *before* config is loaded — it's the key to unlock the config itself. |

### Affected Code Nodes (12 total)

| Workflow | Code Node |
|---|---|
| SMA-V2 Social Generator | ClassifyFolder |
| SMA-V2 Social Generator | PreparePrompt |
| SMA-V2 Social Generator | PostProcess |
| SMA-V2 BlogGenerator | ClassifyFolder |
| SMA-V2 BlogGenerator | AssembleBlogPrompt |
| SMA-V2 BlogGenerator | SaveAndSend |
| SMA-V2 EditDraft | EditDraft |
| SMA-V2 Publisher | Publish |
| SMA-V2 BlogSchedulePublisher | PublishDueBlogs |
| SMA-V2 Scheduler | BuildInput |
| SMA-V2 WeeklyPlanner | PlanWeek |
| SMA-V2 ListDriveFolders | FetchConfig |

### Everything Else is Now Config-Driven

| Previously hardcoded | Now sourced from |
|---|---|
| Wix site ID | `config.wix_site_id` |
| Wix member ID | `config.wix_member_id` |
| Drive folder ID | `config.google_drive_folder_id` |
| OpenAI API key | `config.openai_api_key` |
| Buffer channels | `config.buffer_ig_channel` / `buffer_fb_channel` / `buffer_gbp_channel` |
| Post day / time | `config.post_day` / `config.post_time` |
| Preview URLs | `config.preview_base_url` / `blog_preview_base_url` |

**Safety rule:** If any of these config fields are missing at runtime, the workflow throws a clear error rather than falling back to a stored default. This prevents one customer's content from publishing to another customer's Wix site.

### Options for Removing the Last Hardcoded Value (post-launch)

| Option | Approach | Tradeoff |
|---|---|---|
| n8n credential store | Register the PAT as a native n8n credential, read via `$credentials` | Cleanest; requires editing 12 Code nodes |
| Environment variable | Set `AIRTABLE_PAT` on the n8n instance, read via `process.env` | Simplest; single update point |
| Router table | Route by `telegram_chat_id` → lookup which base + PAT → fetch config | Needed only for 20+ clients on one n8n instance |

**Diagram suggestion:** A lock icon with the text "1 hardcoded value" and a list of the 12 nodes. Below, three alternative approaches drawn as forks.

---

## Slide 6 — Scheduling Walkthrough

Two independent scheduling systems plus a weekly autonomous planner.

### 1. Buffer Scheduling (Instagram / Facebook / GBP)

| Property | Value |
|---|---|
| Handler | `SMA-V2 Publisher` (`RKbtyZ6AMO5sYYjx`) Code node |
| GPT calls inside | 1 (natural-language schedule parser) |
| Buffer mode | `customScheduled` |
| Key field | `dueAt` (ISO 8601, AEST-aware) |
| Current safety lock | `saveToDraft: true` during testing (must flip to `false` before go-live) |

**Flow:** User replies "Schedule for Wed 3pm" → GPT converts phrase to `2026-04-15T05:00:00Z` → Publisher calls Buffer `createPost` mutation with `mode=customScheduled` and `dueAt=...` → Buffer publishes at the right time across all 3 platforms.

### 2. Wix Blog Scheduling (custom cron)

**Reason this exists:** Wix Blog v3 API does not support native post scheduling. Built our own.

| Property | Value |
|---|---|
| Handler | `SMA-V2 BlogSchedulePublisher` (`PLMsHfWePzh8XDrh`) |
| Trigger type | Schedule Trigger |
| Trigger rule | `{field: hours, hoursInterval: 1}` |
| Cadence | Hourly |
| Published when | `status=scheduled` AND `scheduled_publish_date ≤ now` |
| API used | Wix Blog v3 (`/blog/v3/posts`, `/blog/v3/draft-posts`) |

**Note:** Posts scheduled between hours will publish on the next hour boundary. Can be reduced to every 15 min if needed.

### 3. Weekly Planner (Autonomous Drafts)

| Workflow | ID | Role |
|---|---|---|
| SMA-V2 WeeklyPlanner | `kGSN5w3lzNsncE37` | Generates one draft per bucket |
| SMA-V2 Scheduler | `Ru14lsjNsxNt8R8u` | Cron trigger for the planner |

**Current Scheduler trigger rule (verified from API):**
```
{field: weeks, weeksInterval: 1, triggerAtDay: [0], triggerAtHour: 23, triggerAtMinute: 0}
```

**Dynamic self-update:** `BuildInput` Code node reads `config.post_day` + `config.post_time` on every run, converts AEST to UTC, and if it differs from the current Schedule Trigger values, uses the n8n API to `PUT` the workflow with a new trigger rule. The cron rewrites itself on the fly.

**Planner logic:** 1 GPT call in `PlanWeek`. Reads `config.scheduled_posts` (bucket definitions) and `config.context_required` (skip list). For each auto-generable bucket, calls the Social Generator webhook to produce a draft. Sends drafts to Telegram for review.

### Comparison

| Feature | Buffer Scheduling | Wix Blog Scheduling | Weekly Planner |
|---|---|---|---|
| Trigger mechanism | Natural-language reply | Natural-language reply | Cron |
| Execution | Buffer API (external) | Hourly cron (our code) | Weekly cron (our code) |
| Precision | To the minute | To the hour | To the minute |
| Config-driven | ✓ | ✓ | ✓ (self-updating) |

**Diagram suggestion:** Three lanes — (a) Buffer schedule flow with a clock icon, (b) Wix hourly cron loop, (c) Weekly cron feeding bucket generators.

---

## Slide 7 — Preview Logic

### Social Preview

| Property | Value |
|---|---|
| URL template | `{preview_base_url}?id={draftId}` |
| Current URL | `https://preview-app-amber.vercel.app?id={draftId}` |
| Source | `config.preview_base_url` |
| Hosted on | Vercel |
| Renders | Instagram-style mockup with IG/FB/GBP variants |

### Blog Preview

| Property | Value |
|---|---|
| URL template | `{blog_preview_base_url}/?id={recordId}` |
| Current URL | `https://preview-site-inky.vercel.app/?id={recordId}` |
| Source | `config.blog_preview_base_url` |
| Hosted on | Vercel |
| Renders | Full Wix-styled blog article preview |

### Preview Flow

1. Generator creates draft in V2 Drafts table
2. Generator sends Telegram message: `"Draft ready! Preview: {link}"`
3. User taps link on phone → preview page fetches draft from Airtable by ID on page load
4. User replies to the Telegram message to edit, approve, or publish

**Key point:** Previews are URLs, not images. They always reflect the current state of the draft in Airtable, including after edits.

**Diagram suggestion:** Phone mockup showing a Telegram message with a link, arrow pointing to a browser window showing the rendered preview.

---

## Slide 8a — The Smart Agent (Natural Language)

### Main Agent

| Property | Value |
|---|---|
| Workflow | SMA-V2 Agent (`joOvKKDolWpOTLdP`) |
| Agent node type | `@n8n/n8n-nodes-langchain.agent` |
| Model | `gpt-5.4-mini` |
| Temperature | 0.3 |
| Tools registered | 9 |
| Intent-routing IF/Switch nodes | 0 |

### GPT Calls Embedded Inside Sub-Workflows

| Workflow | Code Node | GPT Calls | Purpose |
|---|---|---|---|
| SMA-V2 Social Generator | ClassifyFolder | 1 | Pick Drive folder from topic |
| SMA-V2 BlogGenerator | ClassifyFolder | 1 | Pick Drive folder from topic |
| SMA-V2 Publisher | Publish | 1 | Natural-language schedule parser |
| SMA-V2 EditDraft | EditDraft | **5** | Image ops, text edits, platform detection, revert, intent classification |
| SMA-V2 WeeklyPlanner | PlanWeek | 1 | Weekly bucket planning |

**EditDraft is the largest Code node in the system** — 45,701 characters of JavaScript containing 5 GPT calls. Features confirmed in the code:

| Feature | Evidence |
|---|---|
| Image op classifier | `operation` + `new_order` JSON schema |
| Reorder support | `reorder` logic branch |
| Versioned revert | `versions` Airtable field + snapshot logic |
| GPT system prompt | Present (verified) |

### Natural Language Examples (Representative)

| User says | Agent does |
|---|---|
| "Write up that heat pump install" | `create_social_post`, bucket = job_spotlight |
| "Make the tone punchier" | `edit_draft`, text edit, all platforms |
| "Swap the second image" | `edit_draft`, image op, slot=2 |
| "Reverse the image order" | `edit_draft`, image op, reorder |
| "Remove GBP from this one" | `edit_draft`, platform removal |
| "Schedule for Wed 3pm" | `publish_post`, scheduled |
| "Undo that" | `edit_draft`, revert |
| "Delete from schedule" | `delete_scheduled_posts` |
| "What's in the queue?" | `lookup_drafts` |

### Reply-Tracking Safety Rule

Every destructive or modifying action (edit, publish, schedule, delete) requires the user to *reply* to a specific draft message in Telegram. Unreplied messages that mention drafts get a clarifying response instead of acting blindly.

**Diagram suggestion:** Chat bubble saying a natural phrase, arrow to a GPT icon, arrow to a tool selection showing which of the 9 tools fires. Contrast with V1 side showing a keyword matching tree.

---

## Slide 8b — Drive Logic

### Folder Discovery

| Property | Value |
|---|---|
| Parent folder source | `config.google_drive_folder_id` |
| Discovery workflow | `SMA-V2 ListDriveFolders` (`pGYuk5UAzPpRQCsj`) |
| Workflow node count | 4 |
| Mechanism | Webhook workflow — `FetchConfig` node reads parent ID from Airtable and returns all live subfolders |

**Effect:** Adding, renaming, or removing a Drive subfolder is picked up on the next generation. Zero code changes required.

### Fuzzy Folder Matching (Verified from Code)

Location: `SMA-V2 DriveImageSearch` (`B9aee5u4h9UTzBcM`), `PickFolder` node.

**Exact scoring logic:**

| Match type | Rule | Score |
|---|---|---|
| Exact match | `name === requestedLower` | 100 |
| Substring | `name.indexOf(requestedLower) >= 0` | 80 |
| Reverse substring | `requestedLower.indexOf(name) >= 0` | 60 |

**Selection:** Picks the subfolder with the highest `bestScore`, returns `{folder_id, folder_name, match_score}`.

### Image Deduplication

| Property | Value |
|---|---|
| Dedup node | `FilterAndReturn` in `SMA-V2 DriveImageSearch` |
| Dedup key | `md5Checksum` (from Drive API) |
| Purpose | Drop physical duplicates (same file content uploaded multiple times) |

### Image Rotation

| Property | Value |
|---|---|
| Rotation table | V2 Used Images (`tblesyONTANz0axVG`) |
| Strategy | LRU — least recently used images surface first |
| Filter | Images used in the last N drafts are excluded from the next generation |

### Drive Logic Summary Table

| Stage | What Happens |
|---|---|
| 1. Discover folders | ListDriveFolders webhook returns live subfolder list |
| 2. Classify topic | GPT picks the best folder name for the current post topic |
| 3. Fuzzy match | PickFolder scores the classification against real folders (100/80/60) |
| 4. Pull images | DriveImageSearch queries the selected folder |
| 5. Dedup | FilterAndReturn removes md5 duplicates |
| 6. Rotate | Used Images table filters out recently-used files |
| 7. Assign | Images get attached to the draft |

**Diagram suggestion:** Funnel shape — wide top showing a Drive folder tree with many subfolders, narrowing through Classify → Fuzzy Match → Dedup → Rotate → final 1–5 selected images at the bottom.

---

## Slide 9 — Getting Started, Caveats, Repo Link

### How to Use

| Step | Action |
|---|---|
| 1 | Open Telegram, message @TrenthamSocialsV2bot |
| 2 | Describe what you want in plain English |
| 3 | Check the preview link sent back |
| 4 | Reply to the draft to edit, schedule, publish, or delete |
| 5 | Weekly drafts arrive automatically on the configured day |

### Current State

| Item | Value |
|---|---|
| Hardcoded values | 1 (Airtable PAT, in 12 Code nodes) |
| Config-driven values | Everything else (29 config fields) |
| Error reporting | `SMA - Error Reporting` (`udKAhf29RLRxVd6T`) wired to all 17 V2 workflows |
| Error recipient | mick@trenthamelectrical.com |

### Known Platform Limits

| Limit | Source | Workaround |
|---|---|---|
| Buffer rate limits | Buffer API key-level quotas (15min and 24hr windows) | Production volume is much lower than test volume; not expected to affect normal use |
| GBP CTA button | Buffer does not support CTA buttons for Google Business Profile posts | None available |
| Wix scheduling granularity | Wix Blog v3 API has no native scheduling | Hourly cron; scheduled blogs publish on the next hour boundary |
| V1 table dependency | Blog Generator reads brand guide + examples from 2 V1 tables | Migrate post-launch |

### Error Workflow Wiring (verified across all 17 V2 workflows)

| Workflow | Error Workflow Set | Active |
|---|---|---|
| All 17 V2 workflows | `udKAhf29RLRxVd6T` | ✓ |

### Repo

Private GitHub repo: `TrenthamSocialMediaAgent` (to be created).
Contents: architecture docs, preview apps, system overview. The n8n workflows themselves live in Mick's n8n Cloud instance — not mirrored here.

**Diagram suggestion:** Three horizontal sections: "Using it" (phone + chat bubble), "Known limits" (warning icons list), "Support" (error alert email icon).

---

## Appendix A — All V2 Workflow IDs

| Workflow | ID | Nodes | Active | Error WF |
|---|---|---|---|---|
| SMA-V2 Agent | `joOvKKDolWpOTLdP` | 24 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 Social Generator | `eIWk6RjvYP2lgDlI` | 7 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 BlogGenerator | `uHELgth7y2dIq3Ft` | 13 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 EditDraft | `YZq8YMqeaHxht5Xk` | 2 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 Publisher | `RKbtyZ6AMO5sYYjx` | 2 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 BufferDelete | `pw1nSD3wci2vCv6u` | 2 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 DeleteBlog | `mcHV28IQbqXLG2ZH` | 2 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 LookupDrafts | `quswMumV1Ks7UK0B` | 2 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 SendTelegram | `fS2F2MiHdiBfAtnB` | 2 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 DriveImageSearch | `B9aee5u4h9UTzBcM` | 8 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 DriveSearchProxy | `LNNdWgoytdln4Dws` | 2 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 ListDriveFolders | `pGYuk5UAzPpRQCsj` | 4 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 UploadToDrive | `F93MGaoXeZZoNPyJ` | 5 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 WeeklyPlanner | `kGSN5w3lzNsncE37` | 2 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 Scheduler | `Ru14lsjNsxNt8R8u` | 3 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 BlogSchedulePublisher | `PLMsHfWePzh8XDrh` | 2 | ✓ | `udKAhf29RLRxVd6T` |
| SMA-V2 Draft Cleanup | `mO2MRyvyM9zTeKIM` | 2 | ✓ | `udKAhf29RLRxVd6T` |

## Appendix B — Verification Method

All facts in this brief were verified from:
- **n8n Cloud API** (`trentham.app.n8n.cloud/api/v1/workflows/{id}`) for node counts, node types, workflow settings, error workflow wiring, trigger rules, and Code node content
- **Airtable Metadata API** (`api.airtable.com/v0/meta/bases/app3fWPgMxZlPYSgA/tables`) for config table field list
- **Direct code inspection** of exported Code node JavaScript for GPT call counts, scoring logic, and embedded behavior

No figures were estimated. If a number is in this document, it came from a live API response or a direct code read.
