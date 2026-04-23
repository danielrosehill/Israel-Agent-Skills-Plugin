# Israel-Agent-Skills

A Claude Code plugin that collects agent skills for Israel and Hebrew-specific workflows.

<!-- SKILLS:START -->
## Skills

### Government & Civic

| Skill | What it does |
|---|---|
| **`israel-post-appointment`** | Check the next available appointment, book an appointment, or cancel an appointment at an Israel Post branch (דואר ישראל, doar) — e.g. for package pickup (מסירת דואר ללקוח), general counter service (אשנב כל), foreign currency (מטבע חוץ), or vehicle ownership transfer (העברת בעלות רכב) |
| **`jerusalem-municipality-report`** | File a "106" public-contact report with the Jerusalem Municipality (עיריית ירושלים, pniya la-106) |

### Healthcare

| Skill | What it does |
|---|---|
| **`maccabi-medicine-lookup`** | Check whether a medicine is available through Maccabi Healthcare Services (מכבי שירותי בריאות) — whether it is listed, prescription-only (מרשם), included in the health basket (סל הבריאות), its out-of-pocket price, and any patient information leaflet |

### Meta / Tooling

| Skill | What it does |
|---|---|
| **`add-skill-to-plugin`** | Add a new skill to this plugin from rough / raw notes pasted into chat — scaffolds `skills/<name>/SKILL.md`, syncs the local plugin cache, commits, and pushes |
| **`update-plugin-readme`** | Refresh the README's Skills section from the current `skills/*/SKILL.md` inventory — reads each skill's frontmatter, groups by category, and rewrites the table between `<!-- SKILLS:START -->` / `<!-- SKILLS:END -->` markers |
<!-- SKILLS:END -->

## Related plugins

Shopping workflows for Israeli residents are provided separately by [`Claude-Israel-Shopping-Plugin`](https://github.com/danielrosehill/Claude-Israel-Shopping-Plugin) — install that plugin for any shopping, vendor, or price-comparison skills.

## Installation

```bash
claude plugins marketplace add danielrosehill/Claude-Code-Plugins
claude plugins install israel-agent-skills@danielrosehill
```

## License

MIT
