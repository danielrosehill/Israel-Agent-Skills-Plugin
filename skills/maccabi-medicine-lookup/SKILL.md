---
name: maccabi-medicine-lookup
description: Use when the user wants to check whether a medicine is available through Maccabi Healthcare Services (מכבי שירותי בריאות) — whether it is listed, whether it is prescription-only (POM, מרשם), whether it is included in the health basket / sal briut (סל הבריאות, subsidised), its out-of-pocket price to the patient, and a link to the patient information leaflet (עלון לצרכן) if one is published. Drives the Maccabi medicines guide at https://www.maccabi4u.co.il/healthguide/medicines/ via a visible Playwright browser, searches by medicine name using the autocomplete search box, and extracts the key fields from the medicine detail page. Trigger phrases: "is this med on maccabi", "check maccabi for [drug]", "is X in the sal briut", "how much does X cost on maccabi", "maccabi medicine lookup", "find [drug] on maccabi".
---

# Maccabi Medicine Lookup

Looks up a medicine on the Maccabi Healthcare Services public medicines guide and reports back the facts the user actually cares about:

1. Whether Maccabi lists it at all.
2. Whether it is prescription-only (POM / מרשם).
3. Whether it is in the health basket (בסל הבריאות) — i.e. subsidised.
4. The out-of-pocket **price to the patient** (not the formulary / reference price computations).
5. A link to the patient information leaflet (עלון לצרכן) if shown.

## Entry point

Open the medicines guide landing page:

`https://www.maccabi4u.co.il/healthguide/medicines/`

Individual medicine pages follow the pattern:

`https://www.maccabi4u.co.il/healthguide/medicines/%D7%AA%D7%A8%D7%95%D7%A4%D7%95%D7%AA/<id>/`

(`%D7%AA%D7%A8%D7%95%D7%A4%D7%95%D7%AA` = `תרופות` / "medicines"). The trailing numeric id is Maccabi's internal med id — there's no predictable mapping from drug name to id, so always reach the page via search.

## How to search

The site uses a physical search box with autocomplete — pasting a URL-encoded query into the address bar does **not** work. The skill must:

1. Navigate to the medicines landing page in a visible Playwright browser.
2. Locate the medicine search input on the page.
3. Type the medicine name **character-by-character** (not `fill`) so the autocomplete dropdown populates. Hebrew and English names both work; prefer whatever the user supplied.
4. Wait for the autocomplete suggestions to appear.
5. Click the matching suggestion — do **not** just press Enter, because the site relies on the suggestion click to navigate to the medicine detail page.

If there is no autocomplete match, report that back — Maccabi does not list it under that name. Offer the user the chance to try an alternative spelling (Hebrew vs. transliteration, brand vs. generic).

## What to extract from the detail page

Example detail pages used as references:

- `https://www.maccabi4u.co.il/healthguide/medicines/%D7%AA%D7%A8%D7%95%D7%A4%D7%95%D7%AA/92793/`
- `https://www.maccabi4u.co.il/healthguide/medicines/%D7%AA%D7%A8%D7%95%D7%A4%D7%95%D7%AA/35659/`
- `https://www.maccabi4u.co.il/healthguide/medicines/%D7%AA%D7%A8%D7%95%D7%A4%D7%95%D7%AA/80895/`

### 1. תנאים ואישורים — Conditions & approvals

Section heading on the page: **תנאים ואישורים**. Under it, the site indicates:

- Whether the drug is **prescription-only (מרשם / POM)**.
- Whether the drug is **in the health basket (בסל הבריאות / subsidised)**, sometimes with indication restrictions (e.g. only for a specific condition).

Capture the text verbatim in Hebrew, and provide a short English gloss in the report.

### 2. Price

At the bottom of the page there is a price block when a price is published. The **only** figure the user cares about is **the price the patient actually pays** (usually labelled מחיר לצרכן / מחיר לחולה / "price to consumer"). Ignore the reference-price / formulary computations, ceiling prices, pharmacist margins, etc.

If no price is shown, say so explicitly — don't invent one.

### 3. Patient information leaflet (עלון לצרכן)

Detail pages often include a link to the patient information leaflet — typically labelled **עלון לצרכן** or **עלון למטופל**, often pointing at a PDF on the Israeli Ministry of Health site. If present, return the absolute URL. If absent, say so.

## Output format

Report back in a short structured block. Example:

```
Medicine: <name as shown on Maccabi>
Maccabi page: <detail URL>
Prescription-only (מרשם): yes / no
In health basket (בסל הבריאות): yes / no  [+ any indication restriction text]
Price to patient: ₪<amount>  (or "not published")
Patient leaflet (עלון לצרכן): <URL or "not listed">
Raw "תנאים ואישורים" text: <verbatim Hebrew>
```

## Playwright notes

- Use a **visible** browser — the site occasionally throws cookie / consent banners that are easier to clear with the user watching. Dismiss any cookie banner before interacting with the search box.
- The page is RTL Hebrew; selectors by role/name work better than positional selectors.
- Wait on network idle after clicking an autocomplete suggestion before scraping — the detail page hydrates client-side.
- Do not trigger `alert` / `confirm` dialogs. If a dialog-like modal appears, close it via its own close button, not by pressing Enter.

## Out of scope

- Does **not** attempt to determine co-pay tiers by Maccabi membership class (Magen Zahav etc.) — only the base price shown on the public page.
- Does **not** cross-check Clalit / Meuhedet / Leumit. This skill is Maccabi-only.
- Does **not** give medical advice. If the user asks about dosage or interactions, point them at the leaflet link and their pharmacist.
