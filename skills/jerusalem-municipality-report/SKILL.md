---
name: jerusalem-municipality-report
description: Use when the user wants to file a "106" public-contact report with the Jerusalem Municipality (עיריית ירושלים, pniya la-106). Opens the official form at https://www.jerusalem.muni.il/he/contactus/106/ via Playwright, fills the applicant, contact, address, and description fields from user-supplied data, pauses for the user to solve the reCAPTCHA, then submits. Trigger phrases: "open a Jerusalem municipality report", "file a 106", "report something to iriya", "pniya la-iriya", "report a pothole / graffiti / broken streetlight to Jerusalem".
---

# Jerusalem Municipality Report (106)

Files a public-contact report ("פנייה ל-106") with the Jerusalem Municipality via the official online form. The form uses reCAPTCHA, so this skill uses a **visible** Playwright browser and hands the reCAPTCHA to the user — it does not try to solve it.

## Form URL

`https://www.jerusalem.muni.il/he/contactus/106/`

## Form fields (as of 2026-04-23)

All labels are in Hebrew; the skill may fill Hebrew or English values (Hebrew preferred for addresses).

### פרטי הפונה — Applicant details

| Label (HE) | English | Type | Required |
|---|---|---|---|
| שם פרטי | First name | text | yes |
| שם משפחה | Last name | text | yes |
| אמצעי זיהוי | ID type | select (`בחר` / `תעודת זהות` / `דרכון`) | yes |
| מספר זיהוי | ID number | text | yes |

### פרטי יצירת קשר — Contact details

| Label (HE) | English | Type | Required |
|---|---|---|---|
| מספר טלפון | Phone number | text | yes |
| מספר טלפון נוסף | Additional phone | text | no |
| דואר אלקטרוני | Email | text | yes |

### כתובת האירוע — Event address

| Label (HE) | English | Type | Required |
|---|---|---|---|
| יישוב | City (usually `ירושלים`) | text | yes |
| רחוב | Street | text | no |
| מספר בית | House number | text | no |

### תיאור הפנייה — Report description

| Label (HE) | English | Type | Required |
|---|---|---|---|
| תוכן הפנייה | Report body (character counter visible) | textarea | yes |
| צירוף קובץ | File attachment — up to 3 files, allowed types: png / doc / pdf / tif / jpg / gif, max 5 MB each | file | no |

### Submit

Button label: **שליחה** (Send), with `sendIco.png` icon.

### Success indicator

On success the page shows: **תודה רבה על פנייתך. פנייתך הועברה בהצלחה לעיריית ירושלים בתאריך DD.MM.YYYY**. A reference number is emailed / SMSed later.

## Procedure

### 1. Gather inputs from the user

Ask for any missing mandatory fields. Offer sensible defaults: city defaults to `ירושלים`, ID type defaults to `תעודת זהות`. Confirm the report body in the user's preferred language (Hebrew or English — the form accepts either, Hebrew gets faster triage).

Required before proceeding: first name, last name, ID type + number, phone, email, report body. Optional: additional phone, street, house number, attachments (list absolute paths).

### 2. Open the form via Playwright

Use the **Playwright MCP** tools from the `plugin_playwright` server. Do **not** use a headless browser — the user must see and solve the reCAPTCHA.

Exact tool names and validated call signatures (v1.0.0 of the official Playwright MCP):

| Action | Tool | Required parameters |
|---|---|---|
| Open URL | `mcp__plugin_playwright_playwright__browser_navigate` | `url` (string) |
| Get element refs | `mcp__plugin_playwright_playwright__browser_snapshot` | none (optional: `depth`, `filename`) |
| Batch-fill fields | `mcp__plugin_playwright_playwright__browser_fill_form` | `fields[]` — each `{name, type, ref, value}` where `type` ∈ `textbox \| checkbox \| radio \| combobox \| slider` |
| Type into one field | `mcp__plugin_playwright_playwright__browser_type` | `ref`, `text` (optional: `element`, `slowly`, `submit`) |
| Select dropdown | `mcp__plugin_playwright_playwright__browser_select_option` | `ref`, `values[]` |
| Upload files | `mcp__plugin_playwright_playwright__browser_file_upload` | `paths[]` (absolute paths) |
| Click | `mcp__plugin_playwright_playwright__browser_click` | `ref` (optional: `element`, `button`, `doubleClick`, `modifiers[]`) |
| Wait for text | `mcp__plugin_playwright_playwright__browser_wait_for` | one of `text`, `textGone`, `time` |
| Screenshot | `mcp__plugin_playwright_playwright__browser_take_screenshot` | `type` ∈ `png \| jpeg` (optional: `element`+`ref` together, `filename`, `fullPage`) |

