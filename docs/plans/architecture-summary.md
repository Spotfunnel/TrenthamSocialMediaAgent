# Architecture Summary

> Full detail: [2026-04-02-agent-architecture.md](2026-04-02-agent-architecture.md)
> Build status as of: 2026-04-03

## The System in One Diagram

```
        Mick sends anything to Telegram
                    |
                    v
        +---------------------------+
        |   AI CLASSIFIER           |  Every message. Understands
        |   (gpt-5.4-mini)         |  multi-intent, photo context,
        |                           |  draft references, natural language
        +---+---+---+---+---+------+
            |   |   |   |   |
            v   v   v   v   v
         Social Blog Approval Q&A Schedule
         Agent  Agent Agent  Agent (cron)
            |   |
            v   v
        +-----------+
        |  JUDGE    |  Scores quality before
        |  AGENT    |  Mick ever sees it
        +-----+-----+
              |
              v
         Telegram (draft for approval)
              |
              v
         Publisher -> Buffer / GBP API / Wix
```

## Current Build Status (2026-04-03)

| Component | Status | Notes |
|-----------|--------|-------|
| WF1 Router | Deployed | Webhook trigger for testing (Telegram trigger to be reconnected) |
| WF2 Social Content | **Working end-to-end** | Brief check -> examples -> GPT-5.4-mini -> judge -> Telegram |
| WF3 Blog | Deployed | Not tested yet |
| WF4 Approval | Deployed | Connected to WF7 publisher and WF2 redraft |
| WF5 Q&A | Deployed | Not tested yet |
| WF6 Scheduler | Deployed | Not tested yet |
| WF7 Publisher | Deployed | Buffer for FB/IG live, GBP and Wix placeholders |
| Airtable | **Live** | 7 tables in dedicated base |
| Credentials | **All in n8n** | Telegram, OpenAI, Airtable, Drive, Buffer |

**Total: 7 workflows, 116+ nodes deployed.**

## Key Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| **Model** | gpt-5.4-mini everywhere | 400K context, vision, $0.20-0.55/month total. GPT-4o retired. |
| **Prompt strategy** | Minimal prompt + 30 real examples in USER message | Rules flatten voice. Examples teach it. One-line system message. |
| **Examples placement** | USER message, not system message | System message examples have weaker influence. Proven via direct API test. |
| **Brief richness check** | Agent asks for story if brief is too thin | "Got the specs. Anything interesting about this job?" prevents generic content. |
| **Social agents** | One agent -> 3 platform outputs (IG + GBP + FB) | Single structured JSON call. GBP gets consultative tone, no hashtags. |
| **FB = IG** | Same caption, fewer hashtags | Instruction embedded in JSON output schema description. Don't rewrite. |
| **Routing** | AI classifier on every message | Mick talks naturally. Multi-intent supported. |
| **Blog agent** | Separate, with research tool | Completely different task. Needs web search + fact verification. |
| **Quality gate** | Separate Judge agent on all content | No grading your own homework. Swap test catches generic slop. |
| **Multi-variation** | Built in -- "give me 5 options" works | Agent generates N variations with different hooks/structures. |
| **Approval** | Natural language -- "approve all except blog" | Classifier already knows what Mick means. |
| **State** | Airtable for everything | Drafts, history, conversation, images, examples, config. |
| **Publishing** | Buffer for FB/IG, GBP API direct, Wix API direct | Buffer handles Meta auth complexity. |

## Critical Learning: The Prompt Overload Lesson

We started with 6,000+ word brand guides with 34 rules, vocabulary lists, emoji guides, hashtag counts, and tone spectrums. The AI averaged everything into generic corporate content.

**The fix:** Strip all rules, load 30 real posts as examples, one-line system message. The examples teach the voice implicitly. The model extracts patterns itself rather than following a checklist. Content quality jumped dramatically.

**Only surviving explicit rules:**
- Spec accuracy (use the brief exactly)
- Don't copy examples
- FB = IG minus hashtags
- GBP formatting differences

## 6 Agents

| Agent | What it does | When |
|-------|-------------|------|
| **Classifier** | Understands intent, platforms, photo purpose, draft refs | Every message |
| **Social Content** | Generates IG + GBP + FB from one brief | Per content request |
| **Blog Content** | Researches + writes 600-1800 word articles | Per blog request |
| **Judge** | Scores on 5 dimensions, rejects generic content | After every generation |
| **Approval** | Parses "approve", "skip blog", "option 3", "combine 1+4" | Per approval message |
| **Q&A** | Answers "what did we post?" using Airtable tools | Per question |

## 7 Workflows

| WF | ID | Name | AI? | Status |
|----|----|------|-----|--------|
| 1 | 4p3NQbRQpRwCBZzG | Intelligent Router | Yes (classifier) | Deployed |
| 2 | 3jxUdiGw049BLCVh | Social Content Gen | Yes (content + judge) | **Working** |
| 3 | bHoB1SprYKbSjInk | Blog Generation | Yes (research + content + judge) | Deployed |
| 4 | OykBD1JVgJAK3dcj | Approval Flow | Yes (approval parser) | Deployed |
| 5 | FEPuOJHELAObLuxD | Q&A | Yes (with Airtable tools) | Deployed |
| 6 | EDQFZF6vViRvh6gC | Autonomous Scheduler | No (cron + planner) | Deployed |
| 7 | 2suYnYb764NmhtQr | Publisher | No (API calls) | Deployed |

## Airtable

- **Base:** app3fWPgMxZlPYSgA
- **Tables:** Master Config, Pending Drafts, Conversation Messages, Post History, Image Library, Example Bank, Schedule Config

## Cost

**~$0.20-0.55/month** total API cost. All infrastructure already exists.

## What's Left

1. Reconnect Telegram trigger (currently webhook for testing)
2. Blog agent testing and prompt tuning
3. Approval flow end-to-end testing
4. Publisher testing (Buffer, GBP, Wix)
5. Scheduler testing
6. Remove n8n watermark from Telegram messages (n8n Cloud setting)
7. Google Drive folder structure creation
8. Image handling (upload, categorise, select for posts)
9. Multi-variation mode testing
10. Photo-based posts (vision API integration)
