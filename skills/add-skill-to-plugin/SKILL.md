---
name: add-skill-to-plugin
description: Use when Daniel wants to add a new skill to the Israel-Agent-Skills-Plugin repo based on rough / raw notes he pastes into the chat. Takes unstructured bullet points, URLs, field notes, Hebrew snippets and example pages, and turns them into a well-formed `skills/<skill-name>/SKILL.md` file that matches the conventions of existing skills in this repo (YAML frontmatter with `name` + rich `description` including trigger phrases, then a structured markdown body). Also syncs the new skill into the local plugin cache at `~/.claude/plugins/cache/danielrosehill/israel-agent-skills/<version>/skills/` so it is usable immediately, commits, and pushes. Trigger phrases: "add a skill to this plugin", "new skill for israel-agent-skills", "turn these notes into a skill", "scaffold a skill from my raw notes", "save this as a skill in the repo".
---

# Add a Skill to Israel-Agent-Skills-Plugin

Meta-skill that converts Daniel's rough notes into a properly structured skill file inside this repo and activates it locally.

## When to invoke

Daniel pastes free-form notes describing something he wants Claude to be able to do in the context of Israel / Hebrew / regional workflows — e.g. "check if a medicine is on Maccabi", "file a 106 report with Jerusalem municipality", "look up bus times on Egged". The notes will typically include:

- A rough task description
- One or more URLs (landing page + example detail pages)
- Hebrew field labels copy-pasted from the site
- Hints about what the user actually cares about in the output
- Occasionally gotchas (captcha, autocomplete, RTL layout, login required)

Do not wait for a clean spec — these notes are the input.

## Repo conventions (match these)

Plugin root: `/home/daniel/repos/github/my-repos/Israel-Agent-Skills-Plugin/`

Layout:

```
.claude-plugin/plugin.json
skills/
  <skill-name>/
    SKILL.md
```

- **Skill directory name**: `kebab-case`, descriptive, prefixed with the service or domain when useful (e.g. `jerusalem-municipality-report`, `maccabi-medicine-lookup`). Not Train-Case — skill dirs are lowercase-kebab even though the *repo* name is Train-Case.
- **One `SKILL.md` per skill**. Additional assets (reference data, schemas) can live alongside but keep the directory lean.
- **Frontmatter** is YAML with two fields:
  - `name`: must match the directory name exactly.
  - `description`: a long, information-dense paragraph. This is what Claude sees when deciding whether to trigger the skill, so it must:
    - State when to use the skill ("Use when the user wants to…").
    - Mention the concrete site / API / artefact involved, including Hebrew names where relevant (e.g. `עיריית ירושלים`, `סל הבריאות`).
    - End with a list of explicit **trigger phrases** the user is likely to say, in both English and Hebrew-transliterated forms where natural.
- **Body** follows a loose but consistent structure — look at `skills/jerusalem-municipality-report/SKILL.md` and `skills/maccabi-medicine-lookup/SKILL.md` as canonical examples. Typical sections:
  - One-sentence restatement of what the skill does.
  - Entry point URL / API endpoint.
  - How to search / navigate (including UI quirks: autocomplete, reCAPTCHA, RTL, cookie banners).
  - What to extract (tables of Hebrew label ↔ English ↔ type ↔ required).
  - Output format (show an example block).
  - Playwright / tooling notes.
  - Out of scope.
- **Never invent facts.** If the raw notes don't cover something (e.g. selector IDs, exact price-field label), say so in the SKILL.md rather than guessing.

## Procedure

1. **Read the notes.** Identify: skill name candidate, primary URL(s), what signals the user cares about in the output, any gotchas.
2. **Confirm the directory name** with Daniel only if it's genuinely ambiguous. Otherwise pick a sensible kebab-case name and proceed (auto mode).
3. **Read one existing skill** (`skills/jerusalem-municipality-report/SKILL.md` or `skills/maccabi-medicine-lookup/SKILL.md`) to mirror structure and tone.
4. **Write** `skills/<new-skill>/SKILL.md` with:
   - Frontmatter `name` + dense `description` with trigger phrases.
   - Body sections drawn from the notes, with Hebrew labels preserved verbatim.
   - Explicit "not inferred from notes" markers where notes were silent.
