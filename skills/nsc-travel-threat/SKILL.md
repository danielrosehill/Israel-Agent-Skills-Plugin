---
name: nsc-travel-threat
description: Use when the user wants the current Israel National Security Council (NSC) travel threat level / advisory for a specific country. Pulls the official rating, recommendation, area under threat, and background details from gov.il. Trigger phrases include "NSC threat level for X", "is it safe for Israelis to travel to X", "travel warning for X", "Israeli travel advisory for X", "what's the threat rating for X", "NSC recommendation on X".
---

# Israel NSC — Travel Threat Lookup

Resolves a country to its Israel National Security Council travel-threat card on gov.il and returns the published threat level, recommendation, area under threat, and background.

Source: <https://www.gov.il/en/departments/dynamiccollectors/travel-warnings-nsc>

## When to use

- "What's the NSC threat level for Angola?"
- "Is there an Israeli travel warning for Thailand?"
- "Show me the Counter-Terrorism Bureau advisory for Mexico."
- "Current threat rating for Türkiye / Turkey?"

## Usage

```bash
python3 scripts/nsc_threat.py "Angola"
python3 scripts/nsc_threat.py "United Kingdom" --json
python3 scripts/nsc_threat.py --list-cached
```

The first lookup for a country uses the page's autocomplete to resolve its internal 3-digit ID and caches it in `data/country_codes.json`. Subsequent lookups go straight to the country-scoped URL (`?country=NNN`).

If the user gives a name that doesn't match the gov.il list verbatim (e.g. "USA", "UK"), retry with the official label as it appears in the dropdown ("The United States of America (USA)", "United Kingdom").

## Returned fields

| Field | Notes |
|---|---|
| `threat_image_alt` | The icon label, e.g. `Potential Threat`, `High Threat` — corresponds to the rating tier |
| `Country` | Country name as displayed |
| `Threat Level` | Numeric tier (e.g. `02`) |
| `Recommendation` | Short recommendation, e.g. "Increased precautionary measures" |
| `Area Under Threat` | Sub-region if the warning is geographically scoped, otherwise empty |
| `Details` | Background paragraph from the NSC |
| `Recommendations of the Ministries of Foreign Affairs and Health` | Cross-reference link to the parallel MFA/Health advisory |

## Browser modes

The script uses a **persistent browser profile** by default (stored under `~/.cache/israel-agent-skills/nsc-chromium-profile/`, override with `NSC_PROFILE_DIR`). State carries between runs, so a one-time interactive setup is enough.

If a lookup fails to render the card:

1. Run once headed so any first-visit checks can be cleared interactively:
   ```bash
   python3 scripts/nsc_threat.py "Angola" --headed
   ```
2. Subsequent runs (same profile) can usually go headless.
3. As an alternative, attach the script to a Chrome you already have open:
   ```bash
   chromium --remote-debugging-port=9222 &
   python3 scripts/nsc_threat.py "Angola" --cdp http://localhost:9222
   ```

After the first successful lookup the country code is cached, so subsequent same-country lookups are fast.

## Limitations

- English locale only.
- Some entries (e.g. regions like "Sinai", "Chechnya (Russia)") are listed as their own "country" in the dropdown — pass the exact label.

## Requires

- Python 3.10+
- `playwright` with Chromium installed.

If `python3 -c "import playwright"` fails, defer to the **`environment-check`** skill in this plugin rather than installing manually.
