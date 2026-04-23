---
name: ben-gurion-flight-board
description: Use when the user wants to check live arrivals or departures at Ben Gurion Airport (Tel Aviv, TLV, LLBG) from the official Israel Airports Authority flight board. Supports filtering by city, airline, or flight number. Trigger phrases include "is flight X on time", "Ben Gurion arrivals", "TLV departures", "flights from [city] to Tel Aviv", "did the [destination] flight leave", "arrivals today at Ben Gurion", "when does [airline] flight land".
---

# Ben Gurion Airport — Flight Board

Fetches the official IAA arrivals or departures board for Ben Gurion (TLV / LLBG) and optionally filters client-side by city, airline, or flight number.

## When to use

- "Is LY 008 from New York on time?"
- "What arrivals are coming in from Athens right now?"
- "Show me all El Al departures today."
- "Did the Bangkok flight leave?"

## Usage

```bash
python3 scripts/flight_board.py arrivals
python3 scripts/flight_board.py departures
python3 scripts/flight_board.py arrivals --airline "EL AL"
python3 scripts/flight_board.py departures --city "ATHENS"
python3 scripts/flight_board.py arrivals --flight "LY 008"
python3 scripts/flight_board.py arrivals --json
```

Filters are case-insensitive substring matches. The board only returns flights in the current operational window (a few hours either side of `now`); it is not a historical query.

## Returned fields

| Field | Notes |
|---|---|
| `Flight` | e.g. `LY 008` |
| `AirlineCompany` | e.g. `EL AL ISRAEL AIRLINES` |
| `City` | origin for arrivals, destination for departures |
| `Terminal` | `1` or `3` |
| `ScheduledDateTime` | `HH:MM DD/MM` |
| `UpdatedDateTime` | live estimate, `HH:MM` |
| `StatusColor` | e.g. `FINAL`, `LANDED`, `DELAYED`, `NOT FINAL`, or empty |

## Limitations

- No country filter (the board does not expose country).
- No date-range filter — only flights in the current operational window.
- English locale only.

## Requires

- Python 3.10+
- `playwright` with Chromium installed (`pip install playwright && playwright install chromium`)
