---
name: install-companion-plugins
description: Use when the user wants to install or review other Claude Code plugins that complement this Israel-Agent-Skills plugin — specifically Daniel Rosehill's related plugins for Israeli shopping workflows (israel-shopping) and Green Invoice operations (greeninvoice-ops). Reads the curated list from `data/companion-plugins.yaml`, shows the user what each plugin does, confirms the selection, and runs the `claude plugins marketplace add` + `claude plugins install` commands. Does not install anything without explicit confirmation. Trigger phrases - "install related israel plugins", "what other plugins go with israel-agent-skills", "install israel shopping plugin", "install greeninvoice plugin", "install companion plugins", "show me related plugins".
---

# Install Companion Plugins

Helps the user install other Claude Code plugins that pair well with Israel-Agent-Skills. The curated list lives in `data/companion-plugins.yaml` — it's a maintained shortlist, not a general plugin discovery tool.

## Procedure

1. Read `data/companion-plugins.yaml`.
2. For each plugin, check whether it's already installed:
   ```bash
   claude plugins list 2>/dev/null | grep -qE '^\s*{slug}\b'
   ```
   Label each entry `installed` / `not installed`.
3. Present the list to the user as a short menu — one line per plugin with topic, blurb, and install status.
4. Ask which to install (accept `all`, `none`, or a comma-separated subset of slugs).
5. If the marketplace isn't registered, add it once (idempotent):
   ```bash
   claude plugins marketplace add {marketplace}
   ```
6. Install each selected plugin:
   ```bash
   claude plugins install {slug}@{owner}
   ```
7. Re-check with `claude plugins list` and report the post-install state.

## What this skill does NOT do

- Install plugins without explicit user confirmation.
- Uninstall anything.
- Discover plugins beyond the curated list. If the user asks for unrelated plugins, point them at `claude plugins marketplace browse` rather than extending this skill ad-hoc.
- Modify Claude Code settings, permissions, or MCP configs.

## Extending the list

Add a new entry to `data/companion-plugins.yaml` with `slug`, `owner`, `repo`, `topic`, and `blurb`. The `slug` must match the target plugin's `.claude-plugin/plugin.json` `name` field — verify before adding.