5. **Sync to local cache** so the skill is active in the user's current Claude Code session without a reinstall:
   ```bash
   VER=$(jq -r .version /home/daniel/repos/github/my-repos/Israel-Agent-Skills-Plugin/.claude-plugin/plugin.json)
   CACHE=/home/daniel/.claude/plugins/cache/danielrosehill/israel-agent-skills/$VER/skills
   cp -r /home/daniel/repos/github/my-repos/Israel-Agent-Skills-Plugin/skills/<new-skill> "$CACHE"/
   ```
   If the cache dir for that version doesn't exist, skip the sync and tell Daniel — it means the plugin hasn't been installed from the marketplace at that version yet.
6. **Commit and push** from the repo root:
   ```bash
   git add -A
   git commit -m "Add <new-skill> skill\n\n<one-line summary>"
   git push
   ```
   Per Daniel's global git rules: always commit all pending changes and push immediately. Do not create feature branches — this repo uses `master` directly.
7. **Report back** with: the new skill path, the commit hash, whether the local cache sync succeeded, and any gaps in the notes that the SKILL.md flagged as unknown.

## Optional follow-ups (ask before doing)

- Bump the plugin version in `.claude-plugin/plugin.json` if Daniel says this is a release-worthy addition.
- Add the new skill to README.md if the README maintains a skill index (check before editing).

## Ethical skill development (apply when authoring the SKILL.md)

This plugin's skills frequently interact with Israeli government / health / municipal / commercial websites that have authentication, autocomplete, reCAPTCHA, RTL quirks, and assorted anti-bot friction. Knowledge of how to negotiate those surfaces is genuinely dual-use — useful for the ordinary white-hat user, useful for abuse at scale.

Follow the [Ethical Skill Development](https://github.com/danielrosehill/Ethical-Skill-Development) code of practice when authoring a new skill in this plugin:

1. **Decouple dev artefacts from the published SKILL.md.** Captured payloads, full HAR files, detailed maps of auth/CAPTCHA challenges, fingerprint observations, and probing scripts belong in the **private dev workspace** (`Israel-Agent-Skills-Dev` — `~/repos/github/my-repos/Israel-Agent-Skills-Dev/`). The published `SKILL.md` in this plugin should contain only what's needed at runtime.
2. **Sanitise the published SKILL.md.** Skills can't hide what they do at runtime, but the SKILL.md does not need to narrate the target site's defensive posture. Specifically:
   - Describe **outcomes** (what the user gets), not bypasses.
   - Don't enumerate which header/cookie/timing the site checks, or precisely how the skill negotiates with each defensive surface.
   - Don't ship development comments like "the site rejects requests without X within 200ms of Y" — those stay in the dev workspace.
   - Hebrew label tables, output schema, and UI quirks the *user* needs to know about are fine; tutorial-grade write-ups of anti-bot internals are not.
3. **Be willing not to publish.** Some skills, on reflection, should stay in the dev workspace only. If publishing materially advantages bad actors, leave it private.

Apply this judgement when transforming the raw notes in step 1 of the Procedure. If notes contain detailed anti-bot or auth-defence observations, route those to the dev workspace and write a sanitised version into the published `SKILL.md`.

## Out of scope

- Does not implement the skill's runtime logic — only authors the SKILL.md. The skill itself is executed by Claude at invocation time using whatever tools it declares (Playwright, WebFetch, etc.).
- Does not publish to the plugin marketplace. That's a separate release flow.
- Does not invent Hebrew translations or selectors that weren't in the notes.
