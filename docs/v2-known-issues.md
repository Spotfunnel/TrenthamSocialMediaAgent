# V2 Known Issues — 2026-04-08 (Updated)

---

## FIXED: Always Reply Node — Replaced with Hybrid Architecture

**Status:** FIXED (2026-04-08)
**Solution:** Sub-workflows now send Telegram messages directly with the correct draft ID. Always Reply replaced with "ReplyGate" — a 15-line passthrough that only sends the agent's output for conversational messages. Write tools return DONE, ReplyGate skips.
**Plan:** `docs/plans/2026-04-08-always-reply-fix.md`
**Test results:** All flows verified — create post, blog, edit, lookup, conversational all produce exactly ONE correct message.

---

## FIXED: Wrong Preview Links in Telegram

**Status:** FIXED (2026-04-08)
**Was:** Always Reply queried Airtable for "newest pending draft" and grabbed wrong one
**Fix:** Each sub-workflow sends its own Telegram message using the draft ID it just created. No guessing.

---

## FIXED: Agent Ignores Lookup Tool Data

**Status:** FIXED (2026-04-08)
**Was:** Agent received "6 drafts found: ..." from lookup_drafts but told user "no pending drafts"
**Root cause:** Known n8n agent issue — agent produces empty output or contradicts tool data
**Fix:** Lookup tool now sends to Telegram directly (same hybrid pattern as write tools)

---

## FIXED: Blog Topic Lost Through DriveSearch Pipeline

**Status:** FIXED (2026-04-08)
**Was:** Blog Generator returned "No blog topic provided" because SearchDriveImages node lost the topic field
**Fix:** GenerateBlog now reads topic from `$('ClassifyFolder')` instead of `$input`

---

## FIXED: GBP "More" Button Broken

**Status:** FIXED (2026-04-08) — Added onclick handler that shows full text and hides truncated version.

**Location:** `v2-preview-app/index.html` line 482 and the `gbpHTML` function
**Problem:** GBP text truncated at 200 chars with `b.slice(0, 200)`. A "More" span is rendered with `cursor: pointer` but NO JavaScript click handler. Clicking does nothing.
**Full GBP content:** 491 chars / 78 words (for the Woodend solar post). Only 200 chars shown.
**Fix:** Add onclick handler to expand the text, or increase the truncation limit, or remove truncation entirely for preview purposes.

---

## FIXED: Too Many Paragraphs

**Status:** FIXED (2026-04-08) — Added paragraph structure rules to GPT system prompt: "3-5 paragraphs max, flowing paragraphs 30-50 words each, contact+hashtags at end of final paragraph."

**Example:** BBQ post (recIbQY9rn0StIbGI) IG caption:
```
🍖☀️ Team BBQ, Trentham style! 🌿          ← P1: opening (6 words)

Last Friday we swapped the tools...   ← P2: body (25 words)

Days like this matter...               ← P3: reflection (22 words)

At Trentham Electrical & Solar...      ← P4: brand (22 words)

Thanks to everyone...                  ← P5: thanks (13 words)

If you're looking for a local team...  ← P6: CTA (17 words)

🌐 www... 📞 1300...                   ← P7: contact (4 words)

#TrenthamElectrical...                 ← P8: hashtags (10 words)
```
**8 paragraphs for 143 words = 18 words per paragraph average**

**Mick's real posts (from Example Bank, 70 posts):**
- Average: 138 words, typically 3-5 substantial paragraphs
- Mick writes flowing paragraphs, not single-sentence breaks
- Contact info and hashtags are part of the last paragraph, not separate

**Root cause:** GPT prompt doesn't specify paragraph structure. GPT-5.4-mini defaults to many short paragraphs with double line breaks between every thought.
**Fix:** Add to Social Generator system prompt: "Use 3-5 paragraphs maximum. Write flowing paragraphs, not single sentences. Contact info and hashtags go at the end of the last paragraph, not as separate blocks."

---

## FIXED: FB Identical to IG

**Status:** FIXED (2026-04-08) — Added post-processing: if FB caption matches IG, FB hashtags are trimmed to first 6. Also added explicit prompt instruction for FB to use 5-6 hashtags.

**Example:** BBQ post (recIbQY9rn0StIbGI):
- IG: 868 chars — full caption with 10 hashtags
- FB: 868 chars — EXACT SAME TEXT, byte for byte identical

