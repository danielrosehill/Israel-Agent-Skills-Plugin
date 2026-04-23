---
name: miklatim-lookup
description: Use when the user wants to find a public bomb shelter (miklat tziburi, מקלט ציבורי) near a location in Israel — by address, neighbourhood, coordinates, or current position — with address, type, capacity, accessibility, and Google Maps / Waze directions. Primary backend is the Miklat-MCP server (streamable HTTP, `https://mcp.jlmshelters.com/mcp`), which currently supports Jerusalem (198 public shelters). If the MCP server is unavailable or the user is asking about a city not yet supported, fall back to the Jerusalem Municipality's official list at `https://www.jerusalem.muni.il/en/residents/security/spaces/list/` (for Jerusalem only). Trigger phrases - "find a shelter near me", "nearest miklat", "closest bomb shelter in Jerusalem", "miklat tziburi", "shelters in [neighbourhood]", "shelter capacity", "accessible shelter near", "how do I get to the shelter", "public shelters list Jerusalem".
---

# Miklatim Lookup (Public Shelters in Israel)

Helps users find **miklatim tziburim** (public bomb shelters) with address, capacity, accessibility, and navigation links.

## Coverage

- **Jerusalem** — 198 public shelters, served by the Miklat-MCP backend. The Jerusalem Municipality maintains the authoritative list.
- **Other cities** — not yet in the Miklat-MCP dataset. If the user asks about another city, say so explicitly and direct them to Pikud HaOref (`https://www.oref.org.il/eng`) or the relevant municipality.

## Primary: Miklat-MCP server

Remote MCP server at `https://mcp.jlmshelters.com/mcp` (streamable HTTP transport). Register it with the Claude CLI if not already present:

```bash
claude mcp add miklat --transport http https://mcp.jlmshelters.com/mcp
```

Once registered, the following tools are available as `mcp__miklat__*`:

| Tool | Parameters | Use for |
|---|---|---|
| `search_shelters` | `city`, `query`, `limit?` | Free-text search across name, address, neighbourhood |
| `find_nearest_shelters` | `city`, `latitude`, `longitude`, `limit?` | Nearest-shelter search from a coordinate |
| `list_neighborhoods` | `city` | All neighbourhoods with shelter counts |
| `get_shelter_by_id` | `city`, `id` | Single shelter by feature id |
| `get_stats` | `city` | Totals, breakdown by type, capacity |
| `list_cities` | *(none)* | Which cities are supported right now |
| `get_directions_link` | `city`, `shelter_id`, `origin_latitude`, `origin_longitude`, `app?` | Google Maps / Waze nav link |
| `filter_shelters` | `city`, `shelter_type?`, `min_capacity?`, `accessible?`, `limit?` | Filter by type / capacity / accessibility |
| `list_shelters_in_neighborhood` | `city`, `neighborhood`, `limit?` | All shelters in a neighbourhood |

Always pass `city` as a lowercase slug (e.g. `jerusalem`).

### Typical answer flow

1. Clarify the city — if not specified, assume Jerusalem only if the user's context makes it obvious; otherwise ask.
2. If the user gave an address/neighbourhood, use `search_shelters` or `list_shelters_in_neighborhood`.
3. If the user gave coordinates (or "near me" with location available), use `find_nearest_shelters`.
4. For each result, include: shelter name/id, address, capacity, accessibility if relevant.
5. Offer `get_directions_link` for the top candidate(s) so the user can navigate.
6. If the user asks about shelter types or stats across the city, use `list_neighborhoods` / `get_stats`.

## Fallback: Jerusalem Municipality list

If the MCP server is unreachable and the user is asking about Jerusalem, fall back to the official municipality page:

- `https://www.jerusalem.muni.il/en/residents/security/spaces/list/` (English)
- `https://www.jerusalem.muni.il/he/residents/security/spaces/list/` (Hebrew)

The municipality page is the authoritative source; the MCP dataset is derived from it. If the two disagree, the municipality page wins — mention this to the user and include the URL.

Note: the municipality page is a JavaScript-rendered list that may require a browser fetch (Playwright headless) rather than plain `curl`. Treat it as a last-resort fallback, not a routine code path.

## Authoritative source for emergencies

In an actual emergency, users should follow Pikud HaOref (Home Front Command) instructions — `https://www.oref.org.il/eng` — and the real-time alerts app/portal. This skill helps with **preparation and planning**; it is not a real-time alert system. Pair it with the `home-front-command-guidelines` skill for behaviour guidance during an alert, and remind users that if time is critical, the nearest protected space (including the building's mamad or stairwell) takes precedence over a dedicated miklat tziburi.

## Out of scope

- Real-time alert feeds (that's Pikud HaOref's role).
- Private building mamadim — only public shelters.
- Cities other than those returned by `list_cities`.
- Arranging physical access or keys — the skill only reports the shelter metadata.
