"""Load user-local preferences for Israel-Agent-Skills.

Canonical path: ~/.config/israel-agent-skills/preferences.yaml (gitignored, never in repo).
Also supports a .env-style file at ~/.config/israel-agent-skills/fiber.env as a lighter-weight
alternative for this skill only. Environment variables win over files so callers can override
per-invocation.

Keys consulted by this skill:
- default_city        (e.g. "ירושלים")
- default_street      (e.g. "בן יהודה")
- default_house       (e.g. "1")
- default_entrance    (optional)
- phone               (E.164 or local; used when a provider requests it for the lead step — currently unused but surfaced for future providers)
- email               (ditto)

Env var overrides (uppercase, prefixed):
  IL_FIBER_CITY, IL_FIBER_STREET, IL_FIBER_HOUSE, IL_FIBER_ENTRANCE, IL_FIBER_PHONE, IL_FIBER_EMAIL
"""
from __future__ import annotations

import os
from pathlib import Path

CONFIG_DIR = Path(os.path.expanduser("~/.config/israel-agent-skills"))
YAML_PATH = CONFIG_DIR / "preferences.yaml"
ENV_PATH = CONFIG_DIR / "fiber.env"

_ENV_MAP = {
    "default_city": "IL_FIBER_CITY",
    "default_street": "IL_FIBER_STREET",
    "default_house": "IL_FIBER_HOUSE",
    "default_entrance": "IL_FIBER_ENTRANCE",
    "phone": "IL_FIBER_PHONE",
    "email": "IL_FIBER_EMAIL",
}


def _parse_yaml_flat(text: str) -> dict:
    out: dict = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line or ":" not in line or line.startswith(" "):
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _parse_env(text: str) -> dict:
    out: dict = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def load() -> dict:
    """Return merged preferences dict. Missing keys simply absent."""
    prefs: dict = {}

    if YAML_PATH.is_file():
        try:
            prefs.update(_parse_yaml_flat(YAML_PATH.read_text(encoding="utf-8")))
        except OSError:
            pass

    if ENV_PATH.is_file():
        try:
            flat = _parse_env(ENV_PATH.read_text(encoding="utf-8"))
            # .env uses the IL_FIBER_* names; map back to canonical keys
            reverse = {v: k for k, v in _ENV_MAP.items()}
            for k, v in flat.items():
                prefs[reverse.get(k, k)] = v
        except OSError:
            pass

    for canonical, env_name in _ENV_MAP.items():
        if os.environ.get(env_name):
            prefs[canonical] = os.environ[env_name]

    return prefs


def resolve_address(args_city: str | None, args_street: str | None, args_house: str | None, args_entrance: str | None) -> dict:
    """Merge CLI args with preferences. CLI wins. Return {city, street, house, entrance}.

    Raises SystemExit with an onboarding hint if any of the three required fields
    are still missing after the merge.
    """
    prefs = load()
    city = args_city or prefs.get("default_city")
    street = args_street or prefs.get("default_street")
    house = args_house or prefs.get("default_house")
    entrance = args_entrance if args_entrance is not None else prefs.get("default_entrance", "")

    missing = [name for name, val in (("city", city), ("street", street), ("house", house)) if not val]
    if missing:
        raise SystemExit(
            f"Missing required field(s): {', '.join(missing)}. "
            f"Either pass --{missing[0]} on the CLI, or create {YAML_PATH} with keys "
            f"default_city / default_street / default_house (see SKILL.md)."
        )

    return {"city": city, "street": street, "house": str(house), "entrance": entrance or ""}
