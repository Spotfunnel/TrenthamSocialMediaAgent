# V2 Session Report — April 10, 2026

## Test Results Summary

### Automated Tests (Playwright via Telegram)
| Test | Status | Notes |
|------|--------|-------|
| Post creation (social) | ✓ PASSED | Draft created with IG/FB/GBP content, auto-classified images |
| Carousel post creation (3 photos) | ✓ PASSED | "Kyneton Solar, Done Right" with 3-image carousel |
| Blog creation | ✓ PASSED | Solar maintenance blog, 940 words, 4 images, SEO validated |
| Buffer scheduling (IG + FB + GBP) | ✓ PASSED | Wed 3pm + Thu 5pm, all 3 platforms, clean confirmation message |
| Reply tracking enforcement | ✓ PASSED | Direct messages without reply get "Which draft?" response |
| **Image reorder (reverse)** | ✓ PASSED | "reverse the image order" correctly reversed 3 images |
| **Live Drive folder list** | ✓ PASSED | `list-drive-folders` webhook returns 10 real folders dynamically |
| Schedule parsing (AEST) | ✓ PASSED | "Wednesday 3pm" → `2026-04-15T05:00:00Z` correctly |
| Telegram "Scheduled" message | ✓ PASSED | "Scheduled for Wednesday 15 Apr at 3pm AEST! Instagram: OK..." |
| Platform-specific post creation | ✓ PASSED | "Create an IG post" → only IG (tested previously) |

### Requires Manual Testing (Code deployed, Playwright can't reliably reproduce)
| Test | Status | Blocker |
|------|--------|---------|
| Revert/undo | ⏳ Code deployed | Previous edits saved to `previous_version`; Playwright kept targeting wrong message in cluttered chat. **Action**: Reply to a recent edit confirmation with "undo" |
| Swap second image | ⏳ Code deployed | `detectSlot()` now handles ordinals ("second body image"). **Action**: Reply to a carousel/blog draft with "swap the second image" |
| Buffer delete | ⏳ Code deployed | `SMA-V2 BufferDelete` workflow + agent tool wired. **Action**: Schedule a post, then reply with "delete from schedule" |
| Wix blog scheduling | ⏳ Code deployed | Publisher saves `status: 'scheduled'` + cron publishes when due. **Action**: Reply to blog draft with "schedule for Wednesday 10am" |

---

## What was fixed this session

### Critical Fixes
1. **Publisher syntax error** — Ricos builder functions inside `try` block + orphaned `{` block caused "Unexpected token 'catch'". Moved functions outside `try`, fixed brace nesting.
2. **Social Generator PostProcess syntax error** — Stray `var` keyword prepended to a comment on line 181.
3. **Buffer posts leaked to live during testing** — Test posts auto-published via Buffer queue. Root cause: `saveToDraft` was `false` during scheduling tests with short timers. Fixed by understanding Buffer's `addToQueue` + `saveToDraft` interaction properly.
4. **Thumbnails in Drive** — 10 low-res thumbnails (< 50KB) deleted from Drive.
5. **Publisher grabbed wrong draft** — Removed fallback to "most recent pending". Now requires reply tracking match. Responds "Please reply to a specific draft message" if no match.
6. **Carousel stripped to single image** — Publisher now sends `assets: { images: [{url: img1}, {url: img2}, ...] }` for all images instead of just the first.
7. **Wix Site/Member IDs hardcoded** — Now loaded from `config.wix_site_id` / `config.wix_member_id`.
8. **EditDraft hardcoded PAT** — Replaced 8+ instances of hardcoded PAT in headers with `'Bearer ' + PAT` variable.

### EditDraft Improvements
- **`detectSlot()` function** — understands ordinals (first/second/third), "image 1/2/3", "second body image", "last image"
- **Image reorder** — "swap the order" / "reverse images" / "reorder" now reverses existing carousel images instead of pulling new ones from Drive
- **Revert feature** — snapshots draft fields before every edit. "revert" / "undo" / "go back" / "restore" restores previous version via `previous_version` Airtable field

### New Workflows Created
- **SMA-V2 BufferDelete** (`pw1nSD3wci2vCv6u`) — agent tool for deleting scheduled posts from Buffer
- **SMA-V2 BlogSchedulePublisher** (`PLMsHfWePzh8XDrh`) — hourly cron that publishes scheduled blog drafts when their time arrives
- **SMA-V2 ListDriveFolders** (`pGYuk5UAzPpRQCsj`) — dynamic folder list from the Drive image library

