# V2 Config Table — Full Export
**Table ID:** `tbleVI4pkVedNuQth`  
**Base ID:** `app3fWPgMxZlPYSgA`  
**Record:** `recOanshU91Rio5ER`

---

## Scheduling & Content

| Field | Value | Description |
|-------|-------|-------------|
| **scheduled_posts** | `job_spotlight,educational,blog` | What gets created each week. Comma-separated list of content buckets. |
| **context_required** | `job_spotlight,blog` | Which scheduled posts need user input before generating. Each gets a separate Telegram message. |

### Content Buckets

| Bucket | Description | Auto-gen? |
|--------|-------------|-----------|
| `job_spotlight` | Highlights from a recent solar/battery/electrical job | **No** — asks for photo + description |
| `educational` | Solar, batteries, rebates, EV charging, heat pumps, air con, switchboards, off-grid, energy tips | **Yes** — GPT picks specific topic |
| `team_brand` | Crew, purple van, behind-the-scenes, team culture | **Yes** — GPT picks creative angle |
| `product_spotlight` | Fronius, SMA, BYD, Tesla, FranklinWH, Reclaim, Mitsubishi, Trina, Schneider | **Yes** — GPT picks specific product |
| `community` | Local events, sponsorships, school projects, community involvement | **Yes** — GPT picks creative angle |
| `blog` | SEO blog post (600-1200 words) on any topic | **No** — asks for topic/angle |

### Drive Folder Selection (Dynamic)

Images are NOT hardcoded per bucket. The `ClassifyFolder` node uses GPT to match the brief to the right Drive folder:

| Drive Folder | Matched when brief is about... |
|-------------|-------------------------------|
| Solar | Solar panels, rooftop installs, solar ROI |
| Batteries | Battery storage, BYD, Tesla Powerwall, FranklinWH |
| Team | Crew photos, van shots, behind the scenes |
| Electrical | Switchboard upgrades, electrical work |
| Air Conditioning | Air con installs, Mitsubishi, cooling |
| EV Charging | EV chargers, home charging |
| Heat Pump Hot Water | Heat pumps, Reclaim, hot water systems |
| General | Anything that doesn't fit above |

So if `educational` generates a brief about heat pump rebates → ClassifyFolder picks "Heat Pump Hot Water" folder → images come from that folder. If `product_spotlight` picks Fronius → ClassifyFolder picks "Solar" → solar images. Blog about EV charging → "EV Charging" folder.

### How Repetition is Avoided
- Agent fetches last 50 posts before generating
- GPT is told "DO NOT repeat these recent topics: [last 10 briefs]"
- Creative freedom within each bucket — no rigid rotation, no index tracking

---

## Brand & Client

| Field | Value |
|-------|-------|
| client_name | `Trentham Electrical & Solar` |
| brand_voice | Professional but approachable. Local Macedon Ranges flavour. Focus on quality, reliability, and long-term customer value. Educational tone for filler content. Avoid jargon. Short sentences, active voice, clear calls to action. |
| active | `True` |

## Telegram

| Field | Value |
|-------|-------|
| telegram_bot_token | `8684524385:AAFH...` (masked) |
| telegram_chat_id | `8541854415` |

## Preview Sites

| Field | Value |
|-------|-------|
| preview_base_url | `https://v2-preview-app.vercel.app` |
| blog_preview_base_url | `https://preview-site-inky.vercel.app` |

## Buffer (Social Publishing)

| Field | Value |
|-------|-------|
| buffer_api_key | masked |
| buffer_ig_channel | `69ccf6e4af47dacb697888d8` |
| buffer_fb_channel | `69ccf79baf47dacb69788af8` |
| buffer_gbp_channel | `69ccf7cbaf47dacb69788b7b` |

## Google Drive

| Field | Value |
|-------|-------|
| google_drive_folder_id | `11RUOMIqGGFEQbcBxPj6c_4WdGkz2HEx_` |

## Wix Blog

| Field | Value |
|-------|-------|
| wix_api_key | masked (721 chars, has Blog scope) |
| wix_site_id | `796324bf-df28-4821-8173-2dd11719b668` |
| wix_member_id | `4bf5dd3c-6dd2-4097-b163-4821e9feff44` |

## AI

| Field | Value |
|-------|-------|
| openai_api_key | masked |

## Legacy (cleared, no longer used)

| Field | Status |
|-------|--------|
| topic_rotation | Cleared — replaced by `scheduled_posts` buckets |
| blog_topics | Cleared — blogs now use `context_required` prompt |
| last_topic_index | Cleared — no rotation tracking needed |
| last_blog_topic_index | Cleared — no rotation tracking needed |
| blogs_per_week | Cleared — blogs are just another entry in `scheduled_posts` |
| posts_per_week | Cleared — count is determined by `scheduled_posts` length |
| post_time | `09:00` — still available but cron handles timing |

---

## How to Customize

| Want to... | Do this |
|-----------|---------|
| Add more posts per week | Add entries to `scheduled_posts` (e.g. `job_spotlight,educational,team_brand,blog`) |
| Auto-generate everything | Remove all entries from `context_required` |
| Make all posts need input | Put all post types in `context_required` |
| Change which posts are created | Edit `scheduled_posts` with bucket names |
| Pause the agent | Set `active` to `False` |
| Change who receives messages | Update `telegram_chat_id` |
