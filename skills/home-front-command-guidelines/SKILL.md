---
name: home-front-command-guidelines
description: Use when the user asks about Israeli civilian emergency / shelter / protection guidelines issued by Pikud HaOref (Home Front Command, פיקוד העורף) — e.g. what to do during a rocket or missile alert, how long they have to reach a protected space (mamad / miklat), what to do in a vehicle, on the road, or outdoors during a siren, hazardous-materials events, terrorist infiltration, hostile aerial vehicle (drone) infiltration, how to prepare a home protected space, emergency equipment lists, family emergency planning, and official alert channels. Answers from a bundled English-language snapshot (22 files, ~31K words) of the official oref.org.il/eng guidelines and always cites the upstream source URL per answer. Trigger phrases - "what do I do during an air raid", "how long to get to a shelter", "rocket siren guidelines", "mamad requirements", "home front command advice", "pikud haoref guidelines", "shelter time in my area", "what to do if siren goes off in car", "hazardous materials instructions", "oref guidelines", "prepare emergency kit Israel".
---

# Home Front Command Guidelines (Pikud HaOref)

Answers civilian emergency-preparedness and shelter-protocol questions from a local snapshot of the official Home Front Command (פיקוד העורף, Pikud HaOref) guidelines.

## Sources

- **Primary (bundled)**: `data/guidelines/` — 22 English-language Markdown files extracted from `https://www.oref.org.il/eng`. The snapshot's extraction date is recorded in `data/guidelines/manifest.json` under `extraction_date`.
- **Authoritative live source**: `https://www.oref.org.il/eng` — always cite this as the canonical reference in answers, and direct the user there for the most current guidance.

## How to answer

1. Parse `data/guidelines/manifest.json` to index titles, categories, source URLs, and file paths.
2. Match the user's question against `title`, `categories`, and file-path topic folder (e.g. `shelter-and-home`, `security-threats`, `faq`).
3. Read the matching file(s) from `data/guidelines/` and answer from the contents verbatim where relevant.
4. Always cite the upstream `source_url` from the manifest entry alongside the answer.
5. Before answering, check `manifest.extraction_date`. If older than ~6 months, add a prominent note that guidelines may have been updated and link to `https://www.oref.org.il/eng`.

## Topic folders

| Folder | Covers |
|---|---|
| `alerts-and-communication/` | Alert channels, siren types, app/portal/TV/radio, fake-news guidance |
| `defensive-policy/` | HFC policy levels, routine during war, education and gatherings |
| `emergency-preparedness/` | Equipment lists, family plans, emergency contacts |
| `faq/` | General behavior, hazardous materials, rocket/missile, arrival time to protected space |
| `security-threats/` | Hostile aerial vehicles (drones), terrorist infiltration, threat-type overview |
| `shelter-and-home/` | Mamad requirements and maintenance, preparing home, choosing protected space |

## Answer hygiene

- Quote the guidelines rather than paraphrasing when the detail matters (e.g. exact times to reach shelter, exact equipment list items).
- Never invent numbers. If the user asks "how long do I have in Tel Aviv" and that exact answer isn't in the snapshot, say so and point to `oref.org.il/eng`.
- Include the upstream `source_url` for the file(s) you drew from.
- Do not present this skill as a substitute for emergency services. In an active emergency the user should call **100** (police), **101** (Magen David Adom / ambulance), or **102** (fire) as relevant.
