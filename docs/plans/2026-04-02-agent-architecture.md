# Trentham Social Media Agent — Architecture Design

## Core Principle

**Every interaction is AI-powered.** Mick talks naturally. The system understands context, intent, and nuance. No keywords, no rigid commands, no structuring messages around system limitations.

---

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                       TELEGRAM GROUP                          │
│  Mick sends anything: photos, text, approvals, questions,    │
│  revisions, multi-intent messages, voice notes, references   │
│  to old drafts — whatever feels natural                      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                 WF1: INTELLIGENT ROUTER                       │
│                                                              │
│  Every message → Context fetch → AI Classifier → Route       │
│  Understands multi-intent, photo purpose, draft references   │
└───┬────────┬────────┬────────┬────────┬────────┬────────────┘
    │        │        │        │        │        │
    ▼        ▼        ▼        ▼        ▼        ▼
   WF2      WF3      WF4      WF5     WF6      WF7
  Social    Blog   Approval   Q&A   Schedule  Publisher
   Gen       Gen    Flow             (cron)   (no AI)
    │        │        │
    ▼        ▼        ▼
  ┌─────────────────────┐
  │    JUDGE AGENT      │
  │  (quality gate on   │
  │   all generated     │
  │   content)          │
  └──────────┬──────────┘
             │
             ▼
        Send to Telegram
        for Mick's approval
```

---

## Workflows

### WF1: Intelligent Router

**Every message goes through AI classification.** No deterministic shortcuts. The classifier sees full context and reasons about intent.

```
Telegram Trigger (any message)
    │
    ▼
