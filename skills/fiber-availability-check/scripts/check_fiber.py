#!/usr/bin/env python3
"""Check fiber-optic internet availability at an Israeli street address across
multiple providers (Bezeq, HOT). Documents Partner / Cellcom / IBC as unsupported.

Reads defaults from ~/.config/israel-agent-skills/preferences.yaml (or fiber.env)
so the user can run with no args after onboarding.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta

import preferences
import providers


def run(addr: dict, chosen: list[str], include_unsupported: bool) -> dict:
    results = {name: providers.PROVIDERS[name](**addr) for name in chosen}
    out = {
        "query": addr,
        "results": results,
        "unsupported": providers.UNSUPPORTED if include_unsupported else {},
        "fetched_at": datetime.now(timezone(timedelta(hours=3))).isoformat(timespec="seconds"),
        "test_address_note": "Reference test address: city='ירושלים' street='בן יהודה' house='1'",
    }
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Check Israeli fiber availability across providers.")
    p.add_argument("--city", help="City name in Hebrew, e.g. ירושלים")
    p.add_argument("--street", help="Street name in Hebrew, e.g. בן יהודה")
    p.add_argument("--house", help="House number, e.g. 1")
    p.add_argument("--entrance", default=None, help="Entrance (optional)")
    p.add_argument(
        "--provider",
        action="append",
        choices=list(providers.PROVIDERS.keys()) + ["all"],
        help="Provider(s) to check. Repeatable. Default: all.",
    )
    p.add_argument("--stdin", action="store_true",
                   help="Read JSON {city,street,house,entrance?,providers?} from stdin")
    p.add_argument("--show-unsupported", action="store_true",
                   help="Include a note in output about providers that cannot be automated")
    args = p.parse_args()

    if args.stdin:
        blob = json.loads(sys.stdin.read())
        addr = preferences.resolve_address(
            blob.get("city"), blob.get("street"), blob.get("house"), blob.get("entrance"),
        )
        chosen_in = blob.get("providers")
    else:
        addr = preferences.resolve_address(args.city, args.street, args.house, args.entrance)
        chosen_in = args.provider

    if not chosen_in or "all" in (chosen_in or []):
        chosen = list(providers.PROVIDERS.keys())
    else:
        chosen = list(dict.fromkeys(chosen_in))

    result = run(addr, chosen, args.show_unsupported)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