### Buffer Scheduling (Verified Working)
- **IG + FB**: `mode: 'customScheduled'` + `dueAt: ISO8601` — working
- **GBP**: `metadata: { google: { type: 'whats_new' } }` — working (no CTA button, Buffer doesn't support CTA buttons for GBP per their support docs)
- **Schedule parsing**: AEST timezone conversion working. "Wednesday 3pm" → `2026-04-15T05:00:00Z` ✓
- **Telegram message**: "Scheduled for Wednesday 15 Apr at 3pm AEST! Instagram: OK / Facebook: OK / GBP: OK"
- **saveToDraft**: Set to `false` for go-live.

### Wix Blog Scheduling
- Built `SMA-V2 BlogSchedulePublisher` hourly cron workflow
- Publisher saves `status: 'scheduled'` + `scheduled_publish_date` + `wix_draft_id` to Airtable
- Cron checks every hour for due blogs and publishes to Wix
- Wix REST API doesn't support native scheduling — we handle it ourselves

### Dynamic Drive Folder Support
- Added `SMA-V2 ListDriveFolders` webhook that returns all subfolder names from the parent Drive folder
- `ClassifyFolder` (Social Generator) fetches live folder list at runtime — no more hardcoded folder arrays
- `EditDraft` also uses live folder list for swap detection
- **Impact**: Mick can add/rename Drive subfolders and they're automatically picked up. No code changes needed.

## Known Issues / Open Items

### Edit/Text Bugs (not image-related)
- **"Delete from schedule"** previously went to text edit instead of delete — fixed by Buffer delete tool
- **"Revert to this version"** previously went to text edit — fixed by revert feature

### Buffer/Platform Limits
- **GBP CTA button** — Buffer doesn't support it. No workaround available.
- **Buffer rate limiting** — Heavy API usage triggers 15min-24hr rate limits. Production usage much lower than testing, should be fine.
- **Facebook "posted recently"** — Buffer's FB API has a duplicate detection that flags very similar captions within a short window. Unlikely to affect production with varied content.

### Deferred to Post-Launch
1. **Webhook URLs** — `trentham.app.n8n.cloud/webhook/...` hardcoded in EditDraft and Planner. Fine for single-instance, would need config field for multi-client.
2. **Airtable PAT** — hardcoded at top of each Code node. Can't be avoided without n8n credential refactor. Post-launch: move to n8n credentials or env vars for cleaner multi-tenant support.
3. **Blog table IDs** — Blog generator uses V1 tables for brand guide/examples. Works but not V2-consistent.
4. **Context prompt replies** — Replying to "Job Spotlight:" prompt (from weekly planner) still says "couldn't find draft". Needs the planner to create a placeholder draft first, or the agent to detect context prompts differently.

---

## System Architecture

### Flow
```
User (Telegram) → V2 Agent (n8n AI Agent, gpt-5.4-mini)
  ↓ Routes to tools:
  ├── create_social_post → Social Generator → GPT → Airtable draft → Telegram confirmation
  ├── create_blog_post → Blog Generator → GPT → Airtable draft → Telegram confirmation
  ├── edit_draft → EditDraft → GPT/Image swap/Reorder/Revert → Airtable update → Telegram
  ├── publish_post → Publisher → Buffer (IG/FB/GBP) or Wix (blogs) → Telegram
  ├── delete_scheduled_posts → BufferDelete → Buffer API delete → Telegram
  ├── lookup_drafts → LookupDrafts → Airtable query
  └── search_drive_folder → DriveSearchProxy → Google Drive

Scheduled (Cron):
  ├── Weekly Planner (Monday 6pm AEST) → auto-generates posts per content bucket
  └── Blog Schedule Publisher (hourly) → publishes scheduled blog drafts to Wix
```

### Tech Stack
- **n8n Cloud** — workflow orchestration, AI Agent, webhook triggers
- **GPT-5.4-mini** — content generation (social + blog), caption editing
- **Telegram Bot API** — user interface (create, edit, approve, schedule via chat)
- **Buffer V2 GraphQL API** — publishing to Instagram, Facebook, Google Business Profile
- **Wix Blog v3 API** — blog publishing (draft → publish, cover image, SEO)
- **Google Drive API** — image library (organized by folder: Solar, Team, General, etc.)
- **Airtable** — all state (drafts, config, post history, used images, example bank)
- **Vercel** — preview sites (social preview + blog preview)

### Airtable Tables
| Table | Purpose |
|-------|---------|
| V2 Config | Per-client config (API keys, channels, brand voice, schedule) |
| V2 Drafts | All drafts (social + blog) with full edit history, `previous_version` snapshots |
| V2 Post History | Published posts log with Buffer/Wix post IDs |
| V2 Example Bank | Real posts for voice matching (50 examples shuffled per generation) |
| V2 Used Images | Drive image usage tracking (LRU rotation) |

### Key Config Fields (V2 Config)
- `client_name`, `brand_voice`, `website_url`
- `telegram_bot_token`, `telegram_chat_id`
- `buffer_api_key`, `buffer_ig_channel`, `buffer_fb_channel`, `buffer_gbp_channel`
- `openai_api_key`
- `wix_api_key`, `wix_site_id`, `wix_member_id`
- `google_drive_folder_id`
- `scheduled_posts` (content buckets: job_spotlight, educational, team_brand, etc.)
- `context_required` (buckets that need user input: job_spotlight, blog)
- `posts_per_week`, `blogs_per_week`, `post_time`
- `blog_preview_base_url`, `preview_base_url`

### Content Buckets (Weekly Planner)
| Bucket | Description | Auto-generate? |
|--------|-------------|----------------|
| job_spotlight | Recent installations, project showcases | No (needs user context) |
| educational | Heat pumps, EV chargers, AC, solar tips | Yes |
| team_brand | Team culture, behind the scenes | Yes |
| product_spotlight | Product features, new offerings | Yes |
| community | Local events, sponsorships | Yes |
| blog | Blog post promotion | No (needs user context) |

### Workflows
| Workflow | ID | Purpose |
|----------|-----|---------|
| SMA-V2 Agent | joOvKKDolWpOTLdP | Main AI agent with tool routing |
| SMA-V2 Social Generator | eIWk6RjvYP2lgDlI | Generate IG + FB + GBP content |
| SMA-V2 BlogGenerator | uHELgth7y2dIq3Ft | Generate SEO blog posts |
| SMA-V2 EditDraft | YZq8YMqeaHxht5Xk | Edit drafts (text, images, reorder, revert) |
| SMA-V2 Publisher | RKbtyZ6AMO5sYYjx | Publish to Buffer/Wix, schedule posts |
| SMA-V2 BufferDelete | pw1nSD3wci2vCv6u | Delete scheduled posts from Buffer |
| SMA-V2 LookupDrafts | quswMumV1Ks7UK0B | Query draft status |
| SMA-V2 SendTelegram | fS2F2MiHdiBfAtnB | Send Telegram messages |
| SMA-V2 DriveImageSearch | B9aee5u4h9UTzBcM | Search Drive for images by folder |
| SMA-V2 DriveSearchProxy | LNNdWgoytdln4Dws | Proxy for agent to call DriveSearch |
| SMA-V2 ListDriveFolders | pGYuk5UAzPpRQCsj | List all subfolders of image library |
| SMA-V2 UploadToDrive | F93MGaoXeZZoNPyJ | Upload Telegram photos to Drive |
| SMA-V2 WeeklyPlanner | kGSN5w3lzNsncE37 | Auto-generate weekly post batch |
| SMA-V2 Scheduler | Ru14lsjNsxNt8R8u | Monday cron trigger for planner |
| SMA-V2 BlogSchedulePublisher | PLMsHfWePzh8XDrh | Hourly cron for scheduled blog publishing |
| SMA-V2 Draft Cleanup | mO2MRyvyM9zTeKIM | Clean old drafts |
| SMA-V2 DeleteBlog | mcHV28IQbqXLG2ZH | Delete blog from Wix |

---

## Presentation Talking Points

### Problem
Mick (solo electrician running Trentham Electrical & Solar) spends hours per week managing social media — writing posts, finding photos, scheduling across Instagram, Facebook, Google Business Profile, and his Wix blog. He wants to focus on installations, not content.

### Solution
A Telegram bot that does all of it. Mick sends a single message describing what he wants, and within 30 seconds he has a drafted post with auto-selected photos from his Drive library, ready to approve or edit.

### Key Features
1. **Natural conversation** — "Create a post about the heat pump install we finished in Kyneton yesterday" → done.
2. **Multi-platform in one go** — Each post generates 3 platform-specific versions: Instagram (hashtags, emojis), Facebook (fewer hashtags), Google Business Profile (professional tone).
3. **Smart photo selection** — GPT classifies the post topic and pulls relevant photos from the right Drive folder (Solar, Team, Heat Pump, etc.). Mick can add new folders and they're auto-detected.
4. **Blog posts with SEO** — "Write a blog about solar panel maintenance" → 900-word SEO-optimized article with images, meta description, keyword tagging, Wix-ready.
5. **Scheduling in natural language** — "Schedule for Wednesday 3pm" → converts to AEST-aware UTC, publishes at the right time.
6. **Reply-based editing** — Reply to any draft with instructions: "change the tone", "swap the second image", "remove GBP", "reverse the image order", "undo", "delete from schedule".
7. **Weekly autopilot** — Every Monday, auto-generates posts for the week per content calendar (job spotlights, educational tips, team/brand, community).
8. **Revert safety** — Every edit saves a snapshot. "Undo" restores the previous version.
9. **Voice matching** — Uses Mick's real past posts as examples (50 shuffled per generation) so the AI writes in his voice, not corporate-speak.

### Scale
- Single-client MVP. Config-driven architecture means onboarding a new client = editing one Airtable row (API keys, brand voice, Drive folder) + updating one token per Code node.
- Fully multi-tenant requires moving the Airtable PAT to n8n credentials (post-launch optimization).

### Cost
- GPT-5.4-mini: ~$0.20-0.55/month per client (very low — generations are short, examples cached)
- n8n Cloud: ~$20/month (flat, supports many clients)
- Buffer: Mick's existing plan
- Airtable: Free tier sufficient
- Vercel: Free tier
- **Total**: < $25/month/client ongoing

### What Makes This Different
- **Examples over rules**: Most AI content tools use detailed prompts. This one uses 50 real posts from the client's account as examples — GPT matches voice naturally instead of following a rigid template.
- **Reply-based editing**: No web UI, no forms. Just reply to the bot like you're texting a colleague.
- **Config-driven**: Brand voice, schedule, content buckets, Drive folders — all editable in Airtable. No code changes to onboard.
- **Verification safeguards**: Reply tracking required for publishing. Draft snapshots for undo. Context-aware draft matching across the edit chain.
