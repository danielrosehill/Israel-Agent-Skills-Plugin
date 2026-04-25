---
name: environment-check
description: Use when another skill in this plugin reports a missing dependency (Python module, Playwright browser, CLI tool), or when the user wants to verify or set up the runtime environment for Israel-Agent-Skills. Checks for required tools and offers to install them. Trigger phrases - "set up environment for X skill", "playwright not installed", "install dependencies for israel skills", "fix missing module", "ModuleNotFoundError: playwright".
---

# Environment Check & Install

Shared dependency manager for Israel-Agent-Skills. Other skills delegate here when they detect a missing tool, instead of bundling install logic each.

## Supported toolchains

| Tool | Used by | Install command (Linux/macOS) |
|------|---------|-------------------------------|
| `playwright` (Python) + Chromium | `nsc-travel-threat`, `ben-gurion-flight-board`, any browser-driven skill | `pipx install playwright && pipx runpip playwright install playwright && playwright install chromium` — or `pip install --user playwright && python3 -m playwright install chromium` |
| `requests` | `fiber-availability-check`, RSS skills | `pip install --user requests` |
| `pyyaml` | skills reading user prefs | `pip install --user pyyaml` |
| `feedparser` | `israel-news-rss` | `pip install --user feedparser` |

## Procedure

1. **Detect the runtime.** Run `python3 -c "import sys; print(sys.executable, sys.version_info[:2])"` — that interpreter is the one the plugin's scripts will use (they all use `#!/usr/bin/env python3`).

2. **Probe for the missing dependency.** For Python modules:
   ```bash
   python3 -c "import <module>" 2>&1
   ```
   For Playwright's browser binary specifically (the module-import check is not enough — the Chromium binary is separate):
   ```bash
   python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop(); print('ok')"
   ```

3. **If pipx already has the tool but the system `python3` doesn't see it** (common with `playwright`), prefer fixing the import path rather than reinstalling. Either install into user-site as well (`pip install --user <pkg>`), or point `PYTHONPATH` at the pipx venv site-packages for that one invocation.

4. **Confirm with the user before installing anything.** Show: what's missing, what command will run, whether it touches user-site (`--user`) or a system location. Never run `sudo pip install`.

5. **For Playwright browser binaries**, respect any existing `PLAYWRIGHT_BROWSERS_PATH` env var. If the user has one set (check `env | grep PLAYWRIGHT_BROWSERS_PATH`), use it; otherwise let Playwright use its default (`~/.cache/ms-playwright`).

6. **Verify** by re-running the probe after install. Report success or paste the new error.

## What this skill does NOT do

- Does not install system packages (apt, brew, dnf) — surface those instructions to the user instead.
- Does not modify shell rc files. If a `PATH` change is needed, print the line for the user to add.
- Does not manage virtualenvs for the user — the plugin's scripts use whatever `python3` is on PATH.

## Reporting back to the calling skill

Once the dependency is satisfied, tell the user "you can re-run the [skill] command now" and let the original conversation resume there. Do not chain into the original skill yourself.
