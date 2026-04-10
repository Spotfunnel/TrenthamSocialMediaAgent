# V2 Edge Case & Thorough Test Plan

## A. Social Post Creation (10 tests)
1. Simple post with clear topic → verify IG/FB/GBP all generated, image from correct folder
2. Vague brief ("do a post") → agent should ask for detail, NOT create empty post
3. Very long brief (200+ words with specs) → verify specs preserved in output
4. Platform filter: "just IG and FB" → no GBP generated
5. Platform filter: "only for Instagram" → only IG, no FB, no GBP
6. Platform filter: "GBP only" → only GBP
7. Two posts back-to-back → different images selected (LRU), different angles
8. Post about a topic with no matching Drive folder (e.g. "post about our new office") → falls back to General
9. Post with emojis/special chars in brief → no crashes, chars preserved
10. Post requesting specific hashtags → hashtags included

## B. Draft Editing (8 tests)
11. "Make it shorter" → caption genuinely shortened
12. "Make it more casual" → tone changes
13. "Add a call to action" → CTA added at end
14. "Remove GBP" → GBP nulled, platforms updated
15. "Remove Instagram" → IG nulled
16. "Change the opening line" → only first line changes, rest preserved
17. Two edits in a row → both applied to same draft
18. Edit when no pending draft exists → agent says "no draft found"

## C. Drive Integration (6 tests)
19. "Use photos from the Solar folder" → lists images from Solar
20. "Grab a photo from Batteries" (lowercase) → fuzzy matches Batteries folder
21. "Use photos from 21 Trentham St" → searches for that folder name (may not exist, should say so)
22. Search for empty folder (EV Charging) → returns 0 images, falls back to General
23. Image non-repetition: create 3 solar posts → all 3 get different images
24. Image from Drive shows in preview page → verify lh3.googleusercontent.com URL renders

## D. Blog Creation (5 tests)
25. "Write a blog about solar battery storage" → blog draft created, has title/body/meta/slug
26. "Blog about EV charging for rural properties" → different topic, different angle
27. Blog preview URL works → renders on Vercel with correct layout
28. Blog with recent blogs existing → different angle from previous
29. Very short blog topic ("blog about solar") → still generates full 600+ word article

## E. Scheduling (5 tests)
30. "Plan this week's posts" → reads config, plans N posts, advances topic index
31. Plan with crisis_pause=true → returns "paused" message, no posts generated
32. Verify topic index advances after planning → check Airtable config field
33. Plan twice in a row → second plan has different topics (rotation continued)
34. Cron trigger simulation → same result as manual "plan this week"

## F. Publishing (4 tests)
35. "Approve" with pending social draft → publishes to Buffer (saveToDraft mode)
36. "Approve" with no pending draft → says "no draft found"
37. Verify post history logged after publish → V2 Post History table has record
38. Draft status changes to "published" after approval

## G. Q&A / Conversational (5 tests)
39. "What posts are pending?" → lists actual drafts
40. "How many posts this week?" → gives count
41. "What can you do?" → explains capabilities
42. Random non-sequitur ("what's the weather?") → polite response, doesn't crash
43. Empty message → handled gracefully

## H. Preview Page Quality (8 tests)
44. Social preview: IG tab shows caption with hashtags, correct formatting
45. Social preview: FB tab shows caption (fewer hashtags)
46. Social preview: GBP tab shows consultative text (no hashtags)
47. Social preview: Image displays correctly from Drive URL
48. Social preview: Platform tabs hidden when content is null (e.g. GBP removed)
49. Social preview: Mobile responsive layout
50. Blog preview: Full blog renders with correct H2 structure
51. Blog preview: Meta description, title, slug displayed

## I. Multi-Client Readiness (3 tests)
52. Config lookup by chat_id → returns correct client
53. Wrong chat_id → returns "client not found" gracefully
54. All tools use client_name from config (not hardcoded)
