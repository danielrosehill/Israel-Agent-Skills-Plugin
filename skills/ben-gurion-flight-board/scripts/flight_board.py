#!/usr/bin/env python3
"""
Ben Gurion Airport flight board scraper.

Fetches live arrivals or departures from the official IAA site and applies
optional client-side filters by city, country, airline, or flight number.

Driver: Playwright (headless Chromium).

Usage:
    flight_board.py arrivals
    flight_board.py departures
    flight_board.py arrivals --city "NEW YORK"
    flight_board.py departures --country "GERMANY" --airline "LUFTHANSA"
    flight_board.py arrivals --flight "LY 008"
    flight_board.py arrivals --json

Filters are case-insensitive substring matches. Date-range filtering is
not supported in v1 (the site's date-filter endpoint requires a solved
reCAPTCHA); the board only returns flights for the current operational
window anyway.
"""
import argparse
import asyncio
import json
import sys

URL = "https://www.iaa.gov.il/en/airports/ben-gurion/flight-board/"
TIMEOUT_MS = 60_000


async def fetch(flight_type: str) -> dict:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(locale="en-US")
        page = await ctx.new_page()
        await page.goto(f"{URL}?flightType={flight_type}", wait_until="networkidle", timeout=TIMEOUT_MS)
        await page.wait_for_timeout(1500)

        table_id = "flight_board-arrivel_table" if flight_type == "arrivals" else "flight_board-departures_table"
        data = await page.evaluate(
            """(tableId) => {
                const t = document.getElementById(tableId);
                if (!t) return { headers: [], rows: [] };
                const headers = Array.from(t.querySelectorAll('thead th'))
                    .map(th => th.getAttribute('data-model-attribute') || th.innerText.trim());
                const rows = Array.from(t.querySelectorAll('tbody tr')).map(tr => {
                    // Each td has a div.td-<field> holding the actual value; labels live in sibling
                    // .th-<field> divs that are screen-reader-only. Pull from the value divs directly.
                    const obj = {};
                    tr.querySelectorAll('td').forEach((td, i) => {
                        const valueEl = td.querySelector('[class^="td-"], [class*=" td-"]') || td;
                        const text = valueEl.innerText.replace(/\\s+/g, ' ').trim();
                        obj[headers[i] || `col${i}`] = text;
                    });
                    return obj;
                });
                return { headers, rows };
            }""",
            table_id,
        )
        await browser.close()
        return data


def apply_filters(rows: list, filters: dict) -> list:
    def match(row: dict, key: str, needle: str) -> bool:
        if not needle:
            return True
        return needle.lower() in str(row.get(key, "")).lower()

    out = []
    for r in rows:
        if not match(r, "City", filters.get("city")):
            continue
        if not match(r, "AirlineCompany", filters.get("airline")):
            continue
        if not match(r, "Flight", filters.get("flight_number")):
            continue
        # Country is not a column on the board — approximate via city; skip if filter set and no match on city
        if filters.get("country") and filters["country"].lower() not in str(r.get("City", "")).lower():
            continue
        out.append(r)
    return out


def format_table(rows: list) -> str:
    if not rows:
        return "(no flights match the query)"
    cols = ["Flight", "AirlineCompany", "City", "Terminal", "ScheduledDateTime", "UpdatedDateTime", "StatusColor"]
    widths = {c: max(len(c), max((len(str(r.get(c, ""))) for r in rows), default=0)) for c in cols}
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    body = "\n".join(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols) for r in rows)
    return f"{header}\n{sep}\n{body}"


def main():
    ap = argparse.ArgumentParser(description="Ben Gurion Airport flight board")
    ap.add_argument("flight_type", choices=["arrivals", "departures"])
    ap.add_argument("--city", help="Filter by city (substring, case-insensitive)")
    ap.add_argument("--country", help="Filter by country — approximated against city since the board does not expose country")
    ap.add_argument("--airline", help="Filter by airline company name (substring)")
    ap.add_argument("--flight", dest="flight_number", help="Filter by flight number (substring, e.g. 'LY 008')")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    args = ap.parse_args()

    filters = {
        "city": args.city,
        "country": args.country,
        "airline": args.airline,
        "flight_number": args.flight_number,
    }
    try:
        data = asyncio.run(fetch(args.flight_type))
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    filtered = apply_filters(data["rows"], filters)
    meta = {
        "flight_type": args.flight_type,
        "filters": {k: v for k, v in filters.items() if v},
        "total_on_board": len(data["rows"]),
        "count": len(filtered),
    }

    if args.json:
        print(json.dumps({"meta": meta, "headers": data["headers"], "rows": filtered}, indent=2, ensure_ascii=False))
    else:
        print(f"# Ben Gurion — {args.flight_type} ({meta['count']}/{meta['total_on_board']} flights)")
        if meta["filters"]:
            print(f"# filters: {meta['filters']}")
        print(format_table(filtered))


if __name__ == "__main__":
    main()
