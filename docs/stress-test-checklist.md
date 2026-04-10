# Stress Test Checklist — Production Readiness

Send all messages to **@TrenthamSocialsbot** in Telegram. Check off each item.

---

## Test 1: Basic Content Generation + Photo Archive
**Send a photo** of a solar install with the caption:
> "10kW solar in Daylesford, 22 Trina panels, Fronius Primo. Customer was stoked."

**Verify:**
- [ ] Preview arrives within 2 min with all fields (type, platforms, quality score, link)
- [ ] Preview page loads, shows IG/FB/GBP tabs with content
- [ ] Photo appears in Google Drive > SMA Image Library > Telegram Uploads
- [ ] Image Library table has new record (source: telegram_upload)
- [ ] Preview shows the photo you sent (not a stock image or auto-selected one)

---

## Test 2: Text-Only Post + Auto Image Selection
**Send** (no photo):
> "Educational post about why adding a battery to solar saves money during peak rates"

**Verify:**
- [ ] Classified as Educational (check the Type line in preview message)
- [ ] Auto-selected image from Drive appears in preview (not blank)
- [ ] Quality score shown
- [ ] Brief text preserved in the preview message (not paraphrased)

---

## Test 3: Approval (reply to Test 1 preview)
**Reply to the Test 1 preview message:**
> "Approve"

**Verify:**
- [ ] Telegram confirmation message received ("All platforms approved" or similar)
- [ ] Draft status in Airtable changes to "approved"
- [ ] Post appears in Buffer as a DRAFT (not published — saveToDraft is on)
- [ ] Post History table has entries for IG, FB, GBP

---

## Test 4: Partial Approval + Redraft (reply to Test 2 preview)
**Reply to the Test 2 preview message:**
> "Approve IG and Facebook but make the Google one shorter and more direct"

**Verify:**
- [ ] Telegram confirms partial approval
- [ ] A NEW preview arrives for the redrafted GBP version
- [ ] Original IG/FB route to Buffer (draft mode)
- [ ] GBP gets regenerated with the feedback incorporated

---

## Test 5: Full Redraft (reply to any pending preview)
**Reply to a preview:**
> "Nah start over. Make it more casual and mention the purple van"

**Verify:**
- [ ] Classified as draft_revision (not approval or new content)
- [ ] NEW preview arrives with revised content
- [ ] Revised version mentions "purple van" or similar
- [ ] Original draft still exists in Airtable (not deleted)

---

## Test 6: Drive Reference
**Send:**
> "Use the photos from the Solar folder in Drive to do a post about a recent install"

**Verify:**
- [ ] Classified as drive_reference
- [ ] Content generated with an image from the Solar folder
- [ ] Preview shows the Drive image

---

## Test 7: Q&A
**Send:**
> "How many posts have we published so far?"

**Verify:**
- [ ] Bot replies with an answer (not a preview)
- [ ] Answer references actual data from Airtable (post count, platforms)

---

## Test 8: Weekly Scheduler
**Fire manually** (webhook still works for this):
```
curl -X POST https://trentham.app.n8n.cloud/webhook/sma-schedule-test -H "Content-Type: application/json" -d '{}'
```

**Verify:**
- [ ] 1 autonomous post generated (educational/team/product — depends on rotation)
- [ ] 1 job spotlight prompt sent to Telegram asking Mick for photos
- [ ] Autonomous post has auto-selected image
- [ ] Summary message arrives listing what was generated

---

## Test 9: Job Spotlight Response (reply to scheduler prompt)
**After Test 8, reply to the job spotlight prompt with a photo and:**
> "8kW solar in Kyneton, Jinko panels, GoodWe inverter, Lewis did the install"

**Verify:**
- [ ] Content generated using the photo you sent
- [ ] Preview arrives with the job details
- [ ] Photo archived to Drive

---

## Test 10: Rapid Fire (stress test)
**Send 3 messages in quick succession** (within 30 seconds):
> "Post about an EV charger install in Woodend"
> "Meet the team post about Sam"  
> "Educational post about VEU rebates"

**Verify:**
- [ ] All 3 generate without errors
- [ ] All 3 previews arrive
- [ ] Each classified correctly (check Type labels)
- [ ] No duplicate drafts

---

## Test 11: Edge Cases
**Send each of these one at a time:**

> "👍" (just an emoji)
- [ ] Classified as not_for_agent or ignored gracefully

> "What's the weather like?" (irrelevant question)
- [ ] Doesn't generate a post, responds appropriately

> "Approve" (not replying to any preview)
- [ ] Doesn't approve a random draft — asks which post or says no matching draft

---

## After All Tests

- [ ] Check Airtable Pending Drafts — no orphan records without content
- [ ] Check Post History — only posts from Test 3 approval
- [ ] Check Buffer — posts are in DRAFT mode, not published
- [ ] Check Google Drive — photos from Test 1 and Test 9 in Telegram Uploads folder
- [ ] Check Image Library — new records for uploaded photos
- [ ] All 7 workflows show ACTIVE in n8n

---

## If Something Breaks

1. Check n8n execution log for the workflow that failed
2. Common issues:
   - **WF1 routing wrong**: Verify Is Approval/Revision/Q&A connections (they get overwritten)
   - **Config not loading**: Check Build Config node in the failing workflow
   - **Telegram 404**: Bot token issue in the Code node's CONFIG loader
   - **Airtable field error**: Field name mismatch (check actual table columns)
3. The webhook still works for testing: `POST https://trentham.app.n8n.cloud/webhook/sma-test-router`