┌──────────────────────────────────────┐
│  CONTEXT FETCH (n8n, deterministic)  │
│                                      │
│  Parallel fetches:                   │
│  • Pending drafts from Airtable      │
│    (what's awaiting approval?)       │
│  • Last 5 conversation messages      │
│    (what were we just talking about?)│
│  • Metadata: has photo? is reply?    │
│    reply_to_message_id?              │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  CLASSIFIER AGENT                    │
│  gpt-5.4-mini | temp 0.1 | ~400 tok │
│                                      │
│  Understands:                        │
│  • Multi-intent messages             │
│  • Photo purpose (new content vs     │
│    revision vs question)             │
│  • References to existing drafts     │
│    without being a direct reply      │
│  • Platform preferences stated in    │
│    natural language                   │
│  • Variation requests ("give me 5")  │
│                                      │
│  Input:                              │
│  • Mick's message text               │
│  • Photo attached? (yes/no)          │
│  • Is reply? To which message?       │
│  • Pending drafts summary            │
│  • Recent conversation context       │
│                                      │
│  Output (structured JSON):           │
│  {                                   │
│    intents: [                        │
│      {                               │
│        type: "new_social_content"    │
│          | "new_blog_content"        │
│          | "approval_response"       │
│          | "draft_revision"          │
│          | "agent_question"          │
│          | "photo_swap"             │
│          | "schedule_change"         │
│          | "not_for_agent",          │
│        draft_id: null | "abc123",    │
│        details: "extracted context"  │
│      }                               │
│    ],                                │
│    platforms: ["fb_ig","gbp","blog"] │
│      | null (= all),                 │
│    photo_purpose: "new_content"      │
│      | "revision" | "reference"      │
│      | null,                         │
│    save_photo_to_drive: true|false,  │
│    variation_count: null | 3 | 5,    │
│    urgency: "normal" | "scheduled"   │
│  }                                   │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  INTENT EXECUTOR (n8n)               │
│                                      │
│  For EACH intent in array:           │
│                                      │
│  new_social_content                  │
│    → WF2 with content brief +        │
│      platforms + variation_count      │
│                                      │
│  new_blog_content                    │
│    → WF3 with topic brief            │
│                                      │
│  approval_response                   │
│    → WF4 with draft_id + message     │
│                                      │
│  draft_revision                      │
│    → WF2 or WF3 with draft_id +     │
│      revision instructions +         │
│      new photo (if photo_swap)       │
│                                      │
│  photo_swap                          │
│    → Update draft's image,           │
│      regenerate with new photo       │
│                                      │
│  agent_question                      │
│    → WF5 with question               │
│                                      │
│  schedule_change                     │
│    → Update Airtable config,         │
│      confirm in Telegram             │
│                                      │
│  not_for_agent → no response         │
│                                      │
│  If save_photo_to_drive: true        │
│    → Also save to Drive + Image      │
│      Library (categorise with        │
│      vision API)                     │
└──────────────────────────────────────┘
```

**Example messages the classifier handles correctly:**

| Mick says | Classified as |
|-----------|---------------|
| "Do a post about this solar install" + photo | new_social_content, save_photo=true |
| "Also do a blog about it" | new_blog_content (references last conversation) |
| "Use this photo instead" + photo | photo_swap, draft_id=current pending |
| "Approve" (reply to bot) | approval_response, all platforms approve |
| "Looks good but skip the blog" | approval_response, blog=skip |
| "Give me 5 options for this one" + photo | new_social_content, variation_count=5 |
| "What did we post last week?" | agent_question |
| "Combine option 1 and 3" | draft_revision |
| "Hold off on that one" | draft_revision (pause, not delete) |
| "Hey boys what time tomorrow?" | not_for_agent |
| "Approve the social and also write a blog about batteries" | multi-intent: [approval_response, new_blog_content] |
| "Can you make the GBP shorter and more punchy?" | draft_revision, platforms=gbp |
| "Actually use the Kyneton photos from last week" | photo_swap, references Drive |
| "Move Tuesday's post to Thursday" | schedule_change |

---

### WF2: Social Content Generation

```
Input from Router:
  • content_brief (Mick's description)
  • photo (if provided)
  • platforms (fb_ig, gbp, or both — default both)
  • variation_count (null=1, or 3 or 5)
  • is_revision? (if yes: existing draft + instructions)
    │
    ▼
┌──────────────────────────────────────┐
│  CONTEXT ASSEMBLY (n8n)              │
│                                      │
│  Parallel fetches:                   │
│  1. Brand guide (master + social)    │  ← Airtable
│  2. Last 10 posts per platform       │  ← Airtable Post History
│  3. 2-3 examples matching post type  │  ← Airtable Example Bank
│     (rotated, never same as last     │     (track which were used)
│      generation)                     │
│  4. 1 anti-example for this type     │  ← Airtable Example Bank
│  5. Image description via vision API │  ← If photo provided
│  6. Post type template               │  ← Airtable (matched by
│     (install showcase, educational,  │     classifier's details)
│      team intro, product spotlight,  │
│      etc.)                           │
│                                      │
│  If revision:                        │
│  7. Existing draft content           │  ← Airtable Pending Drafts
│  8. Conversation history             │  ← Airtable Messages
│  9. Mick's revision instructions     │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  SOCIAL CONTENT AGENT                │
│  gpt-5.4-mini | temp 0.7 | ~1500 tok│
│                                      │
│  System prompt (~900 tokens):        │
│  ┌────────────────────────────────┐  │
│  │ IDENTITY (300 tokens)          │  │
│  │ • Business facts (bullets)     │  │
│  │ • Core voice rules (7 max)     │  │
│  │ • Banned words                 │  │
│  │ • Permission statements        │  │
│  │ • Privacy rules                │  │
│  ├────────────────────────────────┤  │
│  │ SOCIAL RULES (400 tokens)      │  │
│  │ • IG format: emoji, hashtags,  │  │
│  │   contact, @tags, specs format │  │
│  │ • GBP format: no hashtags,     │  │
│  │   truncation, consultative     │  │
│  │ • FB format: like IG, fewer    │  │
│  │   hashtags                     │  │
│  │ • Post type template           │  │
│  ├────────────────────────────────┤  │
│  │ META-INSTRUCTIONS (200 tokens) │  │
│  │ • "If a rule makes the post    │  │
│  │   sound forced, skip it"       │  │
│  │ • Anti-repetition: don't reuse │  │
│  │   [last hook type], [last town]│  │
│  │ • "The goal is content Mick    │  │
│  │   would be proud to post"      │  │
│  └────────────────────────────────┘  │
│                                      │
│  User message (~600 tokens):         │
│  • Content brief + image description │
│  • 2-3 real examples (rotated)       │
│  • 1 anti-example                    │
│  • "Last 3 posts used these hooks:   │
│    [list]. Use a different approach." │
│                                      │
│  If variation_count > 1:             │
│  • "Generate {n} distinct variations.│
│    Each MUST use a different opening  │
│    hook and structural approach."     │
│                                      │
│  If revision:                        │
│  • "Previous draft: [content]        │
│    Mick's feedback: [instructions]   │
│    Revise accordingly."              │
│                                      │
│  Output (structured JSON):           │
│  {                                   │
│    variations: [                     │
│      {                               │
│        instagram: {                  │
│          caption: "...",             │
│          hashtags: [...],            │
│          tags: [...]                 │
│        },                            │
│        gbp: {                        │
│          body: "...",                │
│          cta_button: "Learn more"    │
│        },                            │
│        facebook: {                   │
│          caption: "..."              │
│        }                             │
│      }                               │
│    ]   // 1 item normally,           │
│  }     // 3-5 if variations requested│
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  JUDGE AGENT                         │
│  gpt-5.4-mini | temp 0.2 | ~800 tok │
│                                      │
│  Scores EACH platform output on:     │
│                                      │
│  Voice match         30%             │
│  "Does it sound like Mick, not a     │
│   generic solar company?"            │
│                                      │
│  Local specificity   20%             │
│  "Named town, team member, or        │
│   specific technical detail?"        │
│                                      │
│  Technical accuracy  20%             │
│  "Specs correct? No fabrication?"    │
│                                      │
│  Engagement potential 15%            │
│  "Strong hook? Emotional resonance?  │
│   Clear CTA?"                        │
│                                      │
│  Structural freshness 15%            │
│  "Different from last 5 posts?"      │
│                                      │
│  Also applies SWAP TEST:             │
│  "Could this appear unchanged on a   │
│   competitor's page? If yes, fail."  │
│                                      │
│  Input:                              │
│  • Generated content (all platforms) │
│  • Brand guide (core rules)          │
│  • Last 5 posts (for freshness)      │
│  • Scoring rubric                    │
│                                      │
│  Output:                             │
│  {                                   │
│    scores: {                         │
│      instagram: 3.8,                 │
│      gbp: 3.2,                       │
│      facebook: 3.7                   │
│    },                                │
│    feedback: {                       │
│      gbp: "Opening too similar to    │
│       last post. No town mentioned." │
│    },                                │
│    pass: true | false                │
│  }                                   │
│                                      │
│  Score >= 3.0 → Pass                 │
│  Score < 3.0 → Regenerate            │
│  (feed feedback back to Social Agent)│
│  Max 3 attempts, then flag to Mick   │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  SEND TO TELEGRAM                    │
│                                      │
│  VISUAL PREVIEWS — photo messages     │
│  that resemble how posts look live.  │
│  Each platform = separate Telegram   │
│  photo message (swipeable).          │
│                                      │
│  Single variation:                   │
│                                      │
│  Message 1: 📱 INSTAGRAM             │
│  [PHOTO as Telegram image]           │
│  Caption = full IG caption with      │
│  emoji, hashtags, contact info       │
│                                      │
│  Message 2: 📍 GOOGLE BUSINESS       │
│  [SAME PHOTO as Telegram image]      │
│  Caption = GBP text (no hashtags,    │
│  shorter, consultative)              │
│                                      │
│  Message 3: 📘 FACEBOOK              │
│  [SAME PHOTO as Telegram image]      │
│  Caption = FB text (fewer hashtags)  │
│                                      │
│  Message 4 (if blog):               │
│  📝 BLOG: [Wix draft preview link]  │
│  "Open to see full article with      │
│   headings, images, formatting"      │
│                                      │
│  Final message:                      │
│  "Reply to approve all, or tell me   │
│   what to change for any platform."  │
│                                      │
│  Multiple variations:                │
│  Send N photo messages per platform  │
│  with variation number in label:     │
│                                      │
│  📱 IG Option 1: [PHOTO + caption]   │
│  📱 IG Option 2: [PHOTO + caption]   │
│  📱 IG Option 3: [PHOTO + caption]   │
│  ...                                 │
│  "Pick a number, or tell me to       │
│   combine elements from different    │
│   options."                          │
│                                      │
│  Mick swipes through like a feed —   │
│  closest to how it'll actually look  │
│  on each platform.                   │
│                                      │
│  Save to Airtable:                   │
│  • Pending Drafts (all platform      │
│    content, status=pending)          │
│  • Conversation Messages (agent msg) │
│  • Store telegram_message_id for     │
│    reply matching                    │
└──────────────────────────────────────┘
```

---

### WF3: Blog Generation

```
Input from Router:
  • topic brief (Mick's description or content calendar)
  • photos (if provided)
  • is_revision? (if yes: existing draft + instructions)
    │
    ▼
┌──────────────────────────────────────┐
│  RESEARCH STEP (n8n + AI)            │
│                                      │
│  1. Research Agent determines what    │
│     needs verification:              │
│     • Rebate amounts? → search       │
│     • Policy deadlines? → search     │
│     • Product specs? → search        │
│     • General solar education?       │
│       → skip research, use training  │
│                                      │
│  2. For each fact needing research:  │
│     • Web search (5+ results)        │
│     • Cross-reference across 3+      │
│       sources                        │
│     • Priority: govt sites >         │
│       manufacturer > industry bodies │
│     • Reject: SEO farms, affiliates, │
│       AI-generated aggregators       │
│                                      │
│  3. Also fetch from Airtable:        │
│     • Facts table (pre-verified      │
│       rebate rates, deadlines)       │
│     • Blog-specific brand guide      │
│     • Last 3 blog posts              │
│     • Blog template (educational     │
│       or job spotlight)              │
│     • 2 blog examples from bank      │
│                                      │
│  4. If sources conflict:             │
│     → Flag to Mick in Telegram       │
│     "Found conflicting info on STC   │
│      rates: Solar Vic says $310,     │
│      CEC says $336. Which to use?"   │
│     → Wait for response before       │
│       generating                     │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  BLOG AGENT                          │
│  gpt-5.4-mini | temp 0.6 | ~1500 tok│
│                                      │
│  System prompt:                      │
│  • Brand identity (bullets)          │
│  • Blog voice rules (more            │
│    structured than social, but       │
│    same personality)                 │
│  • SEO checklist (title format,      │
│    H2 structure, keyword placement)  │
│  • Research rules:                   │
│    "Verified facts are your most     │
│    powerful tool. $15,540 in savings │
│    before May 1st is compelling.     │
│    'Significant savings for a        │
│    limited time' is forgettable."    │
│  • Technical simplification rules    │
│  • Permission statements             │
│                                      │
│  User message:                       │
│  • Topic brief                       │
│  • Verified research findings        │
│  • Blog template (educational or     │
│    job spotlight)                     │
│  • 2 real blog examples              │
│  • 1 anti-example                    │
│  • Image descriptions (if provided)  │
│                                      │
│  Output:                             │
│  {                                   │
│    title: "...",                      │
│    meta_description: "...",          │
│    slug: "...",                       │
│    body: "... (markdown)",           │
│    content_type: "educational"       │
│      | "job_spotlight",              │
│    sources_used: [{url, claim}],     │
│    facts_to_verify: ["any claims     │
│      I wasn't 100% sure about"]      │
│  }                                   │
└──────────────────┬───────────────────┘
                   │
                   ▼
              Judge Agent
              (same as WF2, blog-specific rubric)
                   │
                   ▼
              Send to Telegram for approval
```

---

### WF4: Approval Flow

**Routed here by the Classifier when intent = approval_response or draft_revision.**

The Classifier has already identified which draft Mick is referring to (even without a direct reply) and extracted his instructions.

```
Input from Router:
  • draft_id (identified by Classifier)
  • Mick's message
  • intent type (approve / revise / photo_swap)
    │
    ▼
┌──────────────────────────────────────┐
│  FETCH DRAFT CONTEXT (n8n)           │
│                                      │
│  • Draft content (all platforms)     │  ← Airtable Pending Drafts
│  • Per-platform status               │
│  • Full conversation history         │  ← Airtable Messages
│  • Variation options (if applicable) │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  APPROVAL AGENT                      │
│  gpt-5.4-mini | temp 0.1 | ~500 tok │
│                                      │
│  Understands natural language:       │
│  • "approve" → all publish           │
│  • "looks good but skip the blog"    │
│    → fb_ig + gbp publish, blog skip  │
│  • "make the GBP shorter" → gbp     │
│    redraft, others hold              │
│  • "option 3" → select variation 3   │
│  • "combine 1 and 4" → merge        │
│  • "hold off" → pause all           │
│  • "actually post it to FB only"     │
│    → fb publish, others skip         │
│  • "use this photo instead" + photo  │
│    → swap image, regenerate          │
│  • "change the second paragraph"     │
│    → specific edit instruction       │
│                                      │
│  Input:                              │
│  • Mick's message                    │
│  • Current draft state per platform  │
│  • Conversation history              │
│  • Variation list (if multi-option)  │
│                                      │
│  Output:                             │
│  {                                   │
│    actions: {                        │
│      instagram: "approve" | "redraft"│
│        | "skip" | "hold",           │
│      gbp: "approve" | "redraft"     │
│        | "skip" | "hold",           │
│      blog: "approve" | "redraft"    │
│        | "skip" | "hold"            │
│    },                                │
│    selected_variation: null | 3,     │
│    merge_variations: null | [1, 4],  │
│    redraft_instructions: {           │
│      gbp: "shorter, more punchy"     │
│    },                                │
│    photo_swap: true | false,         │
│    response: "On it — publishing     │
│      FB and IG, redrafting GBP."     │
│  }                                   │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  EXECUTE ACTIONS (n8n)               │
│                                      │
│  For each platform:                  │
│                                      │
│  "approve"                           │
│    → WF7 Publisher                   │
│                                      │
│  "redraft"                           │
│    → Back to WF2 Social Agent        │
│      with: existing draft +          │
│      Mick's specific instructions +  │
│      new photo (if swap)             │
│    → Re-judge → Telegram             │
│                                      │
│  "skip"                              │
│    → Update Airtable status=skipped  │
│                                      │
│  "hold"                              │
│    → Keep in pending, no action      │
│                                      │
│  "merge_variations"                  │
│    → Send variations [1,4] back to   │
│      Social Agent: "Merge the hook   │
│      from variation 1 with the body  │
│      from variation 4"               │
│    → Re-judge → Telegram             │
│                                      │
│  Log everything:                     │
│  • Mick's message → Messages table   │
│  • Agent response → Messages table   │
│  • Status changes → Pending Drafts   │
│  • Send response to Telegram         │
└──────────────────────────────────────┘
```

---

### WF5: Q&A Agent

```
Input from Router:
  • Mick's question
  • conversation context
    │
    ▼
┌──────────────────────────────────────┐
│  Q&A AGENT                           │
│  gpt-5.4-mini | temp 0.3 | ~400 tok │
│                                      │
│  Tools (sub-workflows):              │
│  • read_post_history                 │
│    → Airtable Post History table     │
│  • read_schedule                     │
│    → Airtable Master Config          │
│  • read_image_library                │
│    → Airtable Image Library          │
│  • read_pending_drafts               │
│    → Airtable Pending Drafts         │
│                                      │
│  Example interactions:               │
│                                      │
│  "What did we post last week?"       │
│  → Fetches last 7 days from history  │
│  → Summarises: "3 posts: install     │
│    showcase in Kyneton (Tue),        │
│    EV charging educational (Thu),    │
│    team photo with Lewis (Sat)"      │
│                                      │
│  "When's the next scheduled post?"   │
│  → Reads config: "Tuesday at 9am,   │
│    topic: battery benefits"          │
│                                      │
│  "How many photos do we have of      │
│   solar installs?"                   │
│  → Queries Image Library             │
│  → "47 in Solar folder, 12 unused    │
│    on Instagram"                     │
│                                      │
│  "What was the last GBP post about?" │
│  → Fetches latest GBP from history   │
│  → Summarises content                │
│                                      │
│  Reply directly in Telegram.         │
└──────────────────────────────────────┘
```

---

### WF6: Autonomous Scheduled Posts

```
n8n Schedule Trigger
(reads days + time from Airtable config)
    │
    ▼
┌──────────────────────────────────────┐
│  CONTENT PLANNER (n8n, deterministic)│
│                                      │
│  1. What type of post is due?        │
│     → Read content calendar from     │
│       Airtable (job spotlight vs     │
│       educational filler)            │
│                                      │
│  2. Select topic                     │
│     → Rotate through filler topics   │
│       (battery benefits, EV, solar   │
│        ROI, blackouts, VEU...)       │
│     → Skip last used topic           │
│     → Check: has this topic been     │
│       covered in last 14 days?       │
│                                      │
│  3. Select image                     │
│     → Query Image Library table      │
│     → Match folder to topic          │
│       (EV topic → EV Charging folder)│
│     → Filter: unused on target       │
│       platform(s)                    │
│     → Pick least-recently-used if    │
│       all used                       │
│                                      │
│  4. Image library health check       │
│     → If < 3 unused images in        │
│       selected folder:               │
│       Alert Mick in Telegram:        │
│       "Running low on EV photos —    │
│        upload some when you can"     │
│                                      │
│  5. Check crisis flag                │
│     → Airtable: crisis_pause field   │
│     → If true: skip, log, don't post │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  GENERATE CONTENT BRIEF              │
│                                      │
│  Assemble a brief as if Mick sent it:│
│  • Topic: "educational post about    │
│    battery benefits"                 │
│  • Image: [selected from Drive]      │
│  • Platforms: all (fb_ig + gbp)      │
│  • Source: "autonomous"              │
│                                      │
│  Feed into WF2 (Social) or WF3      │
│  (Blog) — same pipeline as manual    │
└──────────────────┬───────────────────┘
                   │
                   ▼
              Judge Agent scores it
                   │
                   ▼
              Send to Telegram for approval
              (Mick still approves autonomous
               posts — at least in Phase 1)
```

---

### WF7: Publisher (deterministic, no AI)

```
Approved content arrives (from WF4)
    │
    ▼
┌──────────────────────────────────────┐
│  FOR EACH APPROVED PLATFORM:         │
│                                      │
│  instagram                           │
│    → Buffer API                      │
│    → Upload image from Drive URL     │
│    → Caption + hashtags              │
│    → If success: log + get post URL  │
│    → If fail: report to Telegram     │
│                                      │
│  facebook                            │
│    → Buffer API                      │
│    → Same image                      │
│    → Caption (fewer hashtags)        │
│    → If success: log + get post URL  │
│    → If fail: report to Telegram     │
│                                      │
│  gbp                                 │
│    → Google Business Profile API     │
│    → localPosts endpoint             │
│    → Body text + image + CTA button  │
│    → If success: log                 │
│    → If fail: report to Telegram     │
│                                      │
│  blog                                │
│    → Wix Blog API                    │
│    → Create draft post               │
│    → Convert markdown to Wix rich    │
│      content format                  │
│    → Set title, meta, slug, image    │
│    → Publish draft                   │
│    → If success: log + get post URL  │
│    → If fail: report to Telegram     │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  POST-PUBLISH (n8n, deterministic)   │
│                                      │
│  For each successful publish:        │
│  • Log to Post History table         │
│    (platform, content, topic,        │
│     image_id, judge_score, date)     │
│  • Update Image Library usage date   │
│    (per-platform tracking)           │
│  • Update Pending Draft status       │
│    → "published"                     │
│                                      │
│  Send confirmation to Telegram:      │
│  "Published!                         │
│   📱 Instagram: [link]               │
│   📘 Facebook: [link]                │
│   📍 GBP: posted                     │
│   ✅ All platforms successful"        │
│                                      │
│  Error handling:                     │
│  • If one platform fails:            │
│    → Don't re-post to succeeded ones │
│    → Report: "FB + IG published.     │
│      GBP failed: [error message]"    │
│    → Mick can say "retry GBP"        │
│      → Classifier routes to          │
│        publisher for GBP only        │
└──────────────────────────────────────┘
```

---

## Agent Summary

| Agent | Model | Temp | Purpose | Prompt Size | Calls/post |
|-------|-------|------|---------|-------------|------------|
| Classifier | gpt-5.4-mini | 0.1 | Understand every message: intent, platforms, photo purpose, draft refs, multi-intent | ~400 tok | 1 per message |
| Social Content | gpt-5.4-mini | 0.7 | Generate FB/IG/GBP posts (single or multi-variation) | ~1500 tok | 1 per post |
| Blog Content | gpt-5.4-mini | 0.6 | Research + generate blog posts (600-1800 words) | ~1500 tok | 1 per blog |
| Judge | gpt-5.4-mini | 0.2 | Score quality, apply swap test, enforce freshness | ~800 tok | 1-3 per post |
| Approval Parser | gpt-5.4-mini | 0.1 | Parse natural language approvals, revisions, selections | ~500 tok | 1 per approval |
| Q&A | gpt-5.4-mini | 0.3 | Answer questions using Airtable tools | ~400 tok | 1 per question |

**Total: 6 agents, 7 workflows**

---

## Context Loading Strategy

```
┌─────────────────────────────────────────────────────┐
│  TIER 1: IDENTITY — loaded in EVERY agent (~300 tok)│
│                                                     │
│  • Master Electrician, 20+ years                    │
│  • Based in Trentham, VIC                           │
│  • Services: solar, batteries, EV, heat pumps       │
│  • Team: Mick, Kevin, Sam, Lewis, Ritchie, Max     │
│  • Brand: purple vans, CEC certified                │
│  • Voice: "we/our", casual-pro, craftsmanship       │
│  • Banned: "delve","unlock","harness","landscape",  │
│    "foster","cheap","budget","guarantee"             │
│  • Permission: casual AU English, confident claims,  │
│    light humour, skip rules if forced-sounding       │
│  • Privacy: first names only, suburb not street,     │
│    no customer costs unless provided                 │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│  TIER 2: TASK-SPECIFIC — varies by agent (~600 tok) │
│                                                     │
│  Social Agent:                                      │
│  • IG rules (emoji, hashtags, @tags, contact)       │
│  • GBP rules (no hashtags, truncation, consultative)│
│  • FB rules (like IG, fewer hashtags)               │
│  • Post type template for THIS type                 │
│  • Specs format template                            │
│                                                     │
│  Blog Agent:                                        │
│  • Blog voice rules (structured but personal)       │
│  • SEO checklist                                    │
│  • Research rules + source priority                 │
│  • Technical simplification patterns                │
│                                                     │
│  Judge Agent:                                       │
│  • 5-dimension scoring rubric                       │
│  • Swap test instruction                            │
│  • Last 5 posts (for freshness comparison)          │
│                                                     │
│  Classifier Agent:                                  │
│  • Intent taxonomy + examples                       │
│  • Pending drafts context                           │
│  • Recent conversation                              │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│  TIER 3: PER-CALL — assembled by n8n (~600 tok)     │
│                                                     │
│  • Content brief (Mick's message)                   │
│  • Image description (vision API)                   │
│  • 2-3 rotating real examples                       │
│  • 1 anti-example                                   │
│  • Last 10 posts summary (anti-repetition)          │
│  • Exclusion rules: "last hook was [X], last town   │
│    was [Y], don't repeat either"                    │
│  • Revision context (if applicable)                 │
└─────────────────────────────────────────────────────┘

TOTAL PER CALL: ~1500 tokens input
With prompt caching: Tier 1+2 cached (50-90% off)
Only Tier 3 is fresh each call
```

---

## Quality Loop

```
┌──────────────────────────────────────┐
│           PER-POST LOOP              │
│                                      │
│  Generate                            │
│      │                               │
│      ▼                               │
│  Judge scores (5 dims, 1-5 scale)    │
│      │                               │
│      ├── >= 3.5 → Send to Mick      │
│      │                               │
│      ├── 3.0-3.5 → Regenerate with   │
│      │   specific feedback:          │
│      │   "Score 3.1. Issues: generic │
│      │    opening, no town, same     │
│      │    structure as last post.    │
│      │    Fix these specifically."   │
│      │   → Attempt 2 → Re-judge     │
│      │                               │
│      └── < 3.0 after 3 attempts →    │
│          Flag to Mick:               │
│          "Struggling with this one.  │
│           Best attempt attached.     │
│           Your input would help."    │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│         WEEKLY/MONTHLY LOOPS         │
│                                      │
│  Weekly:                             │
│  • Sample 3-5 published posts        │
│  • Re-score through Judge            │
│  • Flag any score drops              │
│                                      │
│  Monthly:                            │
│  • Track: vocabulary diversity,      │
│    town mention distribution,        │
│    hook pattern variety,             │
│    average judge scores              │
│  • Declining trends = drift alert    │
│                                      │
│  Quarterly:                          │
│  • Refresh example bank:             │
│    retire 3-4 weakest,              │
│    promote 3-4 top performers       │
│  • Review and update prompts         │
│  • A/B test model upgrade            │
│    (5.4-mini vs 5.4 full)           │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│       HUMAN FEEDBACK LOOP            │
│                                      │
│  Every Mick edit is logged:          │
│  • Original AI version               │
│  • Mick's edited version             │
│  • Edit category (tone fix,          │
│    factual correction, added         │
│    specificity, restructured)        │
│                                      │
│  Monthly analysis:                   │
│  • If 40% of edits are "added        │
│    specificity" → strengthen         │
│    specificity rules                 │
│  • If most rejections are "too       │
│    generic" → add more anti-examples │
│  • Best edited posts → promote       │
│    to example bank                   │
└──────────────────────────────────────┘
```

---

## Data Flow: Airtable Tables

```
┌──────────────────┐     ┌───────────────────┐
│  Master Config    │     │  Pending Drafts   │
│                   │     │                   │
│  • Brand guides   │     │  • draft_id       │
│  • Schedule config│     │  • telegram_msg_id│
│  • Folder IDs     │     │  • trigger_type   │
│  • Platform IDs   │     │  • platforms      │
│  • Crisis flag    │     │  • status per     │
│  • Filler topics  │     │    platform       │
│  • Facts table    │     │  • content per    │
│    (verified      │     │    platform       │
│     rebate rates, │     │  • variations[]   │
│     deadlines)    │     │  • judge_score    │
└────────┬─────────┘     │  • revision_count │
         │               └────────┬──────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌───────────────────┐
│  Post History     │     │  Conversation     │
│                   │     │  Messages         │
│  • post_id        │     │                   │
│  • platform       │     │  • message_id     │
│  • content        │     │  • draft_id (link)│
│  • image_id (link)│     │  • sender         │
│  • topic          │     │    (user / agent) │
│  • hook_type      │     │  • message_text   │
│  • town_mentioned │     │  • timestamp      │
│  • judge_score    │     │                   │
│  • published_at   │     │                   │
│  • platform_url   │     │                   │
│  • edit_category  │     │                   │
│    (if Mick edited│     │                   │
│     before approve│     │                   │
└──────────────────┘     └───────────────────┘
         │
         ▼
┌──────────────────┐     ┌───────────────────┐
│  Image Library    │     │  Example Bank     │
│                   │     │                   │
│  • image_id       │     │  • example_id     │
│  • drive_file_id  │     │  • platform       │
│  • folder         │     │  • post_type      │
│  • description    │     │  • content        │
│  • source         │     │  • annotation     │
│  • used_in_fb     │     │    (why it works) │
│  • used_in_ig     │     │  • is_anti_example│
│  • used_in_gbp    │     │  • last_used_date │
│  • used_in_blog   │     │  • performance    │
│                   │     │    (engagement)    │
└──────────────────┘     └───────────────────┘
```

---

## Privacy Rules (embedded in Tier 1, every agent)

- Customer names: **first name only**, never surname
- Location: **suburb/town only**, never street address
- System costs: **never disclose** unless Mick provides in the brief
- Property photos: OK (standard industry practice)
- Team: first names + role, never personal phone/email
- Financial: general savings OK, specific customer savings only if Mick provides
- Mick's surname: never disclosed

---

## Cost Estimate

| Item | Monthly |
|------|---------|
| Classifier (~600 calls) | $0.05 |
| Social Content (~60 calls) | $0.15 |
| Blog Content (~4 calls) | $0.02 |
| Judge (~120 calls) | $0.08 |
| Approval (~80 calls) | $0.03 |
| Q&A (~30 calls) | $0.01 |
| Research (blog web search) | $0.02 |
| **Total API cost** | **~$0.36/month** |

With prompt caching (Tier 1+2 cached): **~$0.20/month**

All other infrastructure (n8n, Buffer, Airtable, Drive) is existing and already paid for.

---

## What Needs Building

| # | Deliverable | Complexity | Dependencies |
|---|-------------|------------|--------------|
| 1 | Restructure brand guides into Tier 1/2/3 prompts | Medium | Architecture approved |
| 2 | Build Example Bank in Airtable (15+ annotated) | Medium | Brand guides done |
| 3 | Build Anti-Example Bank (8+ paired BAD/GOOD) | Medium | Brand guides done |
| 4 | WF1: Intelligent Router + Classifier Agent | Medium | Prompt 1 ready |
| 5 | WF2: Social Content Generation + Judge | Complex | Prompts 2+4 ready |
| 6 | WF3: Blog Generation + Research Tool | Complex | Prompt 3 ready |
| 7 | WF4: Approval Flow | Medium | Prompt 5 ready |
| 8 | WF5: Q&A Agent | Simple | Airtable schema done |
| 9 | WF6: Autonomous Scheduler | Medium | WF2 working |
| 10 | WF7: Publisher (Buffer + GBP + Wix) | Medium | API credentials |
| 11 | Airtable schema (7 tables) | Simple | — |
| 12 | Google Drive folder structure | Simple | Drive credential |
| 13 | Facts Table in Airtable (rebate data) | Simple | Manual data entry |
| 14 | Judge scoring rubric prompt | Medium | Brand guides done |
| 15 | Monthly drift detection workflow | Simple | Post History populated |
