#!/usr/bin/env python3
"""
Israel National Security Council (NSC) travel-threat lookup.

Resolves a country to its NSC threat-level card on gov.il and prints the
fields shown on the public page (threat level, recommendation, area, details).

Driver: Playwright (headless Chromium). The gov.il site is behind Cloudflare
and rejects plain HTTP clients.

The country selector uses internal 3-digit IDs (e.g. Angola = 005). The first
lookup for a country resolves the ID via the page's autocomplete and caches
it in data/country_codes.json so subsequent lookups go straight to the
country-scoped URL.

Usage:
    nsc_threat.py "Angola"
    nsc_threat.py "United States" --json
    nsc_threat.py --list-cached
"""
import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

BASE_URL = "https://www.gov.il/en/departments/dynamiccollectors/travel-warnings-nsc?skip=0"
CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "country_codes.json"
TIMEOUT_MS = 60_000
DEFAULT_PROFILE = Path(
    os.environ.get("NSC_PROFILE_DIR")
    or Path.home() / ".cache" / "israel-agent-skills" / "nsc-chromium-profile"
)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _missing_playwright_msg() -> str:
    return (
        "Playwright is not importable from this Python interpreter "
        f"({sys.executable}).\n"
        "Invoke the plugin's environment-check skill, or run:\n"
        "    pip install --user playwright && python3 -m playwright install chromium"
    )


def load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def cache_key(name: str) -> str:
    return name.strip().lower()


async def resolve_via_autocomplete(page, country: str) -> str | None:
    """Type the country into the autocomplete and capture the resulting URL code."""
    await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
    await page.wait_for_selector("#autocompleteInput", timeout=TIMEOUT_MS)
    await page.fill("#autocompleteInput", "")
    await page.type("#autocompleteInput", country, delay=30)
    await page.wait_for_timeout(500)

    # Click the first visible suggestion that matches (case-insensitive, trimmed).
    needle = country.strip().lower()
    clicked = await page.evaluate(
        """(needle) => {
            const items = Array.from(document.querySelectorAll('#suggestionsList_acTagcountry li[val]'));
            const norm = s => (s || '').trim().toLowerCase();
            let target = items.find(li => norm(li.getAttribute('val')) === needle)
                      || items.find(li => norm(li.getAttribute('val')).startsWith(needle))
                      || items.find(li => norm(li.getAttribute('val')).includes(needle));
            if (!target) return null;
            target.click();
            return target.getAttribute('val').trim();
        }""",
        needle,
    )
    if not clicked:
        return None
    # Wait for URL to update with country=
    try:
        await page.wait_for_function("() => /[?&]country=\\d+/.test(location.search)", timeout=10_000)
    except Exception:
        return None
    m = re.search(r"[?&]country=(\d+)", page.url)
    return m.group(1) if m else None


async def scrape_card(page) -> dict | None:
    """Extract the threat card fields from the currently loaded result page."""
    await page.wait_for_selector("img.lead-img", state="attached", timeout=45_000)
    return await page.evaluate(
        """() => {
            const fields = document.querySelector('.row.row-gov.ordered-fields');
            if (!fields) return null;
            // Walk up to the card root that also contains the lead image.
            let card = fields;
            for (let i = 0; i < 6 && card && !card.querySelector('img.lead-img'); i++) {
                card = card.parentElement;
            }
            if (!card) card = fields;
            const img = card.querySelector('img.lead-img');
            const out = { threat_image_alt: img?.getAttribute('alt') || null,
                          threat_image_url: img?.getAttribute('src') || null };
            fields.querySelectorAll(':scope > div').forEach(div => {
                const label = div.querySelector('label')?.innerText.trim();
                if (!label) return;
                const valueEl = div.querySelector('span.mr-1, a.mr-1');
                out[label] = valueEl ? valueEl.innerText.trim() : null;
            });
            return out;
        }"""
    )


async def lookup(country: str, headed: bool = False, cdp_url: str | None = None,
                 profile_dir: Path | None = None) -> dict:
    try:
        from playwright.async_api import async_playwright
    except ModuleNotFoundError as e:
        raise SystemExit(_missing_playwright_msg()) from e

    cache = load_cache()
    code = cache.get(cache_key(country))

    async with async_playwright() as p:
        browser = None
        ctx = None
        if cdp_url:
            # Attach to a user-launched Chrome (start with: chromium --remote-debugging-port=9222)
            browser = await p.chromium.connect_over_cdp(cdp_url)
            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        else:
            # Persistent context = real browser profile, CF clearance survives between runs
            profile = profile_dir or DEFAULT_PROFILE
            profile.mkdir(parents=True, exist_ok=True)
            ctx = await p.chromium.launch_persistent_context(
                str(profile),
                headless=not headed,
                locale="en-US",
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"],
            )
        page = await ctx.new_page()
        try:
            if code:
                await page.goto(f"{BASE_URL}&country={code}", wait_until="domcontentloaded", timeout=TIMEOUT_MS)
            else:
                resolved = await resolve_via_autocomplete(page, country)
                if not resolved:
                    raise RuntimeError(f"Could not resolve country '{country}' via autocomplete")
                code = resolved
                cache[cache_key(country)] = code
                save_cache(cache)
                # After autocomplete click the page reloads with the country filter applied.
                await page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)

            data = await scrape_card(page)
            if not data:
                raise RuntimeError("No threat card found on page (country may have no advisory listed)")
            return {
                "query": country,
                "country_code": code,
                "url": page.url,
                "data": data,
            }
        finally:
            if cdp_url and browser:
                await browser.close()
            elif ctx:
                await ctx.close()


def format_human(result: dict) -> str:
    d = result["data"]
    lines = [
        f"# NSC Travel Threat — {result['query']}",
        f"URL: {result['url']}",
        "",
        f"Threat image:  {d.get('threat_image_alt') or '-'}",
    ]
    for key in ("Country", "Threat Level", "Recommendation", "Area Under Threat", "Details",
                "Recommendations of the Ministries of Foreign Affairs and Health"):
        if key in d:
            lines.append(f"{key}: {d[key] or '-'}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Israel NSC travel threat-level lookup")
    ap.add_argument("country", nargs="?", help="Country name as it appears on gov.il (e.g. 'Angola')")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of formatted text")
    ap.add_argument("--list-cached", action="store_true", help="Print the cached country->code map and exit")
    ap.add_argument(
        "--headed",
        action="store_true",
        default=os.environ.get("NSC_HEADED") == "1",
        help="Open a visible browser window. Also enabled by NSC_HEADED=1.",
    )
    ap.add_argument(
        "--cdp",
        default=os.environ.get("NSC_CDP_URL"),
        help="Attach to a user-launched Chrome over CDP, e.g. http://localhost:9222. "
             "Start Chrome first: chromium --remote-debugging-port=9222. "
             "Also reads NSC_CDP_URL.",
    )
    ap.add_argument(
        "--profile",
        default=None,
        help=f"Persistent browser profile directory (default: {DEFAULT_PROFILE}, "
             "or set NSC_PROFILE_DIR).",
    )
    args = ap.parse_args()

    if args.list_cached:
        print(json.dumps(load_cache(), indent=2, ensure_ascii=False, sort_keys=True))
        return

    if not args.country:
        ap.error("country is required (or pass --list-cached)")

    try:
        result = asyncio.run(lookup(
            args.country,
            headed=args.headed,
            cdp_url=args.cdp,
            profile_dir=Path(args.profile) if args.profile else None,
        ))
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
