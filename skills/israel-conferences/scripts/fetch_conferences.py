#!/usr/bin/env python3
"""
Israel conferences — whitelist fetcher.

Fetches the curated whitelist of Israeli event aggregators and returns
cleaned text (or raw JSON envelope) per source. This is intentionally a
"dumb fetch" — site-specific HTML structures change too often to maintain
parsers for each. Hand the output to an LLM for event extraction.

Usage:
    fetch_conferences.py
    fetch_conferences.py --source dev
    fetch_conferences.py --json
    fetch_conferences.py --list-sources
"""
import argparse
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser

SOURCES = {
    "events":           "https://events.co.il/",
    "events-feed":      "https://events.co.il/events?locale=he",
    "conferenceindex":  "https://conferenceindex.org/conferences/israel",
    "ivc":              "https://www.ivc-online.com/Events",
    "icx":              "https://www.icx.co.il/%D7%9C%D7%95%D7%97-%D7%94%D7%9B%D7%A0%D7%A1%D7%99%D7%9D-%D7%94%D7%9E%D7%A7%D7%A6%D7%95%D7%A2%D7%99%D7%99%D7%9D",
    "dev":              "https://dev.events/AS/IL/tech",
}

UA = "Mozilla/5.0 (compatible; IsraelConferences/1.0; +https://github.com/danielrosehill)"
TIMEOUT = 20
MAX_TEXT = 60_000  # cap per-source text size handed back to caller


class _Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._chunks = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip:
            return
        s = data.strip()
        if s:
            self._chunks.append(s)

    def text(self):
        out = "\n".join(self._chunks)
        return re.sub(r"\n{3,}", "\n\n", out)


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en,he;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    enc = "utf-8"
    m = re.search(r"charset=([\w-]+)", ctype, re.I)
    if m:
        enc = m.group(1)
    return raw.decode(enc, errors="replace")


def to_text(html):
    p = _Stripper()
    try:
        p.feed(html)
    except Exception:
        pass
    return p.text()[:MAX_TEXT]


def main():
    ap = argparse.ArgumentParser(description="Fetch Israeli conference aggregator whitelist.")
    ap.add_argument("--source", choices=list(SOURCES.keys()), help="Fetch one source only.")
    ap.add_argument("--json", action="store_true", help="Emit JSON envelope.")
    ap.add_argument("--list-sources", action="store_true", help="List source keys and exit.")
    ap.add_argument("--raw", action="store_true", help="Return raw HTML instead of stripped text.")
    args = ap.parse_args()

    if args.list_sources:
        for k, v in SOURCES.items():
            print(f"{k:18s} {v}")
        return 0

    keys = [args.source] if args.source else list(SOURCES.keys())
    results = []
    for k in keys:
        url = SOURCES[k]
        try:
            html = fetch(url)
            body = html if args.raw else to_text(html)
            results.append({"source": k, "url": url, "ok": True, "body": body})
        except Exception as e:
            print(f"[warn] {k}: {e}", file=sys.stderr)
            results.append({"source": k, "url": url, "ok": False, "error": str(e)})

    if args.json:
        json.dump({"count": len(results), "sources": results}, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        for r in results:
            print(f"\n===== [{r['source']}] {r['url']} =====")
            if r["ok"]:
                print(r["body"])
            else:
                print(f"(failed: {r['error']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
