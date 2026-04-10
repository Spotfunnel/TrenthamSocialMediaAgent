# All Prompts Review -- Trentham Social Media Agent

> Generated: 2026-04-03
> Model: gpt-5.4-mini (all agents)
> Strategy: Minimal prompts + 30 real post examples in USER message

---

## Prompt Architecture

The key insight from the April 2026 build session: detailed rule-based prompts flatten the voice into generic corporate content. The current approach uses minimal system prompts with real post examples loaded into the user message at runtime from the Airtable Example Bank.

**What the model sees per social content call:**
- System message: one-line identity ("You write social media posts for Trentham Electrical & Solar.")
- User message: 30 real post examples + content brief + minimal rules (spec accuracy, don't copy, FB=IG, GBP formatting)

**Only the blog and judge agents retain detailed prompts** -- they need explicit structural rules that examples alone can't teach.

---

## File Inventory

| File | Agent | Used In | Status |
|------|-------|---------|--------|
| `00-common-header.md` | All agents (shared identity) | Loaded as prefix | Active |
| `prompt-classifier.md` | WF1 Router | Classifies every message | Active |
| `prompt-social.md` | WF2 Social Content | Generates IG + GBP + FB | Active -- stripped down, examples-first |
| `prompt-judge.md` | WF2 Social Content | Quality gate after generation | Active |
| `prompt-blog.md` | WF3 Blog | Generates blog posts | Active -- not yet tested |
| `prompt-approval.md` | WF4 Approval | Parses approval messages | Active |
| `prompt-qa.md` | WF5 Q&A | Answers questions | Active |

---

## 1. Common Header (`00-common-header.md`)

**Purpose:** Shared identity and rules loaded into every agent.

**Contains:**
- Business facts (location, team, services, accreditations)
- Voice rules (we/our, casual-professional, craftsmanship language, local references)
- Banned words (AI-isms + brand-specific)
- Permissions (Australian English, humour, confidence)
- Privacy rules (first names only, suburb only, no prices unless provided)
- Specificity enforcement (every post needs suburb, team name, or technical detail)

**Notes:** This is the ONLY detailed ruleset that survived the prompt simplification. It provides identity context that examples can't teach (team member names, service area towns, privacy constraints). Used by all agents.

---

## 2. Classifier (`prompt-classifier.md`)

**Purpose:** Intent classification for every incoming Telegram message. Routes to the correct workflow.

**Input:** message_text, has_photo, is_reply, reply_to_message_id, pending_drafts summary, recent_messages (last 5)

**Intent taxonomy (8 types):**
- new_social_content, new_blog_content, approval_response, draft_revision, photo_swap, schedule_change, agent_question, not_for_agent

**Key features:**
- Multi-intent support (single message can trigger multiple actions)
- Variation count detection ("give me 5 options")
- Photo purpose classification (new content vs revision vs reference)
- Draft matching by topic when message isn't a direct reply

**Output:** Structured JSON with intents array, platforms, photo_purpose, save_photo_to_drive, variation_count, urgency

**Status:** Active in WF1 Router.

---

## 3. Social Content Generator (`prompt-social.md`)

**Purpose:** Generate IG + GBP + FB posts from a content brief in a single call.

**Current version is MINIMAL by design.** This is the prompt that benefited most from the examples-over-rules approach.

**What the prompt says:**
- You write social media posts for Trentham Electrical & Solar
- Below are real posts from this account. They ARE the style guide.
- 6 rules only: spec accuracy, no invented equipment, don't copy examples, match reference length, FB = IG minus hashtags, different openings for variations

**What the prompt does NOT say (and this is deliberate):**
- No tone instructions (examples teach this)
- No hashtag lists (examples teach this)
- No emoji guidance (examples teach this)
- No vocabulary lists (examples teach this)
- No sentence structure rules (examples teach this)

**Output:** JSON with instagram (caption + tags), gbp (body + cta_button), facebook (caption)

**GBP differences (embedded in JSON schema description):**
- No hashtags, no phone/URL, no sign-off
- First 150 chars must work as standalone headline

**FB rule (embedded in JSON schema description):**
- Same caption as Instagram, just reduce hashtags to 5-8, do NOT rewrite

**Brief richness check (pre-generation step in WF2):**
- If brief has only specs and no story/angle, agent asks: "Got the specs. Anything interesting about this job that'd make the post stand out?"

**Status:** Active in WF2 Social Content. Working end-to-end.

---

## 4. Quality Judge (`prompt-judge.md`)

**Purpose:** Scores generated content across 5 dimensions before Mick sees it. Separate agent -- no grading your own homework.

**Scoring rubric (weighted):**
- Voice Match (40%) -- swap test: could this appear on a competitor's page?
- Local Specificity (20%) -- named suburb, landmark, team member
- Technical Accuracy (15%) -- specs match the brief exactly
- Engagement Potential (15%) -- would someone stop scrolling?
- Structural Freshness (10%) -- different from recent posts

**Pass threshold:** weighted_score >= 3.5 per platform. Any single dimension below 2.0 triggers revision.

**Platform-specific checks:**
- Instagram: @tags for brands, hashtags, contact info, matches example tone
- GBP: zero hashtags, no phone/URL, first 150 chars standalone, consultative tone
- Facebook: fewer hashtags than IG, voice matches IG not GBP

**Output:** JSON with per-platform scores, pass/fail, specific actionable feedback, revision instructions if needed.

**Status:** Active in WF2 Social Content.

---

## 5. Blog Generator (`prompt-blog.md`)

**Purpose:** Generate blog posts for Wix website. Two content types: educational guide (600-1200 words) and job spotlight (200-400 words).

**This prompt remains detailed** because blog structure, SEO rules, and research requirements can't be taught by example alone.

**Key sections:**
- Reference blog posts (match VOICE not LENGTH -- existing posts are shorter than target)
- Structure rules (H1/H2/H3 hierarchy, paragraph length, bold-label lists)
- Tone: conversational-formal, third-grade reading level
- Technical simplification (jargon + plain English translation pattern)
- SEO rules (keyword in H1, first 2 sentences, 2+ H2s, meta description format, slug format)
- Formatting bans (no emoji, no hashtags, no single-sentence paragraphs)
- Mick's voice markers ("Let's be honest:", "Here's the kicker:", deploy 2-3 per article)
- CTA rules (end only, frame as conversation, bridge from education)
- Research rules (verify facts 3+ sources, government sites first, never fabricate)

**Output:** JSON with title, meta_description, slug, body (markdown), content_type, sources_used, facts_to_verify

**Status:** Deployed in WF3 Blog. Not yet tested.

---

## 6. Approval Parser (`prompt-approval.md`)

**Purpose:** Parse Mick's natural-language approval messages into structured per-platform actions.

**Action types:** approve, redraft, skip, hold

**Handles:**
- Simple approvals ("approve", "looks good", "send it")
- Variation selection ("option 3", "go with number 2")
- Merging ("combine 1 and 4")
- Partial approvals ("approve the social but redo the blog")
- Platform-specific edits ("make the GBP shorter")
- Photo swaps ("use this photo instead" + image)
- Holds ("hold off on that one")

**Key rules:**
- "Approve" without specifying = approve ALL pending platforms
- Redraft one platform = others go to hold (not auto-approve)
- Skip = permanent. Hold = paused.
- Ambiguous = ask for clarification

**Output:** JSON with per-platform actions, selected_variation, merge_variations, redraft_instructions, photo_swap flag, natural language response

**Status:** Deployed in WF4 Approval.

---

## 7. Q&A Agent (`prompt-qa.md`)

**Purpose:** Answer questions about posting history, schedule, images, and pending drafts.

**Tools available:**
- read_post_history (filter by platform, date, content type)
- read_schedule (posting days, times, upcoming topics)
- read_image_library (filter by folder, usage, platform)
- read_pending_drafts (current drafts awaiting approval)

**Response style:** Brief, factual, plain language. Summarise, don't dump data. Include specific numbers and dates.

**Scope boundary:** Only answers questions. If asked to create content or approve drafts, redirects to the correct action.

**Status:** Deployed in WF5 Q&A.

---

## Prompt Evolution Log

| Date | Change | Why |
|------|--------|-----|
| 2026-04-01 | Initial prompts drafted | Build kickoff |
| 2026-04-02 | Architecture designed with 6 agents | Separation of concerns |
| 2026-04-03 | Social prompt stripped to minimal + examples | 6,000-word rule-based prompt produced generic content. Examples teach voice better. |
| 2026-04-03 | GPT-4o retired, gpt-5.4-mini adopted | 400K context fits 30 examples + brief. Cost: $0.20-0.55/month. |
| 2026-04-03 | Examples moved from system to user message | User message examples have stronger influence on output. |
| 2026-04-03 | FB=IG instruction moved into JSON schema description | Eliminates separate rule; model follows schema constraints naturally. |
| 2026-04-03 | Brief richness check added pre-generation | Prevents generic content when brief is just specs. |
