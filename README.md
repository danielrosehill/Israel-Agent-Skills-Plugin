# Israel-Agent-Skills

A Claude Code plugin that collects agent skills for Israel and Hebrew-specific workflows.

<!-- SKILLS:START -->
## Skills

### Government & Civic

| Skill | What it does |
|---|---|
| **`israel-post-appointment`** | Check the next available appointment, book an appointment, or cancel an appointment at an Israel Post branch (דואר ישראל, doar) — e.g. for package pickup (מסירת דואר ללקוח), general counter service (אשנב כל), foreign currency (מטבע חוץ), or vehicle ownership transfer (העברת בעלות רכב) |
| **`jerusalem-municipality-report`** | File a "106" public-contact report with the Jerusalem Municipality (עיריית ירושלים, pniya la-106) |
| **`kol-zchut-lookup`** | Search Kol Zchut (כל זכות) — Israel's plain-language citizen rights portal — for answers on employment, consumer, tenancy, healthcare, and social-security rights. Uses the site's MediaWiki API headlessly and returns the top article titles, URLs, and snippets |

### Healthcare

| Skill | What it does |
|---|---|
| **`maccabi-medicine-lookup`** | Check whether a medicine is available through Maccabi Healthcare Services (מכבי שירותי בריאות) — whether it is listed, prescription-only (מרשם), included in the health basket (סל הבריאות), its out-of-pocket price, and any patient information leaflet |

### Emergency Preparedness

| Skill | What it does |
|---|---|
| **`home-front-command-guidelines`** | Answer questions about Israeli civilian emergency / shelter / protection guidelines issued by Pikud HaOref — rocket/missile behaviour, shelter arrival times, hazardous-materials events, terrorist and drone infiltration, home-protected-space (mamad) preparation, emergency equipment lists, and official alert channels. Always cites the upstream `oref.org.il/eng` source |
| **`miklatim-lookup`** | Find a public bomb shelter (miklat tziburi, מקלט ציבורי) near a location in Israel — by address, neighbourhood, coordinates, or current position — with address, type, capacity, accessibility, and Google Maps / Waze directions |

### Finance

| Skill | What it does |
|---|---|
| **`salary-conversion`** | Convert a salary between Israeli and world conventions — Israeli salaries are stated monthly in shekels (NIS/ILS), world salaries annually in local currency. Uses today's FX rate; rounds the shekel side to the nearest integer |

### Meta / Tooling

| Skill | What it does |
|---|---|
| **`add-skill-to-plugin`** | Add a new skill to this plugin from rough / raw notes pasted into chat — scaffolds `skills/<name>/SKILL.md`, syncs the local plugin cache, commits, and pushes |
| **`discover-israel-skills`** | Browse and install third-party Israel-focused Claude Code agent skills (tax/finance, accounting, government, pharmacies, rail, post, cinema, legal, communication) from a curated list covering the `skills-il/*` collections and standalone repos |
| **`install-companion-plugins`** | Install or review other Claude Code plugins that complement this plugin |
| **`update-plugin-readme`** | Refresh the README's Skills section from the current `skills/*/SKILL.md` inventory — reads each skill's frontmatter, groups by category, and rewrites the table between `<!-- SKILLS:START -->` / `<!-- SKILLS:END -->` markers |
<!-- SKILLS:END -->

## Installation

```bash
claude plugins marketplace add danielrosehill/Claude-Code-Plugins
claude plugins install israel-agent-skills@danielrosehill
```

## License

MIT
