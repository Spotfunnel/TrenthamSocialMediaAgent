# V2 Comprehensive Stress Test Plan

Every fix and feature built this session. Tests verify Telegram output, Airtable backend, preview rendering, and n8n execution.

## SETUP
- Clean all pending drafts
- Clean all Used Images records
- Verify all 11 workflows active

## SOCIAL POST TESTS

### S1: Basic social post with all specs
- Send: "Post about a 6kW solar install in Woodend with Enphase microinverters and Q Cells panels, crew was Dave"
- Verify: IG has emojis, 50-120 words, all specs (6kW, Woodend, Enphase, Q Cells, Dave)
- Verify: FB different from IG (fewer hashtags, max 6)
- Verify: GBP no hashtags, no emojis, consultative
- Verify: Image from Drive (lh3 URL)
- Verify: telegram_message_id saved on draft
- Verify: Image logged to Used Images table

### S2: Platform filter + no hashtags
- Send: "Post about team Friday drinks at the Trentham pub, for IG and Facebook only, no hashtags"
- Verify: GBP empty, platforms=fb_ig
- Verify: Zero # in IG and FB captions
- Verify: Different image from S1 (LRU)

### S3: Third post — image uniqueness
- Send: "Post about an EV charger install in Daylesford"
- Verify: Third unique image (3 posts, 3 different images)

### S4: Reply-edit to S1 (not S2/S3)
- Reply to S1's "Draft created!" message: "Remove GBP and mention the purple van"
- Verify: GBP removed from S1 draft only
- Verify: S2 and S3 untouched
- Verify: "purple van" added to S1 caption
- Verify: Telegram shows "Platforms: IG + FB" (not "IG:")

### S5: Vague brief
- Send: "do a post"
- Verify: Agent asks for topic/detail, doesn't create empty post

### S6: Conversational
- Send: "hey what can you help with?"
- Verify: Single response via ReplyGate, lists capabilities

## BLOG TESTS

### B1: Blog with web search research
- Send: "Write a blog about solar battery rebates in Victoria 2026"
- Verify: 4 images (cover + hero + 2 body), all unique, all from Drive
- Verify: Web search performed (check research agent node)
- Verify: SEO validation passed (600-1200 words, 6-8 H2s, keyword 4-6x)
- Verify: Judge loop ran (PassFail node executed)
- Verify: Brand guide + examples + anti-example in prompt (check AssembleBlogPrompt output)
- Verify: Blog preview renders correctly (mobile + desktop)
- Verify: Hero image at top, body images after 3rd and 5th H2
- Verify: No H2 directly under title (intro paragraph styled correctly)
- Verify: telegram_message_id saved

### B2: Blog edit (text)
- Reply to B1's message: "Make the intro paragraph shorter and add a mention of the Macedon Ranges climate"
- Verify: Blog content_blog JSON updated
- Verify: Preview shows changes
- Verify: Correct draft edited (reply tracking)

### B3: Blog photo swap request
- Reply to B1's message: "Swap the cover image"
- Verify: Agent asks Mick to send replacement photo

### B4: Blog delete
- Send: "Delete this blog" (reply to B1's message)
- Verify: Draft status updated to "deleted"
- Verify: Telegram confirms deletion

## LOOKUP + PLANNER TESTS

### L1: Lookup drafts
- Send: "What's pending?"
- Verify: Correct count and list of all pending drafts
- Verify: Shows both social and blog types

### P1: Weekly planner
- Send: "Plan this weeks posts"
- Verify: Plan summary with 3 posts, topic descriptions (not truncated)
- Verify: "Say 'generate all'" hint shown
- Verify: Topic rotation advances

## PREVIEW PAGE TESTS

### PR1: Social preview with 3-photo carousel
- Create: "Create a 3 photo carousel about solar panels"
- Open preview link in browser
- Verify: 1/3 counter, dots, swipeable carousel
- Verify: All 3 images render

### PR2: Blog preview mobile
- Open blog preview on mobile viewport (390px)
- Verify: Title readable (28px+)
- Verify: H2 headings visible (22px+)
- Verify: Intro paragraph styled (bold, distinct from body)
- Verify: Images render (hero + body)

### PR3: Blog card list page
- Open preview-site-inky.vercel.app/ (no ID)
- Verify: Cards with cover images, clean layout
- Verify: Single column on mobile, title below image
- Verify: Not the old dark gradient overlay style

### PR4: Deleted draft fallback
- Open preview link for a deleted draft
- Verify: "Draft Not Found" message, no fake content

### PR5: GBP More button
- Open a social preview with GBP content (3 tabs)
- Click Google tab
- Verify: Text truncated with "More"
- Click "More"
- Verify: Full text expands, More button hides

## EDGE CASES

### E1: Empty Drive folder
- Send a post about a topic with no matching folder images (e.g., very specific niche)
- Verify: Post created with no image (doesn't crash)

### E2: Multiple rapid messages
- Send 3 messages within 5 seconds
- Verify: All 3 get responses, no dropped messages

### E3: Media group (needs Leo to send photos)
- Send 3 photos with caption to bot
- Verify: MediaGroupGate buffers, ResolvePhotos collects
- Verify: Post uses Telegram photo URLs

## VERIFICATION CHECKLIST PER TEST
For each test, check:
- [ ] Telegram message received (correct content, one message)
- [ ] Airtable draft created/updated (correct fields)
- [ ] Preview link works (renders correctly)
- [ ] Image URLs valid (not broken, not repeated)
- [ ] No duplicate messages (ReplyGate skips when tool sent)
