---
name: discover-israel-skills
category: Meta / Tooling
description: Use when the user wants to browse, discover, or install third-party Claude Code agent skills focused on Israel (tax/accounting, government services, healthcare pharmacies, rail, cinema, post tracking, legal research, security compliance, communication, etc.) — skills authored by people other than Daniel, indexed here for easy installation alongside this plugin. Reads a curated list from `data/third-party-skills.yaml` (monorepo skill collections from github.com/skills-il plus standalone skill repos), shows each entry with its source repo / subpath / blurb, confirms the user's selection, and installs the chosen skill(s) into `~/.claude/skills/<name>/` via `git clone` or sparse-checkout. Does not install anything without explicit confirmation. Also surfaces the awesome-list reference (alexpolonsky/awesome-agent-skills-israel) for broader discovery. Trigger phrases - "what other israel skills are there", "install israeli agent skills", "find me a skill for [israel rail / clalit / maccabi pharmacy / cinema / israel post / tax / accounting]", "discover israel skills", "browse israel agent skills", "third-party israel skills".
---

# Discover Israel Agent Skills

Curated index of third-party Claude Code agent skills for life in Israel, with one-command install. The list lives in `data/third-party-skills.yaml` and is the authoritative source — do not enumerate entries in the README; direct users to invoke this skill.

## What's indexed

Three shapes of upstream source:

1. **Monorepo collections** — `github.com/skills-il/*` organises several skills per repo, one per subfolder (each with its own `SKILL.md`). Install the specific subfolder, not the whole repo.
2. **Standalone skill repos** — one skill per repo, `SKILL.md` at the top level (or under a stated subpath).
3. **Awesome list** — `alexpolonsky/awesome-agent-skills-israel` is a human-readable index only; point the user there for browsing beyond the curated shortlist.

Projects that are *not* Claude Code skills (e.g. full web apps like `shneorAziza/MyLaw`) are intentionally excluded even if the user named them — mention that when asked.

## Procedure

1. Read `data/third-party-skills.yaml`.
2. Group the entries by `category` and show a numbered menu — one line per skill: `<name> — <blurb> (<owner>/<repo>[/<subpath>])`.
3. For each entry, check whether it's already installed:
   ```bash
   test -d "$HOME/.claude/skills/<install_name>" && echo installed || echo missing
   ```
4. Ask which to install (`all`, `none`, or a comma-separated list of names).
5. For each selected entry:
   - **Standalone repo, whole repo:**
     ```bash
     git clone --depth 1 https://github.com/<owner>/<repo>.git "$HOME/.claude/skills/<install_name>"
     ```
   - **Monorepo subpath** (sparse):
     ```bash
     tmp=$(mktemp -d)
     git clone --depth 1 --filter=blob:none --sparse https://github.com/<owner>/<repo>.git "$tmp"
     git -C "$tmp" sparse-checkout set <subpath>
     mv "$tmp/<subpath>" "$HOME/.claude/skills/<install_name>"
     rm -rf "$tmp"
     ```
6. Verify the installed folder contains a `SKILL.md`; if not, warn the user and leave the folder in place for inspection.
7. Remind the user to restart Claude Code (or reload skills) so the new skill is picked up.

## What this skill does NOT do

- Install without explicit user confirmation.
- Uninstall, update, or upgrade existing skills (point users at `rm -rf ~/.claude/skills/<name>` + re-install if they ask).
- Install skills with `package.json` scripts that require `npm install` — flag those and let the user run npm themselves; they may have their own Node environment preferences.
- Vouch for the quality or safety of third-party skills. Surface the repo URL so the user can audit before running.
- Add repos to the list automatically. Maintainers add entries to the YAML after reviewing the upstream.

## Safety

Third-party skill folders can contain executable scripts invoked by the agent. Before running an install, show the user the repo URL and a one-line blurb; encourage them to open the repo in a browser first if they don't recognise the author. Never auto-run post-install setup scripts.

## Extending the list

Edit `data/third-party-skills.yaml`. Each entry needs:

- `install_name` — the target folder name under `~/.claude/skills/` (kebab-case).
- `owner`, `repo` — GitHub coordinates.
- `subpath` (optional) — set for monorepo entries.
- `category` — one of `Tax & Finance`, `Accounting`, `Government`, `Healthcare`, `Transport`, `Post & Logistics`, `Media & Entertainment`, `Legal & Compliance`, `Communication`, `Other`.
- `blurb` — one line, plain English.
- `upstream_url` — canonical URL for audit.

Verify the upstream skill actually has a `SKILL.md` (or `SKILL_HE.md`) before adding.
