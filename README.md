# Israel-Agent-Skills

A Claude Code plugin that collects agent skills for Israel and Hebrew-specific workflows.

## Skills

### Jerusalem

- **`jerusalem-municipality-report`** — File a "106" public-contact report with the Jerusalem Municipality. Opens the official form, fills it from user data via Playwright, hands the reCAPTCHA to the user, and submits.

## Planned scope

In scope:

- **Israel news RSS adder** — append vetted Israeli news feeds to an RSS reader export
- **Israel first aid adder** — inject localised first aid / emergency reference content
- **English ↔ Hebrew translation** — bidirectional translation tuned for technical and civic language
- **Hebrew tech vocab updater** — maintain a glossary of Hebrew technical terminology
- **Google Fonts Hebrew downloader** — fetch Hebrew-supporting Google Fonts in bulk
- **Nice Hebrew fonts downloader** — curated non-Google Hebrew typeface pulls
- **Miklat lookup** — query the user's Miklat (bomb shelter) dataset

More skills will be added over time.

## Out of scope

**Israel shopping skills are NOT part of this plugin.** They are provided by the separate standalone plugin [`Claude-Israel-Shopping-Plugin`](https://github.com/danielrosehill/Claude-Israel-Shopping-Plugin). Please install that plugin for any shopping, vendor, or price-comparison workflows targeting Israeli retailers.

## Installation

```bash
claude plugins marketplace add danielrosehill/Claude-Code-Plugins
claude plugins install israel-agent-skills@danielrosehill
```

## License

MIT
