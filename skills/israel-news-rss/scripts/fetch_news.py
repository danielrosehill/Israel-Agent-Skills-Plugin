#!/usr/bin/env python3
"""
Israel news RSS aggregator.

Fetches and merges RSS feeds from major Israeli English- and Hebrew-language
news outlets, sorts by publication date (newest first), and emits a compact
summary suitable for passing to an LLM orchestrator.

Usage:
    fetch_news.py --lang en
    fetch_news.py --lang he --limit 100
    fetch_news.py --lang en --source jpost --json
    fetch_news.py --lang he --since 6h
"""
import argparse
import json
import re
import sys
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

FEEDS = {
    "en": {
        "jpost":    "https://www.jpost.com//rss/rssfeedsfrontpage.aspx",
        "toi":      "https://www.timesofisrael.com/feed/",
        "jns":      "https://www.jns.org/index.rss",
    },
    "he": {
        "ynet":     "https://www.ynet.co.il/Integration/StoryRss2.xml",
        "maariv":   "https://www.maariv.co.il/rss/rsschadashot",
        "walla":    "https://rss.walla.co.il/feed/1?type=main",
        "haaretz":  "https://www.haaretz.co.il/srv/rss---feedly",
        "globes":   "https://www.globes.co.il/webservice/rss/rssfeeder.asmx/FeederNode?iID=2",
    },
}

UA = "Mozilla/5.0 (compatible; IsraelNewsRSS/1.0)"
TIMEOUT = 15


@dataclass
class Item:
    source: str
    title: str
    link: str
    published: str  # ISO 8601
    summary: str


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_date(s: str) -> datetime | None:
    if not s:
        return None
    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(s.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def parse_feed(source: str, raw: bytes) -> list[Item]:
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"[warn] {source}: parse error: {e}", file=sys.stderr)
        return []

    items: list[Item] = []
    for el in root.iter("item"):
        title = strip_html((el.findtext("title") or "").strip())
        link = (el.findtext("link") or "").strip()
        desc = strip_html(el.findtext("description") or "")
        pub = el.findtext("pubDate") or el.findtext("{http://purl.org/dc/elements/1.1/}date") or ""
        dt = parse_date(pub)
        iso = dt.astimezone(timezone.utc).isoformat() if dt else ""
        if not title or not link:
            continue
        items.append(Item(source=source, title=title, link=link, published=iso,
                          summary=desc[:400]))
    return items


def parse_since(s: str) -> timedelta | None:
    m = re.fullmatch(r"(\d+)\s*([hdm])", s.strip().lower())
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    return {"h": timedelta(hours=n), "d": timedelta(days=n), "m": timedelta(minutes=n)}[unit]


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch Israeli news RSS feeds.")
    ap.add_argument("--lang", choices=["en", "he"], default="en",
                    help="Language: en (Jpost/ToI/JNS) or he (Ynet/Maariv/Walla/Haaretz/Globes)")
    ap.add_argument("--limit", type=int, default=50, help="Max items to return (default 50)")
    ap.add_argument("--source", help="Only fetch this source key (e.g. jpost, ynet)")
    ap.add_argument("--since", help="Only items newer than this window (e.g. 6h, 2d, 30m)")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = ap.parse_args()

    feeds = FEEDS[args.lang]
    if args.source:
        if args.source not in feeds:
            print(f"Unknown source '{args.source}' for lang={args.lang}. "
                  f"Available: {', '.join(feeds)}", file=sys.stderr)
            return 2
        feeds = {args.source: feeds[args.source]}

    cutoff = None
    if args.since:
        delta = parse_since(args.since)
        if not delta:
            print(f"Invalid --since value '{args.since}'. Use e.g. 6h, 2d, 30m.", file=sys.stderr)
            return 2
        cutoff = datetime.now(timezone.utc) - delta

    all_items: list[Item] = []
    for key, url in feeds.items():
        try:
            raw = fetch(url)
        except Exception as e:
            print(f"[warn] {key}: fetch failed: {e}", file=sys.stderr)
            continue
        all_items.extend(parse_feed(key, raw))

    def sort_key(it: Item):
        return it.published or ""
    all_items.sort(key=sort_key, reverse=True)

    if cutoff:
        filtered = []
        for it in all_items:
            dt = parse_date(it.published)
            if dt and dt >= cutoff:
                filtered.append(it)
        all_items = filtered

    all_items = all_items[: args.limit]

    if args.json:
        print(json.dumps({"lang": args.lang, "count": len(all_items),
                          "items": [asdict(i) for i in all_items]},
                         ensure_ascii=False, indent=2))
    else:
        print(f"# Israel news — lang={args.lang} — {len(all_items)} items\n")
        for i, it in enumerate(all_items, 1):
            print(f"{i}. [{it.source}] {it.title}")
            if it.published:
                print(f"   {it.published}")
            print(f"   {it.link}")
            if it.summary:
                print(f"   {it.summary[:240]}")
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
