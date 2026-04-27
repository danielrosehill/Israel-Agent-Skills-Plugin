---
name: manage-israel-resource-lists
description: Use when the user wants to add, classify, or maintain entries across Daniel's two Israeli project resource indexes — `Israeli-AI-Tools-And-Ecosystem` (AI-native projects) and `Israeli-Open-Source-Projects` (broader non-AI / AI-adjacent). Trigger phrases include "add to the Israel AI list", "add to the Israeli projects index", "classify these Israeli repos", or any drop of GitHub URLs related to Israeli projects.
---

# Manage Israeli Resource Lists

Maintain two paired resource indexes:

| Repo | Local path | Scope |
|---|---|---|
| `danielrosehill/Israeli-AI-Tools-And-Ecosystem` | `~/repos/github/my-repos/Israeli-AI-Tools-And-Ecosystem` | AI-native: agents, agent skills, MCP servers, Hebrew-language AI, AI dashboards, AI plugins, voice agents |
| `danielrosehill/Israeli-Open-Source-Projects` | `~/repos/github/my-repos/Israeli-Open-Source-Projects` | Broader non-AI and AI-adjacent: scrapers, civic tech, finance utilities, careers, real estate, smart home, media, data sources useful as AI inputs |

A stray duplicate clone exists at `~/repos/github/my-repos/Israeli-AI-Tools-And-Utilities/` — **ignore it**. Both pointed at the same remote; the canonical local working copy is `Israeli-AI-Tools-And-Ecosystem`.

## When the user drops one or more GitHub URLs

### 1. Classify each URL

For every URL, fetch metadata via `gh repo view OWNER/REPO --json description,stargazerCount,topics,name,homepageUrl` (Bash, parallel calls when possible). For an org URL (e.g. `github.com/SomeOrg`), run `gh repo list OWNER --limit 15 --json name,description,stargazerCount` and treat each notable repo as its own item.

Classify each as:

- **AI** — project actively uses, embeds, or wraps AI/LLMs (chatbots, agents, AI-powered features, MCP servers, Claude/agent skills, voice agents, etc.)
- **AI-ADJACENT** — useful data source, scraper, or utility that AI builders would consume but doesn't itself use AI. Default this bucket to the **broader** repo unless it's clearly an "assistant" or has explicit AI features.
- **NON-AI** — purely a utility, scraper, or app with no AI angle.

AI → goes in `Israeli-AI-Tools-And-Ecosystem`.
AI-ADJACENT and NON-AI → go in `Israeli-Open-Source-Projects`.

### 2. Pick the section

**For `Israeli-AI-Tools-And-Ecosystem`:**

| Type | File | Section |
|---|---|---|
| Autonomous AI agent | `agents.md` | (single table) |
| Agent skill / Claude Code skill / skills bundle | `agent-skills.md` | (single table) |
| MCP server, AI tool, AI dashboard, AI plugin, voice agent | `mcps.md` | Pick one of the existing sections — Economics, Finance & Banking, Government & Open Data, Government Services, Healthcare, Insurance, Legal, Library, Real Estate, Safety & Emergency, Shopping & Retail, Transportation, Weather, Careers & Jobs, Dashboards, Plugins, Voice Agents, Other Projects |

**For `Israeli-Open-Source-Projects`:**

`README.md` — single file with sections: Aviation, Careers & Jobs, Finance & Banking, Government & Open Data, Media, Real Estate, Safety & Emergency, Shopping & Retail, Smart Home, Other. Add a new section if the entry doesn't fit any existing one (alphabetise the section list and the table of contents).

### 3. Dedupe before adding

Grep both repos for the OWNER/REPO slug before inserting:

```bash
grep -r "OWNER/REPO" ~/repos/github/my-repos/Israeli-AI-Tools-And-Ecosystem/ ~/repos/github/my-repos/Israeli-Open-Source-Projects/
```

If already present anywhere, skip and tell the user.

### 4. Append in the right table format

Both repos use the same row format:

```markdown
| [Display Name](https://github.com/OWNER/REPO) | One-sentence description (≤22 words) | ![](https://img.shields.io/github/stars/OWNER/REPO?style=social) |
```

- Use a clean human-readable display name, not the raw repo slug.
- Description ≤22 words, factual, no marketing tone.
- Append to the bottom of the relevant section table (no need to re-sort; sections are append-only by convention).

### 5. Commit and push each repo

For each modified repo, in its own commit:

```bash
cd ~/repos/github/my-repos/Israeli-AI-Tools-And-Ecosystem  # or the other one
git add -A
git commit -m "Add: <comma-separated short list of additions>"
git push
```

Do both repos in parallel Bash calls if both were touched.

### 6. Report

Brief summary to the user:

- N entries added to AI repo (list each: name → section)
- N entries added to broader repo (list each: name → section)
- Any URLs skipped as duplicates
- Both pushes confirmed

## Edge cases

- **Skill bundles vs individual skills** — bundle/collection repos (multiple skills in one repo) still go in `agent-skills.md`. Use a display name like "Skills IL — Government Services" to flag the bundle nature.
- **Borderline AI-ADJACENT** — when in doubt, ask the user before placing. The broader repo is the safer default.
- **AI-news-portal style sites** — these are AI-themed media but not AI tooling. Goes in the broader repo's Media section, not the AI repo.
- **Daniel's own repos** — these typically belong in `Israel-Projects-Index` (a separate index of his own work), not either of these third-party indexes. Flag and ask before adding.
- **Bagrut/education AI** — `mcps.md` has no Education section; place in Other Projects.
- **Hebrew-only language tooling without an AI angle** — belongs in the dedicated `Hebrew-Language-Projects-Index`, not these. Flag and ask.

## When the user asks to audit / clean up

- Run dedupe across both repos
- Check for stale links (`gh repo view` returning 404)
- Verify section ordering in the broader repo's TOC matches actual section order
- Ask before bulk-removing anything
