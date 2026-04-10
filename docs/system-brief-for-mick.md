# Your Social Media Agent — How It Works

Hey Mick, here's a rundown of the system Leo's built for you. It handles your social media and blog content across Instagram, Facebook, and Google Business Profile — all through Telegram.

---

## The Big Picture

You send a message or photo to the Telegram bot. The agent figures out what you want, creates the content, shows you a preview, and once you approve it, publishes it to all your platforms through Buffer. You can also set it to generate posts automatically each week without you lifting a finger.

Everything runs on your existing n8n instance. Nothing new to log into — you just talk to the bot.

---

## How You Use It

### Creating a Post

Send the bot a message with some details about a job:

> "Do a post about the 10kW solar install in Daylesford. 22 Trina panels and a Fronius Primo. Sam did a great job."

If you've got photos, send them too. The agent will:

1. Save your photos to Google Drive automatically
2. Write captions for Instagram, Facebook, and Google Business Profile
3. Score the content for quality
4. Send you a preview link you can tap to see how it'll look on each platform

The preview shows you the actual post as it would appear on Instagram, Facebook, and GBP — with swipeable tabs between platforms.

### Approving or Editing

When you get a preview, just **reply to that specific message** in Telegram:

- **"Approve"** — publishes to all three platforms via Buffer
- **"Approve IG and Facebook but redo the Google one, make it shorter"** — publishes the ones you like, rewrites the one you don't
- **"Make it more casual"** — rewrites the whole thing with your feedback
- **"Swap the image"** — quick edit without rewriting the caption

You can have 10 or 20 drafts sitting there and the bot knows exactly which one you're talking about based on which preview you reply to.

### Using Photos from Google Drive

If you've already got photos in Drive, you can say:

> "Use the photos from the Solar folder to make a post"

The agent will grab images from the right folder and generate content using them.

---

## The Weekly Scheduler

The agent can generate posts automatically each week. You control everything from one row in Airtable:

- **Posts per week**: Set it to 2, 3, 4, or 5
- **Post time**: What time of day posts go out (e.g. 9:00 AM)
- **Content rotation**: What types of posts to cycle through
- **Crisis pause**: Flip this on to stop everything immediately

Currently set to **2 posts per week** — one job spotlight and one educational post.

### What It Can Do Automatically

Educational posts (battery benefits, solar savings, EV charging tips, rebates) and team/crew content don't need your input — the agent writes them from knowledge and picks photos from your Drive folders.

### What It Needs From You

**Job spotlights** need real jobs with real photos. The agent will message you each week:

> "Hey Mick! I've got 1 job spotlight to create this week. Got any recent jobs? Send me a photo and a quick description."

You reply with the details and it handles the rest.

---

## Your Google Drive

All your images live in an organised folder structure:

```
SMA Image Library/
  Solar/
    Fronius/  Sigenergy/  Sungrow/  Aiko Panels/  TW Panels/
  Batteries/
    Fronius/  BYD/  Sigenergy/  Franklin/  Victron/  Power Plus/
  EV Charging/
    Zappi/  Fronius/  Sigenergy/
  Air Conditioning/
    Daikin/  Mitsubishi Heavy Industries/
  Heat Pump Hot Water/
    Thermastore/  EvoHeat/  Rheem/  Reclaim/
  Team/
  General/
  Jobs/
  Used/
  Telegram Uploads/
```

**When you send a photo via Telegram**, it automatically saves to the Telegram Uploads folder.

**When a photo gets used in a published post**, it moves to the Used folder so the same image doesn't get used twice.

You can drop product photos into the brand folders anytime — the agent will use them for product spotlight posts.

For job spotlights, create a subfolder under Jobs (e.g. "Daylesford 10kW") and drop the photos in.

---

## Publishing

All publishing goes through **Buffer** to your three platforms:

- **Instagram** — full caption with hashtags and photo
- **Facebook** — same caption, fewer hashtags
- **Google Business Profile** — shorter, more professional version, no hashtags

Nothing ever publishes without your approval. The agent creates drafts in Buffer — they don't go live until you say so.

---

## Content Quality

Every post gets scored by a quality judge before you see it. If the score is too low, the agent automatically rewrites it. By the time the preview reaches you, it's already been through quality control.

The agent writes in your voice — it learned from your last 170+ Instagram posts. Short sentences, local Macedon Ranges references, mentions the team by name, focuses on quality workmanship. No corporate jargon, no AI-sounding fluff.

---

## Airtable

Your Airtable base tracks everything:

- **Schedule Config** — how many posts per week, what time, content rotation
- **Pending Drafts** — posts waiting for your approval
- **Post History** — everything that's been published
- **Image Library** — all your photos with usage tracking
- **Master Config** — system settings, prompts, API keys

You mainly interact through Telegram. Airtable is there if you want to tweak the schedule or check history.

---

## What You Need to Do

1. **Talk to the bot** — send job details and photos when you've got them
2. **Review previews** — tap the link, check the content, reply to approve or edit
3. **Upload photos** — drop product/job photos into the right Drive folders when you can
4. **Adjust the schedule** — change posts per week or content types in Airtable if you want more or less

That's it. The agent handles the writing, formatting, scheduling, and publishing.
