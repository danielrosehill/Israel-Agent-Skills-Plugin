---
name: fiber-availability-check
description: Check whether fiber-optic internet is deployed at an Israeli street address, across multiple providers (Bezeq Bfiber and HOT Fiber today). Use when the user asks "is there fiber at my address", "can I get Bfiber", "does HOT fiber reach [street]", "fiber availability in [city]", "are there sivim opti'im [סיבים אופטיים] at this address", or is comparing ISP coverage before ordering. Supports a reference test address (בן יהודה 1, ירושלים) and reads defaults from a local preferences file so the user can check their own address with no arguments.
---

# Israel Fiber Availability Check

Multi-provider address-level fiber availability lookup for Israel. Plain-HTTP (no browser), device-agnostic.

## Providers

| Provider | Status | Method |
|----------|--------|--------|
| **Bezeq** (Bfiber) | Supported | Public JSON API on `bezeq.co.il` |
| **HOT** (HOT Fiber) | Supported | Public JSON API on `hot.net.il` |
| Partner | Not supported | No public address check — their form is lead-capture only (name + phone). |
| Cellcom | Not supported | React SPA behind Imperva/Incapsula; would need headless-browser escalation. |
| IBC / Unlimited | Not supported | Brand sites parked / offline at time of authoring. |

Call with `--show-unsupported` to include these notes in the output.

## Reference test address

Use **`city=ירושלים, street=בן יהודה, house=1`** to smoke-test the pipeline. As of authoring, Bezeq reports `available` and HOT reports `unavailable` at this address — a healthy signal that both backends are reachable and the normalizer is working.

## Local preferences (user details never in the repo)

User-specific defaults live **outside** the plugin repo. Two options, in precedence order (last wins):

1. **YAML (recommended)** — `~/.config/israel-agent-skills/preferences.yaml`:
    ```yaml
    default_city: ירושלים
    default_street: בן יהודה
    default_house: "1"
    default_entrance: ""      # optional
    phone: "+9725xxxxxxxx"    # reserved for future providers that need a lead step
    email: "you@example.com"
    ```
2. **.env-style** — `~/.config/israel-agent-skills/fiber.env`:
    ```bash
    IL_FIBER_CITY=ירושלים
    IL_FIBER_STREET=בן יהודה
    IL_FIBER_HOUSE=1
    IL_FIBER_PHONE=+9725xxxxxxxx
    IL_FIBER_EMAIL=you@example.com
    ```
3. **Process env vars** of the same names (highest precedence, overrides files).

With any of these set, the user can run the skill with zero arguments and get a check for their own address. CLI flags always win over preferences.

Permissions: the prefs directory is user-scoped. If you ever add secrets (API tokens), put them under `~/.config/israel-agent-skills/secrets/` with `chmod 600` and do **not** co-mingle with the plain preferences file.

## Usage

```bash
# Check all supported providers for the test address
python3 scripts/check_fiber.py --city "ירושלים" --street "בן יהודה" --house 1

# Use defaults from ~/.config/israel-agent-skills/preferences.yaml (no args)
python3 scripts/check_fiber.py

# One provider only
python3 scripts/check_fiber.py --provider bezeq
python3 scripts/check_fiber.py --provider hot

# Include the notes about unsupported providers
python3 scripts/check_fiber.py --show-unsupported

# JSON in, JSON out
echo '{"city":"ירושלים","street":"בן יהודה","house":1,"providers":["bezeq","hot"]}' \
  | python3 scripts/check_fiber.py --stdin
```

## Output schema

```json
{
  "query": {"city": "...", "street": "...", "house": "1", "entrance": ""},
  "results": {
    "bezeq": {
      "provider": "bezeq",
      "status": "available | coming_soon | unavailable | address_not_found | unknown | error",
      "status_code": 1,
      "summary": "human-readable one-liner",
      "error": null,
      "raw": { ... provider response ... }
    },
    "hot": { ... same shape ... }
  },
  "unsupported": {},
  "fetched_at": "2026-04-23T21:06:22+03:00",
  "test_address_note": "..."
}
```

Statuses are normalized across providers so callers can compare coverage without provider-specific glue.

## Notes

- No secrets required. Both supported endpoints are public.
- City and street names should be in Hebrew for best matching. Both Bezeq and HOT share the same `cityId=3000` for Jerusalem, which is why the same preference file works across providers.
- If a future provider requires a phone/email for a lead-style submit step, the prefs file already has those slots — the skill will pick them up without a code change to the CLI surface.
- If either provider's response shape changes (e.g. another layer of JSON wrapping, new status code), failures show as `status: "error"` with the exception string so it's obvious what broke.