**Also on Woodend post (rec1VHbUVs57wrkFW):**
- IG: 741 chars
- FB: 741 chars — identical again

**Should be:** FB should have fewer hashtags (5-8 instead of 10+) and potentially a slightly different opening. Real Mick FB posts are similar to IG but shorter hashtag blocks.
**Root cause:** The Social Generator prompt says "Facebook version (like Instagram but fewer hashtags)" but GPT sometimes returns identical content for both.
**Fix:** Add explicit post-processing in the GenerateWithImage code: after generation, strip IG hashtags from FB and keep only first 5-6. Or add a more explicit instruction in the prompt.

---

## FIXED: Demo Post Fallback for Deleted Drafts

**Status:** FIXED (2026-04-08) — Replaced fake demo content with "This draft has been deleted or could not be found" message. Only shows IG tab with error text.

**Example:** `rec78jMaH5t96UceK` was deleted during testing cleanup. When opening:
`https://v2-preview-app.vercel.app?id=rec78jMaH5t96UceK`

It shows:
- Label: "DEMO POST"
- Caption: "Another tidy solar install in Daylesford... Thinking about solar? Let's chat."
- Only 4 hashtags, no image, ~20 words
- Looks like a real (bad) post — confusing

**Location:** `v2-preview-app/index.html` lines 718-722 — hardcoded fallback demo data returned when API returns no draft
**Problem:** User follows a link from Telegram, sees fake content, thinks the post is terrible. Should show "This draft has been deleted or not found" instead of demo content.

---

## FIXED: Label Truncated in Preview Header

**Status:** FIXED (2026-04-08) — Increased from 80 to 150 chars in `v2-preview-app/api/draft.js`.

**Example:** "CREATE A SOCIAL MEDIA POST ABOUT OUR 10KW SOLAR INSTALL IN WOODEND. INCLUDE THAT" — cut off at 80 chars
**Location:** `v2-preview-app/api/draft.js` line 43: `(f.content_brief || 'Post Preview').substring(0, 80)`
**Additional problem:** The label shows the agent's rewritten brief (system-formatted), not the user's original text
**Fix:** Increase to 120 chars, or use a different field for the label

---

## FIXED: Blog Needs 2 Images (Not 1)

**Status:** FIXED (2026-04-08)
**Solution:** GenerateBlog now picks 2 unused images from Drive search results, saves comma-separated in `image_url` field. Blog preview server splits on comma, renders image[0] as hero at top, image[1] injected after 3rd H2 section. Verified: "Images: 2 auto-selected" in Telegram message, preview renders both correctly.

---

## PARTIALLY FIXED: Edit Draft Grabs Wrong Draft

**Infrastructure done (2026-04-08):**
- Social Generator and Blog Generator now save `telegram_message_id` on draft records after sending to Telegram
- EditDraft code has reply-to-message lookup: queries Airtable for draft with matching `telegram_message_id`
- Fallback: still uses most-recent-pending if no match

**Remaining issue:** The `reply_to_message_id` from the main workflow's Load Config can't be reliably passed to the EditDraft sub-workflow. Approaches tried and failed:
1. `$('V2 Load Config').item.json.reply_to_message_id` in toolWorkflow inputs — doesn't resolve (parent node not accessible)
2. `$json.reply_to_message_id` — `$json` in tool context is agent internal state, not Load Config output
3. `$fromAI('reply_to_message_id')` — agent model (gpt-5.4-mini) doesn't reliably extract the reply ID from system prompt context and pass it as a parameter

**The infrastructure is ready.** The only missing piece is getting the reply_to_message_id from Load Config into the EditDraft tool input. Options:
- **Pre-agent Code node** that reformats the message to include the reply ID in the user text itself
- **Custom n8n node** or plugin that can pass parent workflow context to child workflows
- **Wait for n8n to support** parent node references in toolWorkflow inputs

When only 1 pending draft exists, this isn't an issue — EditDraft finds it via fallback. The bug only manifests when multiple drafts are pending simultaneously.

---

## OPEN: Content Length Variation

**Mick's real posts:** 77-238 words, median 142, average 138
**Generated posts:** 111-143 words — within range but inconsistent
**Not a critical bug:** The variation matches Mick's real range. But could be more consistent by targeting 130-160 words.

