---
name: list-skills
description: Categorized map of every skill in the israel-agent-skills plugin, grouped by area (Healthcare & Medication, Emergency Preparedness, Travel & Transit, Government Services, Finance, Media, Connectivity, Meta/Tooling). Use when the user asks "what skills are in this plugin", "is there a skill for X in Israel", "which medication / shelter / municipality skill should I use", or when you (Claude) need a quick categorical map without reading every individual SKILL.md. Also lists which skills are orchestrators (chain other skills) vs. direct lookups, so you pick the right entry point.
---

# Israel-Agent-Skills — skill map

Read this first when you (or the user) need a directory of what's in the plugin. Skills are grouped by user-intent area. Within each area, **orchestrators** (skills that chain others) come first; pick those when the user's question is open-ended.

## Healthcare & Medication

For "is X available", "is X covered", "what does X cost on my health fund", "is X still licensed in Israel", "tell me about drug X".

- **`medicine-availability-check`** — orchestrator. Routes a "is drug X available to me" question to the right underlying lookup. Default entry point.
- `maccabi-medicine-lookup` — Maccabi-specific catalogue: listed?, prescription?, basket?, prior approval?, list price + per-tier copay.
- `drug-co-il-lookup` — pharma reference (Pharmacists Organization). Active ingredient, ATC, dosage form, equivalents/generics, MOH patient leaflets.
- `israel-drugs-registry-lookup` — official MOH regulatory record. Registration number (דרגיסטר), licence holder, official indication, registration status, all leaflet revisions.

Other health funds (Klalit / Meuchedet / Leumit) are not yet covered.

## Emergency Preparedness

- `home-front-command-guidelines` — Pikud HaOref guidance: rocket/missile alerts, time-to-shelter, mamad/miklat behaviour, drone/HazMat events, family planning.
- `miklatim-lookup` — find a nearby public bomb shelter by address/coords, with directions.

## Travel & Transit

- `ben-gurion-flight-board` — live TLV arrivals/departures from the Israel Airports Authority feed.
- `nsc-travel-threat` — current Israel NSC travel threat level / advisory for a given country.

## Government Services

- `kol-zchut-lookup` — Israeli rights and entitlements (consumer, employment, tenant, social).
- `jerusalem-municipality-report` — file a "106" public-contact report with עיריית ירושלים.
- `jerusalem-council-meetings` — browse / download Jerusalem council committee protocols.
- `israel-post-appointment` — check, book, or cancel a דואר ישראל branch appointment.

## Finance

- `salary-conversion` — convert between Israeli (monthly NIS) and world (annual local-currency) salary conventions.

## Media & Information

- `israel-news-rss` — latest headlines from major Israeli outlets (English or Hebrew) via RSS.
- `israel-conferences` — upcoming conferences, summits, expos, industry meetups in Israel.

## Connectivity

- `fiber-availability-check` — check whether fibre-optic internet (Bezeq Bfiber, HOT Fiber) is deployed at a given Israeli address.

## Meta / Tooling

- `add-skill-to-plugin` — add a new skill to this plugin from rough notes.
- `update-plugin-readme` — refresh this plugin's README skill section to match `skills/*/SKILL.md`.
- `discover-israel-skills` — browse / install **third-party** Israel-focused Claude Code skills authored by others.
- `install-companion-plugins` — install other Claude Code plugins that complement this one.
- `environment-check` — diagnose missing dependencies (Python module, Playwright browser, CLI tool) reported by another skill.

## How to use this map

- For an open-ended question, pick the **orchestrator** in the relevant area if one exists. It will chain underlying lookups only as far as the question requires (saving calls and noise).
- For a precise question whose source is obvious ("what's in the Maccabi catalogue for X"), call the direct skill — don't go through the orchestrator.
- If nothing here matches, suggest `discover-israel-skills` (third-party catalogue) or `add-skill-to-plugin` (build a new one).
