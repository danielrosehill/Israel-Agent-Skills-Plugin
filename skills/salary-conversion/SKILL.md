---
name: salary-conversion
description: Use when the user wants to convert a salary between Israeli and world conventions — Israeli salaries are stated **monthly in shekels (NIS / ILS)**, while most other countries state salaries **annually in their local currency** (USD, EUR, GBP, etc.). Handles both directions. Israel → world - multiply the monthly shekel figure by 12 and convert at today's FX rate to the target currency. World → Israel - convert the annual foreign amount to shekels at today's rate, divide by 12, and round the monthly shekel result to the nearest integer (no decimals). Uses today's FX rate — doesn't need to be up-to-the-minute; a rate from the current day is sufficient. Trigger phrases - "convert this salary to USD", "what is X NIS per month in dollars", "how much is Y USD a year in shekels", "israeli salary to world salary", "שכר במונחים בינלאומיים", "convert shekel salary", "monthly shekel to annual dollar", "annual euro salary to monthly shekel".
---

# Salary Conversion (Israel ↔ World)

Converts salaries between the Israeli convention (**monthly in shekels / NIS / ILS**) and the world convention (**annual in local currency**).

## Direction 1 — Israel → world

Input: a monthly salary in shekels (e.g. `25,000 NIS/month`, `₪ 18000`, `twenty thousand shekels a month`).

Procedure:

1. Multiply the monthly shekel figure by **12** to get the annual shekel figure.
2. Fetch today's FX rate — `ILS → {target_currency}`.
3. Multiply to get the annual figure in the target currency.
4. Present the result at a reasonable precision (usually no more than 2 significant decimal places for the foreign side — `$87,234` is better than `$87,234.16`).

Example: `25,000 NIS/month` → `25,000 × 12 = 300,000 NIS/year` → at `1 ILS = 0.27 USD` → `300,000 × 0.27 = $81,000/year`.

## Direction 2 — World → Israel

Input: an annual salary in a foreign currency (e.g. `$120,000/year`, `€85k annual`, `£60,000 per annum`).

Procedure:

1. Fetch today's FX rate — `{source_currency} → ILS`.
2. Convert the annual foreign amount to annual shekels.
3. Divide by **12** to get the monthly shekel figure.
4. **Round to the nearest integer shekel** — no decimals on the shekel side. `₪ 22,471` is correct; `₪ 22,471.33` is not.

Example: `$120,000/year` → at `1 USD = 3.70 ILS` → `120,000 × 3.70 = 444,000 NIS/year` → `444,000 / 12 = 37,000 NIS/month`.

## FX rate sourcing

Use a reputable rate from **today** — it does not need to be real-time. Acceptable sources in rough order of preference:

1. A live FX API the agent can call (e.g. `https://api.frankfurter.app/latest?from=ILS&to=USD`, ECB, Bank of Israel daily reference rate).
2. A web search for "ILS USD today" / "USD ILS today" returning today's rate from a reputable source (Bloomberg, Reuters, Google Finance, XE).

Always cite the source and the rate used (e.g. `Rate used: 1 USD = 3.703 ILS (frankfurter.app, 2026-04-23)`). If the user asks the same conversion again on a different day, re-fetch rather than reusing the previous rate.

## Default assumptions (ask if unsure)

- If the user says just "shekels" or "NIS" without a time period, assume **monthly** (Israeli convention).
- If the user gives a foreign-currency figure without a time period, assume **annual** (world convention).
- If the input is ambiguous (e.g. "60k USD" — monthly or annual?), ask.
- Default target currency for Israel → world is **USD** unless the user specifies otherwise.

## Gross vs net

This skill handles **stated salary figures as given** — it does not compute Israeli tax, bituach leumi, pension, or keren hishtalmut to move between gross and net. If the user needs gross ↔ net, say so explicitly and note that's outside scope — point them to an Israeli salary calculator (e.g. `kolzchut.org.il`) or offer to do a rough estimate with named assumptions.

## Rounding

- Shekel side (both directions): always round to the nearest integer shekel. No decimals.
- Foreign side: up to the agent — 2 decimals is usually overkill; whole units or thousands is typically cleaner for salary figures.

## Out of scope

- Cost-of-living / PPP adjustments ("is ₪25k in Tel Aviv equivalent to $X in NYC lifestyle-wise"). This is purely nominal FX conversion.
- Tax / net computation.
- Historical salary conversions at a specific past date (use today's rate only).
- Signing bonuses, RSUs, equity — just base salary.
