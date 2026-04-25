---
name: israel-conferences
description: Use when the user wants to find upcoming conferences, professional events, summits, expos, or industry meetups happening in Israel — by topic (tech, AI, biomed, finance, marketing, HR, cyber, startup), by city (Tel Aviv, Jerusalem, Haifa), by date window, or in general ("what conferences are coming up in Israel", "any AI events in Tel Aviv next month", "כנסים בישראל", "אירועים מקצועיים", "tech conferences Israel"). Checks a curated whitelist of Israeli event aggregators FIRST (events.co.il, conferenceindex.org, IVC, ICX, dev.events) before falling back to general web search.
---

# Israel Conferences — Upcoming Events Lookup

Find upcoming conferences and professional events in Israel. The skill enforces a **priority order**: hit the curated whitelist of Israel-focused event aggregators before doing any open web search, so results are anchored in known-good sources rather than ad-spam.

## Priority whitelist (check first, in order)

| # | URL | Coverage | Language | Notes |
|---|-----|----------|----------|-------|
| 1 | https://events.co.il/ | General — business, marketing, HR, tech, professional | Hebrew | Largest Israeli professional event listing site |
| 2 | https://events.co.il/events?locale=he | Same as #1 — direct events feed | Hebrew | Use this URL if the homepage is too marketing-heavy |
| 3 | https://conferenceindex.org/conferences/israel | Academic / scientific conferences in Israel | English | Global academic index, Israel filter |
| 4 | https://www.ivc-online.com/Events | VC, startup, investment, hi-tech | English | IVC Research Center events feed |
| 5 | https://www.icx.co.il/לוח-הכנסים-המקצועיים | Professional conferences (medical, legal, accounting, engineering) | Hebrew | "לוח הכנסים המקצועיים" — Israel's professional conference board |
| 6 | https://dev.events/AS/IL/tech | Developer / tech conferences | English | Clean structured listing, easiest to parse |

Only after these have been consulted should an open web search be used (and only to fill in gaps — e.g. a niche topic the aggregators miss).

## How to use

### 1. Quick lookup — agent-driven (preferred)

For most user queries, the right pattern is:

1. Call `WebFetch` on each whitelist URL **in order**, asking the model to extract events matching the user's filters (topic, city, date window). Stop early if you have enough relevant results.
2. Merge results, dedupe by event name + date, sort by start date ascending.
3. If the user asked for a topic poorly covered by the whitelist (e.g. very niche), supplement with `WebSearch` for `"upcoming [topic] conference Israel 2026"`.
4. Return a tight list: name, date(s), city/venue, organiser, link.

### 2. Bulk fetch — helper script

```bash
python3 scripts/fetch_conferences.py                 # fetch all whitelist URLs, print raw text
python3 scripts/fetch_conferences.py --source dev    # only dev.events
python3 scripts/fetch_conferences.py --list-sources  # show source keys
python3 scripts/fetch_conferences.py --json          # JSON envelope per source
```

The script is a thin fetch+strip helper — it does **not** try to parse every aggregator's bespoke HTML. It returns cleaned text/HTML per source, ready to hand to the LLM for extraction. This avoids brittle scrapers breaking when sites redesign.

### Source keys

- `events` → events.co.il homepage
- `events-feed` → events.co.il direct events feed
- `conferenceindex` → conferenceindex.org Israel page
- `ivc` → ivc-online.com events
- `icx` → icx.co.il professional conferences board
- `dev` → dev.events Israel/tech

## Filters to surface to the user

When the user's request is broad ("conferences in Israel"), ask or assume:

- **Topic** — tech / AI / biomed / fintech / marketing / HR / legal / medical / academic / startup
- **City** — Tel Aviv, Jerusalem, Haifa, Herzliya, online
- **Date window** — next 30 / 60 / 90 days; specific month
- **Language** — sessions in English vs. Hebrew (matters for foreign attendees)

## When to use

- "What conferences are coming up in Israel?"
- "Any AI events in Tel Aviv next month?"
- "Find me biomed conferences in Israel in Q3."
- "כנסי הייטק בישראל"
- "Tech meetups Israel May 2026"
- "Are there any marketing summits in Tel Aviv soon?"

## Notes

- `events.co.il` and `icx.co.il` are Hebrew-first — translate event titles to English in the final summary unless the user asked in Hebrew.
- `conferenceindex.org` is global; many of its "Israel" listings are call-for-papers far in advance — flag dates clearly.
- `ivc-online.com` skews to paid VC events — useful for startup/investor scene, less so for general professional development.
- Some sites (icx.co.il in particular) gate full event detail behind a click-through; the listing page still gives name + date + city, which is usually enough.
- Do **not** persist or cache results — event listings change daily.
