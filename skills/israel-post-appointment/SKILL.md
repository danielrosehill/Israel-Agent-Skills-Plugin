---
name: israel-post-appointment
description: Use when the user wants to check the next available appointment, book an appointment, or cancel an appointment at an Israel Post branch (דואר ישראל, doar) — e.g. for package pickup (מסירת דואר ללקוח), general counter service (אשנב כל), foreign currency (מטבע חוץ), or vehicle ownership transfer (העברת בעלות רכב). Resolves the target branch by name / city / address against a bundled dataset of 314 booking-capable branches (each with its `branchnumber`), constructs the direct booking URL, and drives the headless Playwright flow. The booking flow requires only a mobile phone number entered twice — no ID (teudat zehut), no SMS OTP, no captcha, no login. Trigger phrases - "book a post office appointment", "kavia tor b-doar", "schedule appointment at doar", "check next post office slot", "is there a post office appointment today", "post office near me with appointments", "cancel my post office appointment", "find the branch number for [post office name]".
---

# Israel Post Appointment

Three sub-flows:

- **check-next** — report earliest available slot for (branch, service). Read-only.
- **book** — book at earliest slot or a user-specified slot; returns confirmation details.
- **cancel** — cancel a just-booked appointment (from the same session).

## Surprising facts (confirmed by capture)

- **No ID / teudat zehut required.** Only a mobile phone number.
- **No SMS OTP.** Phone is trust-on-first-use; identification happens physically at the branch's queue terminal by typing the phone.
- **No captcha, no login.** Fully anonymous flow.
- **Headless Chromium works** end-to-end despite Reblaze-style anti-bot on the page; no stealth plugin required.

## Branch lookup (`data/branches.json`)

Bundled dataset of **314 booking-capable branches** (Israel Post has ~1,524 branches total; only those with counter-appointment support are shipped here).

Each branch has: `branchnumber`, `branchname`, `branchtypename`, `city`, `street`, `house`, `zip`, `area`, `region`, `telephone`, `geocode_latitude`, `geocode_longitude`, `ExtraServices`.

Lookup pattern:
1. Filter `branches` by `city` + fuzzy match on `branchname` / `street`.
2. Confirm the match with the user (show full name + address).
3. Use the matched branch's `branchnumber` to construct the booking URL.

Do NOT ask the user for the branch number — resolve it from the name or address.

## Booking URL

The URL-encoded template is bundled in `data/branches.json` under `booking_url_template`. Substitute `{branchnumber}` with the target branch's `branchnumber` field. Example:

```
https://israelpost.co.il/{encoded-hebrew-path}?no=101
```

## Service selection

Four service types are exposed as buttons on the picker page:

| Service key | Hebrew label | Notes |
|---|---|---|
| `general` | אשנב כל | General counter, up to 10 slips per appointment |
| `forex` | מטבע חוץ | Foreign currency |
| `package_pickup` | מסירת דואר ללקוח | Package / mail pickup — the most common |
| `vehicle_transfer` | העברת בעלות רכב | Vehicle ownership transfer |

Not every branch offers every service — the buttons render per branch.

## Flow (driven in headless Playwright)

1. `goto` the booking URL with `?no={branchnumber}`.
2. Dismiss cookie overlay if present — `role=button[name="סגירה"]` (visible text `הבנתי`).
3. Click the service button by Hebrew label (class `.LeadAppt-services-item`).
4. Date/time picker renders:
   - Day tabs — only days with availability appear (e.g. "ראשון 26").
   - Daypart tabs — `#LeadAppt-datepick-time-dayparts button[data-for="noon"]` and `button[data-for="afterNoon"]`. The `.active` one is currently shown; the default is the afternoon tab if it has slots.
   - Slot buttons — 3-minute intervals, labeled `HH:MM`, inside the active daypart only.
5. Select day tab → daypart tab → slot button.
6. Click continue — `#LeadAppt-datepick-btn-next` (fires `LeadApptSubmit()`).
7. Phone form:
   - Primary input: `#leadmobile`
   - Confirm: `role=textbox[name="*הקלדה חוזרת של מספר טלפון סלולארי"]`
   - Both required; must match.
8. Click continue.
9. Confirmation page — look for heading text `פגישתך נקבעה בהצלחה` ("your appointment has been successfully booked"). Read back:
   - Branch name + address
   - Service
   - Day, date (DD-MM-YYYY), time (HH:MM)
   - Masked phone (e.g. `0501****76`)

### Cancel sub-flow

From the confirmation page:
1. Click `role=button[name="בטל תור"]` on the confirmation card.
2. An overlay appears: heading `האם ברצונך לבטל את התור?`, buttons `בטל תור` (confirm) / `לא` (abort).
3. Click the overlay's `בטל תור`.
4. Success overlay with text `פגישתך בוטלה בהצלחה`. A `חזור` button closes it.

Cross-session cancel by phone lookup is **not** currently supported by this skill — the cancel button only appears on the in-session confirmation page.

## Local preferences (`~/.config/israel-agent-skills/preferences.yaml`)

User values are read from a local, gitignored config — never hardcode in the skill.

```yaml
israel_post:
  default_branch_no: 101          # e.g. 101 = מרכזי ירושלים, יפו 23
  default_service: package_pickup # one of: general | forex | package_pickup | vehicle_transfer
  default_phone: "05XXXXXXXX"     # treated as a secret
```

If the config is missing or `default_phone` is absent, the `book` flow must fail with a clear "run the onboard step first" message rather than prompting or defaulting.

## Implementation notes

- Chromium headless=true with a realistic user-agent and default viewport is sufficient — no stealth plugin needed.
- For `check-next`: stop after the daypart/slot tabs render. Extract the first day-tab label + first enabled slot button under the first non-empty daypart. Do **not** click anything further — avoids any risk of triggering a booking.
- For `book`: perform the full flow. Require an explicit user confirmation of the summary (branch, service, day/date/time, phone tail digits) before clicking the final continue button. Verify `פגישתך נקבעה בהצלחה` before reporting success.
- For `cancel`: run from the confirmation page only. Verify `פגישתך בוטלה בהצלחה` before reporting success.
- If the Reblaze challenge ever escalates and headless stops working, fall back to a visible Playwright window; do not try to solve the challenge programmatically.

## Refreshing `data/branches.json`

The bundled dataset can go stale (branches added, renumbered, or decommissioned). Refresh is a maintainer task; the upstream source and refresh script are maintained in the skill's development repo, not in this public plugin. If a branch lookup fails or the dataset is older than ~6 months, flag it to the user rather than silently returning stale data.