Note: `ref` tokens come from the current `browser_snapshot` output. They are not stable across navigations — always re-snapshot before a new batch of interactions. `element` is a human-readable description used for the permission prompt; it must be supplied whenever `ref` is (except for `browser_click` where only `ref` is required).

Procedure:

1. **Navigate.** Call `browser_navigate` with `url: "https://www.jerusalem.muni.il/he/contactus/106/"`.
2. **Snapshot.** Call `browser_snapshot` (no args). Parse the returned accessibility tree to find refs for each form field by matching Hebrew labels (`שם פרטי`, `שם משפחה`, `אמצעי זיהוי`, `מספר זיהוי`, `מספר טלפון`, `מספר טלפון נוסף`, `דואר אלקטרוני`, `יישוב`, `רחוב`, `מספר בית`, `תוכן הפנייה`, `שליחה`).
3. **Fill in one batch.** Call `browser_fill_form` with a `fields` array like:
   ```json
   {
     "fields": [
       {"name": "First name",     "type": "textbox",  "ref": "<ref>", "value": "Daniel"},
       {"name": "Last name",      "type": "textbox",  "ref": "<ref>", "value": "Rosehill"},
       {"name": "ID type",        "type": "combobox", "ref": "<ref>", "value": "תעודת זהות"},
       {"name": "ID number",      "type": "textbox",  "ref": "<ref>", "value": "<id>"},
       {"name": "Phone",          "type": "textbox",  "ref": "<ref>", "value": "<phone>"},
       {"name": "Email",          "type": "textbox",  "ref": "<ref>", "value": "<email>"},
       {"name": "City",           "type": "textbox",  "ref": "<ref>", "value": "ירושלים"},
       {"name": "Street",         "type": "textbox",  "ref": "<ref>", "value": "<street>"},
       {"name": "House number",   "type": "textbox",  "ref": "<ref>", "value": "<num>"},
       {"name": "Report body",    "type": "textbox",  "ref": "<ref>", "value": "<body>"}
     ]
   }
   ```
   If `browser_fill_form` fails for the ID-type combobox (the form uses a custom widget, not a native `<select>`), fall back to `browser_click` on it, re-snapshot, then `browser_click` the `תעודת זהות` option. Attempt `browser_select_option` with `values: ["תעודת זהות"]` only if the snapshot shows a native `combobox` role.
4. **Attachments (optional).** If the user provided file paths, call `browser_click` on the **צירוף קובץ** button to open the file chooser, then `browser_file_upload` with `paths: ["/abs/path1", "/abs/path2", ...]` (max 3 files; accepted types: `png doc pdf tif jpg gif`; each ≤ 5 MB). Validate sizes and extensions before calling.
5. **Verify.** Call `browser_snapshot` again and confirm every required field is populated.

### 3. Hand the reCAPTCHA to the user

Before clicking submit, say in chat:

> The form is filled. Please solve the reCAPTCHA in the browser window, then reply "continue" and I'll submit.

Wait for the user's reply. Do **not** click the reCAPTCHA checkbox or iframe yourself (`browser_iframe_click` is explicitly forbidden here) — Google penalises automated interaction and the submission will be rejected.

### 4. Submit

Once the user confirms:

1. `browser_click` with `ref: "<ref-of-שליחה>"` (and `element: "Send button (שליחה)"` for the permission prompt).
2. `browser_wait_for` with `text: "תודה רבה על פנייתך"` — the success banner. Fall back to `text: "הועברה בהצלחה"` if the first times out.
3. `browser_take_screenshot` with `type: "png"`, `fullPage: true`, and `filename: "jerusalem-106-confirmation-YYYY-MM-DD.png"` (use today's date). Save under the current working directory, or `~/Documents/` if not in a project.
4. Report: success, the confirmation date shown on screen, and that the reference number will arrive by email/SMS.

### 5. If submission fails

- reCAPTCHA rejected → ask the user to re-solve and click Submit again.
- Field validation error (red text next to a field) → re-read the snapshot, identify the error, correct, resubmit.
- Server error → capture a screenshot, report the error text verbatim, and let the user decide whether to retry or file via phone (`106` from any Israeli phone).

## Guardrails

- **Do not fabricate personal details.** Every field must come from the user directly — never guess an ID number, phone, or email.
- **Do not attempt to bypass the reCAPTCHA.** Always hand it to the user.
- **Respect Hebrew/RTL.** When typing Hebrew values, paste them whole rather than character-by-character; `browser_type` handles this correctly.
- **One submission per invocation.** Do not loop or auto-file multiple reports.
- **Re-verify the form structure each run.** Municipal forms change without notice. Always re-read the snapshot rather than relying on cached selectors.

## Out of scope

- Payments, permits, parking-ticket appeals, building-permit submissions — these are separate online services on the Jerusalem Municipality portal, not the 106 form.
- Status lookups — use `https://www.jerusalem.muni.il/he/contactus/checkinquiry/` (separate skill candidate).
