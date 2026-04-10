# CLAUDE.md — Project Instructions

## Quality Standard
**This is a client deliverable. No cutting corners. No "good enough" mentality.**
- Fix every bug before moving to the next feature
- Test every feature end-to-end via Playwright + n8n API before claiming it works
- Always look for faults and errors — verify, don't assume
- Never say "check it" without having verified it yourself first
- If you deploy a page, fetch it and verify it renders
- If you generate content, read it back
- If you update a workflow, check the execution results

## Buffer / Social Media Publishing Rule
**NEVER publish to real social media accounts without EXPLICIT permission from Leo.**
**NEVER call the publish_post tool or V2 Publisher workflow during testing.**
- Buffer publishing is OFF LIMITS unless Leo explicitly says to test it
- Use `saveToDraft: true` if ever testing — but don't test without permission
- Blog publishing to Wix: OK for testing but inspect, note issues, then delete immediately
- Do not touch or delete any of Mick's existing content

## Project: Social Media Agent for Trentham Electrical & Solar
- n8n cloud instance: https://trentham.app.n8n.cloud
- Blog preview: https://preview-site-inky.vercel.app/?id={recordId}
- Social preview: https://preview-app-amber.vercel.app?id={draftId}
- Do NOT publish previews to Wix — Wix publishing is only for final approved posts

---

## V1 (Legacy — DO NOT MODIFY)

V1 uses @TrenthamSocialsbot with 7 workflows (WF1-WF7). It stays untouched as a fallback. V2 is the active build.

### V1 Key Info (reference only)
- WF1 Router: `4p3NQbRQpRwCBZzG` — 45 nodes, IF-based routing
- WF2 Social Generator: `3jxUdiGw049BLCVh`
- WF3 Blog Generator: `bHoB1SprYKbSjInk`
- WF4 Approval: `OykBD1JVgJAK3dcj`
- WF5 Q&A: `FEPuOJHELAObLuxD`
- WF6 Scheduler: `EDQFZF6vViRvh6gC`
- WF7 Publisher: `2suYnYb764NmhtQr`
- Airtable base: `app3fWPgMxZlPYSgA` (shared with V2)

---

## V2 REBUILD (AI Agent Architecture) — ACTIVE BUILD

### V2 Bot
- Telegram bot: @TrenthamSocialsV2bot
- n8n credential: `MUO6sWlMxWZJVzhF` ("V2 Telegram Bot")
- OpenAI credential: `xHFLs3Ij7SByfVgz` ("Mick OpenAI")

### V2 Architecture
- **1 main workflow** (`SMA-V2 Agent`, id: `joOvKKDolWpOTLdP`) — AI Agent with tools
- **Sub-workflows called as Workflow Tools** — each is a `toolWorkflow` on the agent
- Agent uses gpt-5.4-mini, temperature 0.3
- Agent output auto-sent to Telegram via "V2 Always Reply" post-agent node
- No memory currently (removed due to context poisoning — re-add with fresh session key later)

### V2 Airtable (same base as v1: `app3fWPgMxZlPYSgA`)
| Table | ID | Purpose |
|-------|-----|---------|
| V2 Config | `tbleVI4pkVedNuQth` | Per-client config (keys, brand voice, schedule) |
| V2 Drafts | `tblhwcZsM7wh85HFq` | All drafts (social + blog) |
| V2 Post History | `tblSEGhWxj3xRHKvC` | Published posts log |
| V2 Example Bank | `tblOHBbTZG0cSyeCc` | Real posts for voice matching |
| V2 Used Images | `tblesyONTANz0axVG` | Drive image usage tracking |

### V2 Sub-Workflows
| Workflow | ID | Purpose |
|----------|-----|---------|
| SMA-V2 Agent | `joOvKKDolWpOTLdP` | Main agent workflow |
| SMA-V2 SendTelegram | `fS2F2MiHdiBfAtnB` | Send Telegram messages (ack tool) |
| SMA-V2 LookupDrafts | `quswMumV1Ks7UK0B` | Query V2 Drafts table |
| SMA-V2 Social Generator | `eIWk6RjvYP2lgDlI` | Generate IG + FB + GBP content |

### V2 n8n Patterns (hard-won lessons)
- **Code Tools (`toolCode`) DON'T WORK** — `this.helpers.httpRequest` fails inside them. Always use Workflow Tools (`toolWorkflow`) with a sub-workflow instead.
- **Agent output goes to "Always Reply" node** — a post-agent Code node sends `$json.output` to Telegram. Don't rely on the agent calling a send tool.
- **Sub-workflows must be active** — `executeWorkflow` tools fail silently if the target is inactive.
- **Memory can poison the agent** — if the agent gets into a bad loop, buffer memory reinforces it. Use fresh session keys or disable memory to recover.
- **`$fromAI` inputs arrive as `query` field** — sub-workflow trigger receives `{query: "..."}`, not named fields. Always read from `input.query || input.brief || ''`.
- **Node names with spaces break Telegram webhook URLs** — use camelCase (e.g. `TelegramTriggerV2` not `V2 Telegram Trigger`).
- **Duplicate node names cause routing corruption** — n8n resolves connections by name. Never have two nodes with the same name in one workflow.
- **`returnIntermediateSteps` may break tool observation relay** — test with it off first.
- **Don't deactivate v1** — v2 is fully separate (different bot, different tables).

### V2 Design Docs
- `docs/plans/2026-04-07-v2-rebuild-design.md` — full architecture
- `docs/plans/2026-04-07-v2-implementation-plan.md` — 20-task build plan
- `scripts/v2/airtable_ids.json` — all V2 table IDs
- `scripts/v2/workflow_ids.json` — all V2 workflow IDs

### V2 Deploy Pattern
- Python scripts in `scripts/v2/` folder
- Write JSON payload to temp file, `curl -d @file`
- For main workflow: PUT without deactivating (preserves Telegram webhook)
- For sub-workflows: can deactivate/reactivate safely
- After every deploy: test via Playwright on Telegram Web AND check n8n execution API
