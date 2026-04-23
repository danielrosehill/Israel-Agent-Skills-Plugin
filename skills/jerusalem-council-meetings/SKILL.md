---
name: jerusalem-council-meetings
description: Use when the user wants to browse, list, or download protocols (meeting minutes) from Jerusalem Municipality council committee sittings (ישיבות ועדות מועצת העיר ירושלים). Navigates the official archive at https://www.jerusalem.muni.il/he/city/council/committeesmeetings/, opens a specific committee meeting detail page (CommitteeMeeting?term=<N>&id=<GUID>), pulls the section-by-section agenda outline, and downloads the full protocol PDF linked under פרוטוקול. The site is fronted by Akamai and blocks plain curl/fetch, so this skill drives a real browser (Playwright). Trigger phrases: "Jerusalem city council minutes", "committee meeting protocol", "פרוטוקול ועדה ירושלים", "download Jerusalem municipality sitting", "Jerusalem council meeting agenda", "ישיבת ועדה עיריית ירושלים", "get the protocol PDF for meeting X".
---

# Jerusalem Municipality — Council Committee Meetings

Access archived committee sittings (ישיבות ועדה) of Jerusalem City Council: list meetings, open a specific meeting's agenda, and download the protocol PDF.

## URLs

- **Archive / landing page** — list of committees and their meetings:
  `https://www.jerusalem.muni.il/he/city/council/committeesmeetings/`
- **Single meeting detail page** — query-string driven:
  `https://www.jerusalem.muni.il/he/city/council/CommitteesMeetings/CommitteeMeeting?term=<TERM>&id=<GUID>`
  - `term` — council term number (e.g. `17`).
  - `id` — meeting GUID (e.g. `85cf59bc-f6d0-f011-bbd3-7ced8d49cdf0`).

## Access notes

- **Akamai edge protection**: plain `curl` / `fetch` returns HTTP 403 ("Access Denied" from `errors.edgesuite.net`) even with a browser User-Agent. Use a real browser — Playwright (headless is usually fine; fall back to headed if Akamai challenges).
- **Geo**: not confirmed as strictly IL-geo-restricted — the 403 is bot-detection, not geo. Treat as tier 2 (remote headless browser) preferred, tier 3 (local Playwright) as fallback.
- **Language**: Hebrew (RTL). No login required for public protocols.

## What to extract from a meeting detail page

From `CommitteeMeeting?term=<N>&id=<GUID>`:

| Field (HE) | English | Notes |
|---|---|---|
| שם הוועדה | Committee name | Page heading |
| תאריך הישיבה | Meeting date | Usually near title |
| מספר ישיבה | Meeting number | Within the term |
| סדר יום / נושאים | Agenda / topics | Section-by-section outline — the main body of the page |
| פרוטוקול | Protocol (minutes) | **PDF link** — the full meeting minutes. Primary artefact this skill downloads. |
| החלטות | Decisions | Sometimes a separate linked doc |
| הקלטה / וידאו | Audio / video recording | If present, link to media |

The agenda outline on the page is the cheap summary; the `פרוטוקול` PDF is the authoritative record.

## Procedure

1. **Resolve target meeting.** User supplies either:
   - A full `CommitteeMeeting?term=…&id=…` URL, or
   - A description ("latest finance committee", "planning committee from March 2026") — in which case start at the archive landing page and pick the matching row.
2. **Open the detail page with Playwright.** Default to headless Chromium. If the page renders "Access Denied" or a challenge, retry headed.
3. **Extract the agenda** — grab the section headings and any bullet items under סדר יום / נושאים. Preserve Hebrew verbatim.
4. **Find the protocol link.** Look for an anchor whose visible text contains `פרוטוקול` (or an `href` ending in `.pdf` near that label). Resolve to an absolute URL.
5. **Download the PDF.** Use the same browser context (cookies/session) — `page.request.get(pdf_url)` in Playwright, or click-and-capture-download. Save to the user's requested path, defaulting to:
   `~/jerusalem-council-meetings/<term>-<short-id>-<YYYY-MM-DD>.pdf`
6. **Report back** — committee name, date, meeting number, agenda outline, and the saved PDF path.

## Playwright sketch

```python
from playwright.sync_api import sync_playwright
from pathlib import Path

URL = "https://www.jerusalem.muni.il/he/city/council/CommitteesMeetings/CommitteeMeeting?term=17&id=85cf59bc-f6d0-f011-bbd3-7ced8d49cdf0"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(locale="he-IL")
    page = ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded")

    # Agenda
    agenda = page.locator("main").inner_text()

    # Protocol PDF — anchor with text containing פרוטוקול, or href ending .pdf
    pdf_link = page.locator("a:has-text('פרוטוקול')").first
    pdf_url = pdf_link.get_attribute("href")
    if pdf_url and pdf_url.startswith("/"):
        pdf_url = "https://www.jerusalem.muni.il" + pdf_url

    # Download through the browser context so cookies/Akamai tokens are reused
    resp = ctx.request.get(pdf_url)
    out = Path.home() / "jerusalem-council-meetings" / "17-85cf59bc.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(resp.body())

    browser.close()
```

Selectors above are best-effort from the described structure — verify on first run and adjust if the markup differs (especially the `פרוטוקול` anchor and any cookie/consent banner that may intercept clicks).

## Output format

```
Committee: <HE name>  (<English gloss if obvious>)
Date:      <YYYY-MM-DD>
Term:      <N>    Meeting #: <M>
Agenda:
  1. <section heading>
     - <bullet>
     - <bullet>
  2. ...
Protocol PDF saved to: <absolute path>   (<size>, <n> pages)
```

## Out of scope

- Solving Akamai CAPTCHA / challenges (if one appears, surface it to the user in a headed browser).
- Parsing the PDF contents — this skill only fetches the file. Combine with a separate PDF-reading step for content extraction.
- Non-committee council outputs (full council votes, budget documents) — those live on other sections of the site.
