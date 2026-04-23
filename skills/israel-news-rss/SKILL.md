---
name: israel-news-rss
description: Use when the user wants the latest Israeli news headlines from major outlets via RSS, in English or Hebrew. Aggregates Jerusalem Post, Times of Israel, and JNS (English) or Ynet, Maariv, Walla, Haaretz, and Globes (Hebrew), merges them by publication time, and returns a compact summary suitable for orchestrator context. Trigger phrases include "latest Israeli news", "what's happening in Israel right now", "Israeli headlines", "Hebrew news", "מה חדש בחדשות", "check Ynet / Jpost / ToI", "news from Israel in the last X hours".
---

# Israel News — RSS Aggregator

Fetches and merges RSS feeds from major Israeli news outlets. Returns headlines, publication times, links, and short summaries sorted newest-first. No browser, no API keys, no geo-restriction issues.

## Sources

**English (`--lang en`)**
- `jpost` — Jerusalem Post front page
- `toi` — Times of Israel
- `jns` — Jewish News Syndicate

**Hebrew (`--lang he`)**
- `ynet` — Ynet main feed
- `maariv` — Maariv latest news
- `walla` — Walla main feed
- `haaretz` — Haaretz
- `globes` — Globes business

## Usage

```bash
python3 scripts/fetch_news.py --lang en                      # 50 English items, text output
python3 scripts/fetch_news.py --lang he --limit 100          # 100 Hebrew items
python3 scripts/fetch_news.py --lang en --since 6h           # only last 6 hours
python3 scripts/fetch_news.py --lang he --source ynet        # one source only
python3 scripts/fetch_news.py --lang en --json               # JSON for orchestration
```

### Arguments

- `--lang {en,he}` — language set to fetch. Default `en`.
- `--limit N` — max items returned after merge+sort. Default 50.
- `--source KEY` — restrict to a single source key (see lists above).
- `--since WINDOW` — drop items older than the window. Accepts `30m`, `6h`, `2d`.
- `--json` — emit JSON instead of the text digest.

## When to use

- "Give me the latest Israeli news in English."
- "What are Ynet and Haaretz running right now?"
- "Pull the last 6 hours of headlines from Israel in Hebrew."
- "Summarize today's Jpost front page."

## Output

Text mode prints a numbered list:

```
1. [jpost] Headline...
   2026-04-23T20:26:51+00:00
   https://...
   Short summary snippet...
```

JSON mode returns `{ lang, count, items: [{source, title, link, published, summary}, ...] }` — ready to pipe into an LLM for summarization, clustering, or translation.

## Passing to an orchestrator

The `--json` output is the intended handoff format. Typical pattern:

```bash
python3 scripts/fetch_news.py --lang he --limit 40 --since 12h --json > /tmp/news.json
```

Then hand `/tmp/news.json` to Claude with a prompt like *"summarize the top 5 stories, translate Hebrew headlines, and flag anything security-related."*

## Notes

- Feeds are plain RSS 2.0 / Atom-ish XML; parsed with stdlib (no `feedparser` dependency).
- If one feed is temporarily unreachable it's skipped with a `[warn]` on stderr; the rest still return.
- Publication times are normalized to UTC ISO-8601.
