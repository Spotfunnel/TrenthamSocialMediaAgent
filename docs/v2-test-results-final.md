# V2 Comprehensive Test Results — 2026-04-08

## Test Method
All tests run via Playwright on Telegram Web (web.telegram.org) with backend verification via Airtable API and n8n execution API. Every test fired through the real Telegram bot (@TrenthamSocialsV2bot), waited for response, then verified backend state.

## Results: 16/16 PASS

### Section A: Social Post Creation
| Test | Message | Result | Backend |
|------|---------|--------|---------|
| A1 | "10kW solar install at 22 Smith St Woodend, Fronius, 22 Trina panels" | PASS | IG/FB/GBP all present, image from Solar Drive folder, specs preserved in caption |
| A2 | "do a post" | PASS | Agent asked "What about?" — didn't create empty post |
| A4 | "crew BBQ for Instagram and Facebook only" | PASS | GBP="" empty, platforms="fb_ig" |
| A5 | "battery storage, just for Instagram" | PASS | FB=0, GBP=0, only IG content |
| A7 | Two consecutive solar posts | PASS | 2 different images selected (LRU working) |
| A8 | "our new office renovation" (no matching folder) | PASS | Fell back to General folder image |

### Section B: Draft Editing
| Test | Message | Result | Backend |
|------|---------|--------|---------|
| B11 | "Make it shorter and more punchy" | PASS | Caption edited, Telegram response received |
| B13 | "Add a strong call to action at the end" | PASS | CTA added to caption |
| B14 | "Remove GBP from the post" | PASS | GBP="" empty, platforms changed |

### Section C: Drive Integration
| Test | Message | Result | Backend |
|------|---------|--------|---------|
| C19 | "Search the Solar folder in Drive" | PASS | Agent listed images found |
| C20 | "What images are in the batteries folder?" | PASS | Fuzzy matched "batteries" → "Batteries" |

### Section D: Blog Creation
| Test | Message | Result | Backend |
|------|---------|--------|---------|
| D25 | "Write a blog about EV charger installation for rural properties" | PASS | 917 words, 7 H2s, slug/meta/keyword all present, Vercel preview renders correctly |

### Section E: Scheduling
| Test | Message | Result | Backend |
|------|---------|--------|---------|
| E30 | "Plan this week's posts" | PASS | Agent called planner, response received |
| E32 | Topic index check | PASS | Advanced from 0 to 3 after planning 3 posts |

### Section G: Q&A
| Test | Message | Result | Backend |
|------|---------|--------|---------|
| G39 | "What posts do I have pending?" | PASS | Listed actual pending drafts |
| G41 | "What are your capabilities?" | PASS | Explained all features |
| G42 | "Do you know what time it is in Melbourne?" | PASS | Responded gracefully |
| G43 | "hi" | PASS | Friendly greeting |

## Preview Page Quality

### Social Preview (v2-preview-app.vercel.app)
- Instagram mockup: authentic layout, profile pic, username, location, likes, action icons
- GBP mockup: Google logo, verified badge, date, "Learn more" CTA button, text truncation
- Facebook mockup: business name, date, caption above image, action buttons
- Platform tabs: correctly hidden when content is null (e.g. no GBP tab when filtered)
- Images: render from Google Drive lh3 URLs
- Hashtags: rendered in link color (purple/blue)

### Blog Preview (preview-site-inky.vercel.app)
- Renders with real Wix Myriad Pro fonts
- "DRAFT PREVIEW — NOT YET PUBLISHED" banner
- Author, date, read time in header
- H2 sections properly spaced
- SEO preview box at bottom with title, URL, meta description
- Footer with website + phone
- Content quality: educational, local references, proper CTA

## Architecture Notes (not bugs, future improvements)

1. **Blog images**: V2 blog generator doesn't auto-select 4 images like V1. Needs `flatten_with_images` equivalent.
2. **Blog SEO validation**: V2 doesn't run automated SEO checks (keyword density, internal links, meta length). Blog Generator prompt handles most of this but no automated validation step.
3. **Drive folder search**: n8n's `fileFolder` search matches files AND folders by name. Can return wrong results for common names. Architecture limitation.
4. **Tool observation relay**: The AI Agent's `output` field is sometimes empty even when the tool returned data. The "Always Reply" node handles this by checking for recent drafts, but it's a workaround for an n8n platform behavior.
5. **Blog images in preview**: Blog preview renders without images since V2 doesn't select them yet.
6. **Crisis pause removed**: Per Leo, not needed. Customer simply won't approve posts.

## V2 Final Node Count

| Workflow | Nodes | Purpose |
|----------|-------|---------|
| SMA-V2 Agent (main) | 15 | AI Agent + triggers + config + Always Reply |
| SMA-V2 Social Generator | 4 | Classify → Drive search → Generate → Save |
| SMA-V2 DriveImageSearch | 6 | Search Drive folders for images |
| SMA-V2 EditDraft | 2 | Targeted caption edits + platform removal |
| SMA-V2 BlogGenerator | 2 | SEO blog generation |
| SMA-V2 Publisher | 2 | Buffer social + Wix blog publishing |
| SMA-V2 WeeklyPlanner | 2 | Schedule config → topic rotation → brief generation |
| SMA-V2 LookupDrafts | 2 | Query V2 Drafts table |
| SMA-V2 SendTelegram | 2 | Telegram message sending (ack tool) |
| **Total** | **37** | **vs 150+ in V1 (75% reduction)** |
