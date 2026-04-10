# Stress Test Blueprint — Blog Pipeline Production Readiness

All tests via Telegram. Reply to the bot's draft preview unless stated otherwise.

---

## Round 1: New Blog Generation + Quality Check
**Send as new message (not reply):**
> Write a blog about the benefits of battery storage for Trentham homes

**Verify:**
- [ ] Bot sends instant ack ("Got it — writing a blog about...") within seconds
- [ ] Bot sends preview link within ~60s
- [ ] Preview renders correctly (hero image, body images, SEO box, judge score)
- [ ] No duplicate images (cover != hero != body)
- [ ] Cover image is portrait
- [ ] Keyword density 4-6x (check SEO box)
- [ ] Has internal links to Trentham service pages
- [ ] Judge score shown, ideally 3.5+/5

---

## Round 2: Targeted Edits (reply to Round 1 preview)
**Test 3 edits back-to-back on the same draft:**

**2a — Add content.** Reply:
> Add a paragraph about the Victorian battery rebate being $2,950

**Verify:** Preview updates, rebate paragraph present, rest of blog unchanged.

**2b — Title change.** Reply:
> Change the title to "Why Every Trentham Home Needs Battery Storage in 2026"

**Verify:** Preview shows new title, slug updated.

**2c — Section remove.** Reply:
> Remove the section about maintenance

**Verify:** Section gone, section count reduced by 1.

---

## Round 3: Image Operations (reply to same draft)

**3a — Image swap (ambiguous).** Reply:
> Swap the image

**Verify:** Bot asks "Which image do you want to swap?" with numbered list.

**3b — Image swap (specific).** Reply:
> Swap the cover image

**Verify:** Cover image changed, preview shows different cover card.

**3c — Photo upload.** Send a photo as reply to the draft preview (any photo from camera roll).

**Verify:** Bot confirms photo uploaded, preview shows new hero image.

---

## Round 4: Approve + Publish (reply to same draft)

**4a — Approve.** Reply:
> Approve

**Verify:**
- [ ] Bot confirms approved
- [ ] Blog appears on Wix (check live site)
- [ ] Airtable status = "approved" or "published"
- [ ] **DELETE the published blog from Wix immediately after confirming**

---

## Round 5: Scheduled Publish

**Send new message:**
> Write a blog about EV charger installation for rural properties

**Wait for preview, then reply:**
> Approve for next Monday 10am

**Verify:**
- [ ] Bot confirms scheduled date (correct Monday, 10am)
- [ ] Airtable status = "approved", post_type = "scheduled"
- [ ] **Scrap this draft after verifying** (reply "scrap" so it doesn't actually publish)

---

## Round 6: Scrap Flow

**Send new message:**
> Write a blog about solar panel cleaning tips

**Wait for preview, then reply:**
> Scrap it

**Verify:**
- [ ] Bot confirms "Blog scrapped"
- [ ] Airtable status_blog = "skipped"

---

## Round 7: Bulk Blog Plan

**Send new message:**
> Plan 4 blogs for April, 1 per week

**Verify:**
- [ ] Bot sends a plan with 4 blog topics
- [ ] Topics are distinct and relevant to Trentham Electrical & Solar

**Then reply:**
> Approve all

**Verify:**
- [ ] Bot starts generating blogs one by one
- [ ] Each preview arrives separately
- [ ] **Scrap all generated blogs after verifying**

---

## Round 8: Social Post (sanity check WF2 still works)

**Send new message:**
> Do a post about a recent 6.6kW solar install in Kyneton

**Verify:**
- [ ] Social draft arrives (not blog)
- [ ] Content looks right for FB/IG/GBP
- [ ] **Scrap after verifying**

---

## Round 9: Edge Cases (quick fire)

**9a — Not-for-agent filter.** Send:
> Hey boys what time smoko?

**Verify:** Bot does NOT respond / classifies as not_for_agent.

**9b — Broad rewrite falls through.** Reply to any blog draft:
> Rewrite the whole thing from scratch

**Verify:** Triggers full WF3 regeneration (not targeted edit).

**9c — Multi-intent.** Send:
> Approve the blog and also write a new post about heat pump installs

**Verify:** Blog gets approved AND new social post is generated.

---

## Pass Criteria

- All Round 1-6 boxes checked
- Round 7 bulk plan generates correctly
- Round 8 social still works
- Round 9 edge cases handled
- No orphaned Wix posts left on live site
- No Airtable drafts left in "approved" status (scrap everything after testing)

---

## Cleanup Checklist
- [ ] Delete any test blogs from Wix
- [ ] Scrap all test drafts in Airtable (status → skipped)
- [ ] Confirm Mick's 4 original Wix blogs are untouched