---

## Working Correctly (Verified 2026-04-08)

- Social post creation with IG + FB + GBP content ✅
- Platform filtering (IG+FB only, IG only) ✅
- Drive image auto-selection by folder ✅
- Image LRU (no repeats across posts) ✅ FIXED — was broken (no logging), now PostProcess+SaveAndSend write to Used Images table
- Draft editing (applies edit correctly when right draft found) ✅
- GBP removal via edit ✅
- Blog generation (850+ words, 7 H2s, meta/slug/keyword) ✅
- Blog preview rendering (Wix fonts, proper layout, 2 images) ✅ UPDATED
- Blog 2 images (hero + body, auto-selected from Drive) ✅ NEW
- Weekly planner (topic rotation advances) ✅
- Lookup drafts (sends correct count + list to Telegram directly) ✅
- Vague brief handling (asks for detail) ✅
- Conversational responses (hi, capabilities) ✅
- telegram_message_id saved on drafts for reply tracking ✅ NEW
- GBP "More" button working (onclick expand) ✅ FIXED
- Deleted draft fallback (shows error, not fake content) ✅ FIXED
- Label shows full brief (150 chars, up from 80) ✅ FIXED
- 3-5 paragraph structure in generated posts ✅ FIXED
- FB has fewer hashtags than IG (max 6 via post-processing) ✅ FIXED
- Preview page IG tab rendering ✅
- Preview page GBP tab rendering ✅ FIXED
- Preview page FB tab rendering ✅
- Preview page platform tab hiding when content null ✅
- Hybrid architecture: ONE message per interaction, correct preview links ✅

---

## V2 Architecture Reference (Updated)

### Main Workflow: SMA-V2 Agent (`joOvKKDolWpOTLdP`) — 15 nodes
- TelegramTriggerV2 → V2 Load Config → V2 Agent → V2 ReplyGate (was Always Reply)
- V2 OpenAI (sub-node), V2 Lookup Drafts (tool), V2 Create Social Post (tool), V2 Edit Draft (tool), V2 Create Blog (tool), V2 Publish (tool), V2 Plan Weekly (tool), V2 Search Drive (tool)
- V2ScheduleTrigger → V2 Cron Input → V2 Agent

### Hybrid Architecture Flow
```
Write tools (create, edit, blog, plan, lookup):
  Tool does work → Tool sends Telegram directly → Returns DONE → ReplyGate skips

Conversational (hi, capabilities, Q&A):
  Agent responds → ReplyGate sends to Telegram
```

### Sub-Workflows
| Workflow | ID | Nodes | Sends TG? |
|----------|-----|-------|-----------|
| SMA-V2 Social Generator | `eIWk6RjvYP2lgDlI` | 4 | Yes |
| SMA-V2 BlogGenerator | `uHELgth7y2dIq3Ft` | 4 | Yes |
| SMA-V2 DriveImageSearch | `B9aee5u4h9UTzBcM` | 6 | No |
| SMA-V2 EditDraft | `YZq8YMqeaHxht5Xk` | 2 | Yes |
| SMA-V2 Publisher | `RKbtyZ6AMO5sYYjx` | 2 | Not tested |
| SMA-V2 WeeklyPlanner | `kGSN5w3lzNsncE37` | 2 | Yes |
| SMA-V2 LookupDrafts | `quswMumV1Ks7UK0B` | 2 | Yes |
| SMA-V2 SendTelegram | `fS2F2MiHdiBfAtnB` | 2 | N/A (is the sender) |

### Airtable (same base as V1: `app3fWPgMxZlPYSgA`)
| Table | ID |
|-------|-----|
| V2 Config | `tbleVI4pkVedNuQth` |
| V2 Drafts | `tblhwcZsM7wh85HFq` |
| V2 Post History | `tblSEGhWxj3xRHKvC` |
| V2 Example Bank | `tblOHBbTZG0cSyeCc` |
| V2 Used Images | `tblesyONTANz0axVG` |

### Credentials
- V2 Telegram Bot: `MUO6sWlMxWZJVzhF`
- OpenAI: `xHFLs3Ij7SByfVgz`
- Google Drive OAuth2: `mvjZMzva9gEEkFMt`
