# Trentham Social Media Agent

Conversational AI assistant for end-to-end social media and blog operations for **Trentham Electrical & Solar**. Built on n8n Cloud with an AI Agent architecture (GPT-5.4-mini) driving 17 tool workflows.

Users interact entirely through Telegram (`@TrenthamSocialsV2bot`) in natural language — no commands, no magic words.

## What it does

- **Create social posts** — Instagram, Facebook, Google Business Profile (3 platform-specific variants per post)
- **Create blog posts** — SEO-optimized Wix blog articles with 4 image slots
- **Edit drafts** — text edits, image swaps, reorders, platform toggles, undo/revert — all via natural-language replies
- **Schedule posts** — "Schedule for Wed 3pm" → Buffer (social) or hourly cron (Wix blog)
- **Auto-draft weekly** — configurable weekly content calendar across topic buckets
- **Delete from schedule** — pull scheduled posts out of Buffer / Wix

## Architecture (high level)

- **1 main workflow** — `SMA-V2 Agent`, an n8n LangChain AI Agent with 9 tool sub-workflows
- **17 workflows total, 84 nodes** — no keyword routing, no IF/Switch trees for intent
- **All config in Airtable** — 29 fields per client (API keys, brand voice, schedule, content buckets). Change a row, workflows pick it up on next run.
- **Multi-client ready** — onboarding a new client is a new Airtable row + its own Telegram bot + Wix/Buffer/Drive credentials. No code changes.

## Stack

| Layer | Service |
|---|---|
| Orchestration | n8n Cloud |
| LLM | OpenAI `gpt-5.4-mini` |
| User interface | Telegram Bot API |
| Social publishing | Buffer V2 GraphQL (IG, FB, GBP) |
| Blog publishing | Wix Blog v3 API |
| Image library | Google Drive |
| State | Airtable (drafts, config, history, examples, image rotation) |
| Preview pages | Vercel |

## Repo contents

| Path | What's in it |
|---|---|
| `docs/` | Architecture docs, session reports, stress test plans, presentation brief |
| `docs/presentation-brief.md` | Fact-verified 9-slide brief for client walkthrough |
| `brand-guides/` | Brand voice guides and LLM prompt reference |
| `preview-app/`, `v2-preview-app/` | Social post preview (Vercel) |
| `preview-site/` | Wix blog post preview (Vercel) |
| `CLAUDE.md` | Project conventions and workflow IDs |

## What's NOT in this repo

- The n8n workflows themselves — they live in the client's n8n Cloud instance
- Deploy scripts — these hardcoded API keys during rapid iteration; left local
- API keys and credentials — all loaded from Airtable at runtime

## Key learnings (n8n-specific)

- Code tools (`toolCode`) silently fail inside AI Agent nodes — use Workflow Tools (`toolWorkflow`) instead
- Switch nodes silently drop unmatched messages — use explicit IF chains or push routing into GPT
- Buffer memory can poison an AI Agent into a bad loop — use fresh session keys
- Duplicate node names break connection resolution — always camelCase unique names
- Node names with spaces break Telegram webhook URLs

See `CLAUDE.md` for the full list.

## Status

Currently in final stress-testing before client go-live.
