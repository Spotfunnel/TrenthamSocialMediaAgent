# Plan: Hybrid Architecture — Sub-Workflows Send to Telegram Directly

## The Problem

n8n's AI Agent **always summarizes tool responses**. This is a known platform limitation with no fix:
- [Feature request](https://community.n8n.io/t/allow-ai-agents-to-return-the-original-output-instead-of-summarizing/46179)
- [Community thread](https://community.n8n.io/t/ai-agent-how-to-simply-return-the-tool-output-without-reformatting-reinterpreting-it/83248) — one user abandoned agent-relays-tool-output entirely
- [Community recommendation](https://community.n8n.io/t/help-ai-agent-with-two-telegram-tools-either-returns-bad-request-or-sends-no-message-at-all/263139): "The AI Agent is the Brain, not the Hands"
- [n8n Production Playbook](https://blog.n8n.io/production-ai-playbook-deterministic-steps-ai-steps/): "Use AI only where you need AI"

Always Reply tries to compensate by querying Airtable for the "newest pending draft" — but grabs the wrong one when multiple drafts exist, showing wrong preview links, wrong topics, wrong platforms.

## The Fix: Two Output Paths

Every interaction falls into one of two categories:

| Category | Examples | Who sends to Telegram? | Why? |
|----------|----------|----------------------|------|
| **Write ops** | Create post, blog, edit draft, plan weekly | **Sub-workflow** | It knows the exact draft ID, preview link, platforms. Deterministic. |
| **Read ops + conversation** | Lookup drafts, search drive, "hi", "what can you do?" | **Agent via ReplyGate** | Agent summary is the correct response. No precise data to lose. |

### Architecture

```
TelegramTrigger → LoadConfig → AI Agent → ReplyGate → Telegram Send
                                  |
                           [calls tools]
                                  |
                   ┌──────────────┼───────────────┐
                   ↓              ↓               ↓
            SocialGenerator  LookupDrafts    (no tool)
            sends Telegram   returns data    agent responds
            returns "DONE"   agent summarizes  directly
                   ↓              ↓               ↓
             ReplyGate:       ReplyGate:      ReplyGate:
             SKIP (DONE)      SEND summary    SEND response
```

### How It Works

1. **Write tools** (Social Generator, Blog Generator, Edit Draft, Weekly Planner):
   - Do their work (create draft, edit, etc.)
   - Send a formatted Telegram message directly with the correct draft ID and preview link
   - Return `{response: "DONE"}` to the agent
   - Agent's system prompt says: "When a tool responds DONE, output: DONE"
   - ReplyGate sees "DONE" → skips (no duplicate message)

2. **Read tools** (Lookup Drafts, Search Drive):
   - Return data to agent as before (no change)
   - Agent summarizes naturally ("You have 3 pending drafts...")
   - ReplyGate sends the agent's summary to Telegram

3. **Conversational** (greetings, capabilities, Q&A):
   - No tool called
   - Agent generates its own response
   - ReplyGate sends it to Telegram

### ReplyGate (replaces Always Reply)

```javascript
var output = ($input.first().json.output || '').trim();
var config = {};
var chatId = '';
try {
  config = $('V2 Load Config').first().json.config || {};
  chatId = $('V2 Load Config').first().json.chat_id || '';
} catch(e) {}
var token = config.telegram_bot_token || '';

// Skip if tool already sent, or nothing to say
if (!output || output === 'DONE' || !token || !chatId) {
  return [{ json: { sent: false, reason: output === 'DONE' ? 'tool_sent' : 'empty' } }];
}

// Send agent's response to Telegram
var resp = await this.helpers.httpRequest({
  method: 'POST',
  url: 'https://api.telegram.org/bot' + token + '/sendMessage',
  body: { chat_id: chatId, text: output },
  json: true
});

return [{ json: { sent: resp.ok, message_id: resp.result ? resp.result.message_id : null } }];
```

### How Sub-Workflows Get chat_id and bot_token

**Problem:** Sub-workflows can't reference `$('V2 Load Config')` — that node is in the main workflow.

**Solution:** Sub-workflows already fetch config from Airtable (they need the OpenAI key anyway). They already have `config.telegram_bot_token` and `config.telegram_chat_id`. No extra wiring needed.

### Double Message Safety

- If agent follows prompt and says "DONE" → ReplyGate skips → 1 message (from tool)
- If agent doesn't follow prompt and says "I've created your post!" → ReplyGate sends it → 2 messages (detailed from tool + brief from agent). **Annoying but not broken** — the correct preview link was already sent.
- If tool's Telegram send fails → tool returns error → agent relays error → ReplyGate sends error to user. **Graceful degradation.**

### What Changes

| Component | Current | New |
|-----------|---------|-----|
| Social Generator `GenerateWithImage` | Returns `{response: "Draft created!\nPreview: ..."}` | Sends Telegram message, returns `{response: "DONE"}` |
| Blog Generator `GenerateBlog` | Returns `{response: "Blog created!\nPreview: ..."}` | Sends Telegram message, returns `{response: "DONE"}` |
| Edit Draft `EditDraft` | Returns `{response: "Caption updated.\nPreview: ..."}` | Sends Telegram message, returns `{response: "DONE"}` |
| Weekly Planner `PlanWeek` | Returns `{response: "Planned 3 posts..."}` | Sends Telegram message, returns `{response: "DONE"}` |
| Lookup Drafts | Returns draft list to agent | **No change** |
| Search Drive | Returns image list to agent | **No change** |
| Always Reply | 100+ lines, queries Airtable, overrides agent | **ReplyGate**: ~15 lines, simple passthrough with DONE filter |
| Agent system prompt | Generic | Adds: "When a tool responds DONE, output: DONE" |

### Implementation Steps

1. Update Social Generator: add Telegram send after draft save, return DONE
2. Update Blog Generator: same
3. Update Edit Draft: same
4. Update Weekly Planner: same
5. Rewrite Always Reply as ReplyGate
6. Update agent system prompt
7. Deploy all changes
8. Test each flow end-to-end

### What NOT to Change

- Lookup Drafts — agent summary is correct behavior
- Search Drive — agent summary is correct behavior
- Publish — not tested yet, leave for later
- Send Telegram (toolCode) — can be removed later, not urgent
