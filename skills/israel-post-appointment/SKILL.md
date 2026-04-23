---
name: israel-post-appointment
description: Use when the user wants to book an appointment at an Israel Post branch (דואר ישראל, doar) — e.g. for passport collection, oversized package pickup, bank services, or anything requiring a scheduled slot at a specific sniff-haDoar. Locates the right branch, identifies its Qnomy queuing-system id (qnomycode) — Israel Post uses Qnomy (central.qnomy.com) as the appointment backend — and drives the booking flow via a visible Playwright browser for the user-facing steps that need captcha / SMS OTP. Includes a bundled fallback `data/branches.json` with all 1,524 branches (id, branchnumber, name, qnomycode, address, city, lat/lon, type) captured directly from the CDN endpoint the site uses, so branch lookup works even if the live API is temporarily broken. Trigger phrases: "book a post office appointment", "schedule an appointment at doar", "kavia tor b-doar", "book a slot to pick up my passport at the post office", "find the Qnomy code for post office X", "which post office branches accept appointments", "post office in [city] with appointments".
---

# Israel Post Appointment Booking

Helps the user find an Israel Post branch that supports appointment booking and drives the booking flow. Uses the same Qnomy backend (`central.qnomy.com`) that Israel Post's web app talks to.

## Data model — what identifies a branch

Israel Post uses three overlapping identifiers; don't confuse them:

| Field | Source | Used for | Example |
|---|---|---|---|
| `id` | Internal DB | Cross-referencing inside the Israel Post site | `8` |
| `branchnumber` | Public-facing branch number | Shown in the UI, printed on signage | `3` |
| `qnomycode` | Qnomy queuing system id | **This is the one appointments are booked against.** `0` / null means the branch does NOT offer appointments | `86` |

**Only branches with a non-zero `qnomycode` accept appointments.** Of the 1,524 branches in the dataset, roughly 324 have a `qnomycode`. The rest are post-delivery-only (מסירת דואר בלבד), mobile post (דואר נע), community secretariats (מזכירות יישוב), etc.

## Primary data source (API-first)

The official site loads its full branch list from this static CDN endpoint, unauthenticated:

```
https://mypostvouchars-prd.azureedge.net/branches/branches.json
```

Response is `{ ReturnCode, ErrorMessage, Result: [ ... 1524 branches ... ] }`. Each branch has the fields listed above plus hours, accessibility, services, and geocoordinates.

**Always try this endpoint first.** Plain `curl` works — no browser, no captcha, no session. If it succeeds, skip the rest of the lookup ladder.

Per-branch detail (services, hold-times, free slots) is fetched from:

```
https://central.qnomy.com/CentralAPI/...
```

The exact path is discovered via the network-capture flow in `Local-Web-Capture:scrape-web-page` — do that once and record under `sites.yaml` → `central.qnomy.com`.

## Fallback data source — bundled `data/branches.json`

If the CDN endpoint is unreachable (outage, network issue, IP geoblock from outside Israel), fall back to the bundled snapshot at `data/branches.json` inside this skill's directory. Shape:

```json
{
  "source": "https://mypostvouchars-prd.azureedge.net/branches/branches.json",
  "captured_at": "2026-04-23",
  "count": 1524,
  "branches": [
    {
      "id": 8,
      "branchnumber": 3,
      "name": "מרכזי ירושלים",
      "qnomycode": 86,
      "branchtype": "סניף",
      "city": "ירושלים",
      "street": "...",
      "house": 23,
      "zip": "...",
      "telephone": null,
      "lat": 31.78,
      "lon": 35.22
    }
  ]
}
```

The snapshot is captured-at stamped — warn the user it may be stale if the live endpoint failed and the snapshot is older than ~3 months. Offer to re-capture (see "Refreshing the snapshot" below).

## Entry points for the user

Two canonical flows:

1. **"Book an appointment at post office X"** — user names the branch. Look it up by name (fuzzy Hebrew match) in the dataset. Confirm the match (show name + full address). Confirm the branch has a `qnomycode`. Proceed to booking.
2. **"Book an appointment at a post office near me in Y"** — user names a city or area. Filter the dataset by `city` or by distance from a lat/lon if they give an address. Show only branches with `qnomycode`. User picks one. Proceed to booking.

Don't ask the user for the branch id or qnomycode — resolve it from the name.

## Booking flow (UI-driven)

The booking UI is at (as of 2026-04-23 — verify before use):

```
https://doar.israelpost.co.il/locatebranch
```

…with a per-branch deep-link into the Qnomy appointment picker. Discover the deep-link pattern via `scrape-web-page` in `network` mode once and record it.

The booking flow requires:

- **Service selection** — the user must pick the specific service (passport, oversized package, etc.). The list is per-branch and per-qnomycode. Fetched from Qnomy.
- **Date/time slot** — Qnomy returns available slots; user picks.
- **Personal details** — name, Israeli ID number (`teudat zehut`), phone number.
- **SMS OTP** — Israel Post sends an SMS code to confirm. The skill must pause and let the user paste the code.
- **Possibly a reCAPTCHA.** Use a **visible** Playwright browser — do not try to solve.

Never submit a booking without showing the user the full summary (branch, service, date/time, personal details) and getting an explicit "confirm".

## Refreshing the snapshot

To refresh `data/branches.json`:

```bash
curl -s "https://mypostvouchars-prd.azureedge.net/branches/branches.json" -o /tmp/branches_raw.json
python3 - <<'PY'
import json, pathlib
src = json.load(open("/tmp/branches_raw.json"))
out = [{
    "id": b["id"], "branchnumber": b["branchnumber"], "name": b["branchname"],
    "qnomycode": b.get("qnomycode") or None, "branchtype": b.get("branchtypename"),
    "city": b.get("city"), "street": b.get("street"), "house": b.get("house"),
    "zip": b.get("zip"), "telephone": b.get("telephone"),
    "lat": b.get("geocode_latitude"), "lon": b.get("geocode_longitude"),
} for b in src["Result"]]
from datetime import date
pathlib.Path("skills/israel-post-appointment/data/branches.json").write_text(
    json.dumps({
        "source": "https://mypostvouchars-prd.azureedge.net/branches/branches.json",
        "captured_at": str(date.today()), "count": len(out), "branches": out,
    }, ensure_ascii=False, indent=2)
)
PY
```

Commit the refresh with a message like `Refresh Israel Post branches snapshot (YYYY-MM-DD, N branches)`.

## Notes / gotchas

- Israeli IP not strictly required for the CDN endpoint (it's behind Azure CDN, global), but the `doar.israelpost.co.il` site drops a bot-detection challenge to headless browsers. Run Playwright non-headless with `--disable-blink-features=AutomationControlled` and a real UA, per the stealth pattern in `Local-Web-Capture:scrape-web-page`.
- Hebrew-only fields. Preserve RTL strings verbatim.
- The `branchtype` `סניף` means a full-service branch (most likely to accept appointments). `סוכנות א/ב/ג` are smaller agencies — some take appointments, most don't. Filter by `qnomycode` presence, not by type.
- Do not assume a branch's qnomycode is stable forever — it can change. If booking fails with "branch not found in Qnomy", refresh the snapshot.

## Out of scope

- Does not book multi-person appointments.
- Does not cancel or reschedule existing appointments (separate flow — can be added later).
- Does not handle non-appointment services like parcel tracking.
