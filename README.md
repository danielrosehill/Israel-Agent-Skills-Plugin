# Israel-Agent-Skills

A Claude Code plugin that collects agent skills for Israel and Hebrew-specific workflows.

<!-- SKILLS:START -->
## Skills

### Government & Civic

| Skill | What it does |
|---|---|
| **`israel-post-appointment`** | Check the next available appointment, book an appointment, or cancel an appointment at an Israel Post branch (דואר ישראל, doar) — e.g. for package pickup (מסירת דואר ללקוח), general counter service (אשנב כל), foreign currency (מטבע חוץ), or vehicle ownership transfer (העברת בעלות רכב) |
| **`jerusalem-municipality-report`** | File a "106" public-contact report with the Jerusalem Municipality (עיריית ירושלים, pniya la-106) |
| **`kol-zchut-lookup`** | Use when the user asks a question about Israeli citizen / consumer / employment / tenant / social rights or entitlements — anything of the form "what are my rights when...", "what does Israeli employment law say about...", "am I entitled to...", "what's the law on [notice period / severance / rent increases / health basket / disability benefits / maternity leave / unemployment / reserves duty / etc.]" |

### Healthcare

| Skill | What it does |
|---|---|
| **`maccabi-medicine-lookup`** | Check whether a medicine is available through Maccabi Healthcare Services (מכבי שירותי בריאות) — whether it is listed, whether it is prescription-only (POM, מרשם), whether it is included in the health basket / sal briut (סל הבריאות, subsidised), its out-of-pocket price to the patient, and a link to the patient information leaflet (עלון לצרכן) if one is published |
| **`drug-co-il-lookup`** | Look up an Israeli medication on drug.co.il (the Pharmacists Organization's public drug-info site) — Hebrew + English name, manufacturer, active ingredient, ATC, dosage form, prescription/OTC status, health-basket inclusion, approved indication, equivalent generics, and links to MOH-hosted patient leaflets in Hebrew/English/Arabic |
| **`israel-drugs-registry-lookup`** | Look up a medicine in the official Israeli Drug Registry (israeldrugs.health.gov.il, MOH מאגר התרופות) — registration number (דרגיסטר), licence holder, manufacturer(s), ATC code, full approved indication text, registration status (active / cancelled / suspended), basket inclusion record, and the official patient and physician leaflets |
| **`medicine-availability-check`** | Orchestrator for "is X available to me in Israel" questions — chains the health-fund, pharma, and regulatory lookups in the right order, climbing only as far as the question requires |

### Emergency Preparedness

| Skill | What it does |
|---|---|
| **`home-front-command-guidelines`** | Israeli civilian emergency / shelter / protection guidelines issued by Pikud HaOref (Home Front Command, פיקוד העורף) — e.g. what to do during a rocket or missile alert, how long they have to reach a protected space (mamad / miklat), what to do in a vehicle, on the road, or outdoors during a siren, hazardous-materials events, terrorist infiltration, hostile aerial vehicle (drone) infiltration, how to prepare a home protected space, emergency equipment lists, family emergency planning, and official alert channels |
| **`miklatim-lookup`** | Find a public bomb shelter (miklat tziburi, מקלט ציבורי) near a location in Israel — by address, neighbourhood, coordinates, or current position — with address, type, capacity, accessibility, and Google Maps / Waze directions |

### Finance

| Skill | What it does |
|---|---|
| **`salary-conversion`** | Convert a salary between Israeli and world conventions — Israeli salaries are stated **monthly in shekels (NIS / ILS)**, while most other countries state salaries **annually in their local currency** (USD, EUR, GBP, etc.) |

### Media & Information

| Skill | What it does |
|---|---|
| **`israel-news-rss`** | Use when the user wants the latest Israeli news headlines from major outlets via RSS, in English or Hebrew |

### Meta / Tooling

| Skill | What it does |
|---|---|
| **`list-skills`** | Categorised map of every skill in this plugin, grouped by area (Healthcare & Medication, Emergency, Travel, Government, Finance, Media, Connectivity, Meta) — read this first to find the right entry point without scanning every SKILL.md |
| **`add-skill-to-plugin`** | Add a new skill to the Israel-Agent-Skills-Plugin repo based on rough / raw notes he pastes into the chat |
| **`discover-israel-skills`** | Browse, discover, or install third-party Claude Code agent skills focused on Israel (tax/accounting, government services, healthcare pharmacies, rail, cinema, post tracking, legal research, security compliance, communication, etc.) — skills authored by people other than Daniel, indexed here for easy installation alongside this plugin |
| **`install-companion-plugins`** | Install or review other Claude Code plugins that complement this Israel-Agent-Skills plugin |
| **`update-plugin-readme`** | Refresh the README of this plugin (or any Claude Code skills plugin) so that its "Skills" section reflects the current set of skills under `skills/*/SKILL.md` |

### Other

| Skill | What it does |
|---|---|
| **`ben-gurion-flight-board`** | Check live arrivals or departures at Ben Gurion Airport (Tel Aviv, TLV, LLBG) from the official Israel Airports Authority flight board |
| **`fiber-availability-check`** | Check whether fiber-optic internet is deployed at an Israeli street address, across multiple providers (Bezeq Bfiber and HOT Fiber today) |
| **`israel-conferences`** | Find upcoming conferences, professional events, summits, expos, or industry meetups in Israel — checks a curated whitelist of Israeli event aggregators (events.co.il, conferenceindex.org, IVC, ICX, dev.events) before falling back to general web search |
| **`jerusalem-council-meetings`** | Browse, list, or download protocols (meeting minutes) from Jerusalem Municipality council committee sittings (ישיבות ועדות מועצת העיר ירושלים) |

<!-- SKILLS:END -->

## Installation

```bash
claude plugins marketplace add danielrosehill/Claude-Code-Plugins
claude plugins install israel-agent-skills@danielrosehill
```

## License

MIT
