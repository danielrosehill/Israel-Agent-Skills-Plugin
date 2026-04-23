---
name: update-plugin-readme
description: Use when the user wants to refresh the README of this plugin (or any Claude Code skills plugin) so that its "Skills" section reflects the current set of skills under `skills/*/SKILL.md`. Reads each skill's frontmatter (`name`, `description`, optional `category`), groups by category, sorts alphabetically within each group, and rewrites the README's Skills section between the `<!-- SKILLS:START -->` and `<!-- SKILLS:END -->` markers. Preserves everything else in the README (header, installation, license). A helper script at `scripts/generate-skills-section.py` does the extraction and emits the block on stdout; the skill is responsible for splicing it into the README. Trigger phrases - "update the plugin README", "regenerate the skills table", "refresh skills list on the plugin README", "the plugin README is out of date", "add the new skill to the README".
---

# Update Plugin README

Regenerates the "Skills" section of a Claude Code skills plugin README from the actual contents of its `skills/` directory.

## When to run

- A new skill has been added to the plugin's `skills/` folder.
- A skill's frontmatter `description` has been edited.
- A skill has been removed.
- The README drifts from reality (e.g. lists planned skills that already ship).

## Procedure

1. Run `python3 scripts/generate-skills-section.py <plugin-repo-path>` (default: the current plugin repo).
2. The script emits a block starting with `<!-- SKILLS:START -->` and ending with `<!-- SKILLS:END -->`. Capture its stdout.
3. Open `README.md`. Replace everything between those two markers with the new block. If the markers don't exist, locate the existing `## Skills` heading and replace that section (up to the next `##` heading) with the new block wrapped in markers; if there's no `## Skills` heading, insert the block after the README's opening paragraph.
4. Remove any "Planned scope" section that contains items now implemented. Leave genuinely unimplemented items alone but move them into an "Ideas" section if still plausible; drop them otherwise.
5. Show the user a diff before committing.

## Category taxonomy

The helper script uses folder-name inference. Preferred explicit `category` values (add to a skill's SKILL.md frontmatter if inference gets it wrong):

| Category | Scope |
|---|---|
| `Government & Civic` | Postal service, municipal reports, vehicle licensing, national services |
| `Healthcare` | HMOs, medicines, medical appointments |
| `Emergency Preparedness` | Shelters, Home Front Command guidelines, alerts |
| `Localization` | Hebrew language, fonts, translation |
| `Media & Information` | News feeds, media lookups |
| `Meta / Tooling` | Skills that manage the plugin itself |

Category ordering in the README is fixed (Government & Civic → Healthcare → Emergency Preparedness → Localization → Media & Information → Meta / Tooling → Other).

## Fallback category inference rules

If a SKILL.md lacks a `category` field, the script infers from folder name:

- `*-municipality-*`, `israel-post-*`, `*-government-*` → Government & Civic
- `maccabi-*`, `clalit-*`, `meuhedet-*`, `leumit-*`, `*-medicine-*`, `*-medical-*` → Healthcare
- `*-shelter-*`, `miklat*`, `home-front-*`, `pikud-*`, `*-alert-*` → Emergency Preparedness
- `hebrew-*`, `*-translation`, `*-fonts-*` → Localization
- `*-news-*`, `*-rss-*` → Media & Information
- `add-skill-*`, `update-plugin-*`, `install-*-plugin`, `*-plugin-*` → Meta / Tooling
- Otherwise → Other (prompt the user)

Prefer adding the `category` field to the skill's frontmatter over relying on inference.

## Description sanitisation

The full `description` frontmatter for a skill is discovery-oriented (contains "Use when..." preamble and trigger phrases). The README version is a plain, user-facing sentence. The helper script strips the `Use when the user wants to ` prefix, truncates at the first sentence boundary, cuts everything from `Trigger phrases` onward, capitalises the first letter, and drops the trailing period.

## Out of scope

- Regenerating the rest of the README (header, installation, license, related plugins). Those are hand-maintained.
- Editing individual SKILL.md files. This skill only reads them.
