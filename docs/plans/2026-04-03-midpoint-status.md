# Social Media Agent - Midpoint Status
## 2026-04-03

## What's Working

**WF1 Router + WF2 Social Content Generation = end-to-end functional.**

The core pipeline works:
1. Message comes in via webhook (Telegram trigger to be reconnected)
2. AI classifier identifies intent, platforms, extracts brief
3. Brief richness check - asks for story if too thin
4. Social content agent generates IG + GBP posts (FB copied from IG programmatically)
5. Judge agent scores quality
6. Previews sent to Telegram (one message per platform)
7. Draft saved to Airtable

**Content quality is good across multiple post types:**
- Install showcase with story (107w) - purple van, neighbour referral, tricky roof, named team member
- Team introduction (84w) - new apprentice, personal details, community angle
- Rebate urgency (103w) - deadline, specific figures, local references
- Educational (105w) - battery storage for storm season, practical framing

## The Prompt Strategy That Works

**System message (268 chars):**
```
You write Instagram posts for Trentham Electrical & Solar. Match the voice of the 
reference posts exactly. IMPORTANT: Keep posts SHORT. 50-120 words before hashtags. 
Most reference posts are under 100 words. Cut ruthlessly. No padding, no waffle, 
no filler paragraphs.
```

**User message (~33K chars):**
- 30 real Instagram posts as examples
- Brief + output format JSON schema
- "Don't copy examples, write original content in the same voice"
- "Use specs from brief exactly"
- FB schema says "Same caption as Instagram, just reduce hashtags"

**Key: examples in USER message, not system. Length constraint in SYSTEM message.**

## FB = IG Fix

FB caption is now copied programmatically in the Parse Social Output code node. The model only generates IG and GBP. FB is IG with hashtags trimmed to 8. This guarantees consistency.

## Brief Richness Check

Before generating, a quick GPT call checks if the brief has enough story/angle. If thin (just specs), the agent asks:
"Got the specs. Anything interesting about this job that'd make the post stand out? A story or angle always helps."

If rich (has narrative detail), generates immediately.

## What's Deployed but Not Tested

| Workflow | Status |
|----------|--------|
| WF3 Blog Generation | Deployed, needs testing + prompt tuning |
| WF4 Approval Flow | Deployed, connected to WF7 + WF2, needs testing |
| WF5 Q&A Agent | Deployed, needs testing |
| WF6 Scheduler | Deployed, needs testing |
| WF7 Publisher | Deployed, Buffer connected, GBP + Wix placeholders |

## What's Left To Do

1. Reconnect Telegram trigger (currently webhook for testing)
2. Blog agent testing and prompt tuning (minimal prompt + examples approach)
3. Approval flow end-to-end testing
4. Publisher testing (Buffer, GBP, Wix)
5. Scheduler testing
6. Remove n8n watermark from Telegram messages
7. Google Drive folder structure creation
8. Image handling (upload, categorise, select for posts)
9. Multi-variation mode testing ("give me 5 options")
10. Photo-based posts (vision API integration)
11. Pass original message text through to content agent (not classifier's rewrite)

## Key Learnings

1. **Examples > rules.** 30 real posts teach the voice better than 6,000 words of brand guide rules.
2. **Examples in user message > system message.** User message content carries more weight.
3. **Length constraint in system message.** The only rule that works in system - everything else goes in user with examples.
4. **FB should be programmatic, not generated.** The model always rewrites FB differently. Code node copy is reliable.
5. **Brief richness matters more than prompt quality.** A detailed brief with story produces dramatically better posts than any prompt tuning on bare specs.
6. **n8n expression issues.** Bash eats $, large payloads need temp files, Code nodes use $input not $().

## Workflow IDs

- WF1: 4p3NQbRQpRwCBZzG (webhook trigger active)
- WF2: 3jxUdiGw049BLCVh
- WF3: bHoB1SprYKbSjInk
- WF4: OykBD1JVgJAK3dcj
- WF5: FEPuOJHELAObLuxD
- WF6: EDQFZF6vViRvh6gC
- WF7: 2suYnYb764NmhtQr
