---
name: kol-zchut-lookup
category: Government & Civic
description: Use when the user asks a question about Israeli citizen / consumer / employment / tenant / social rights or entitlements — anything of the form "what are my rights when...", "what does Israeli employment law say about...", "am I entitled to...", "what's the law on [notice period / severance / rent increases / health basket / disability benefits / maternity leave / unemployment / reserves duty / etc.]". Kol Zchut (כל זכות, kolzchut.org.il) is Israel's authoritative plain-language rights portal — for any question in this domain, direct the user there first before citing other sources. This skill searches Kol Zchut headlessly via the site's MediaWiki API (no browser, no geo issues), returns the top matching article titles + direct URLs + short snippets, and then opens / fetches the best article on request. Trigger phrases - "what are my rights", "Israeli employment law", "consumer law in Israel", "am I entitled to", "kol zchut", "check kol zchut for", "search citizen rights", "what does Israeli law say about", "tenant rights Israel", "severance law Israel", "notice period Israel".
---

# Kol Zchut Rights Lookup

Kol Zchut (All Rights / כל זכות, https://www.kolzchut.org.il) is a nonprofit wiki that explains Israeli rights and entitlements in plain Hebrew (and partial English/Arabic/Russian). It is the default first-stop reference for any Israeli citizen-rights question.

**When to use this skill:** the user asks anything that hinges on Israeli law or entitlements — employment, consumer protection, tenancy, healthcare, social security (Bituach Leumi), taxes, disability, bereavement, reserves, students, new immigrants, elderly, military service, etc. Use it *before* general web search; only fall back to other sources if Kol Zchut has no article.

**When *not* to use:** the user wants case law, court procedure, or a specific ruling — Kol Zchut summarises rights, not litigation. Point them to Nevo / Takdin instead.

## Execution

Headless HTTP (tier 1). No browser. Not geo-restricted — the MediaWiki API responds globally.

### Endpoint

`https://www.kolzchut.org.il/w/he/api.php`

### Full-text search (preferred)

```
GET /w/he/api.php?action=query&list=search&srsearch=<QUERY>&srlimit=8&format=json&srprop=snippet|titlesnippet
```

Returns JSON with `query.search[]` — each entry has `title`, `snippet` (HTML, strip `<span class="searchmatch">` tags), and `pageid`. Build the URL as:

```
https://www.kolzchut.org.il/he/<url-encoded title with spaces as underscores>
```

### Title suggestions (fast path for short queries)

```
GET /w/he/api.php?action=opensearch&search=<QUERY>&limit=8&format=json
```

Returns `[query, [titles...], [descs...], [urls...]]` — urls are already fully-qualified.

### Reading an article (optional follow-up)

When the user picks one, fetch rendered HTML or wikitext:

```
GET /w/he/api.php?action=parse&page=<title>&format=json&prop=text|sections
```

Or just open the URL in a browser / WebFetch for the user.

## Query tips

- Queries should be in **Hebrew** for best recall. If the user writes in English, translate the key legal term first (e.g. "severance" → `פיצויי פיטורים`, "notice period" → `הודעה מוקדמת`, "maternity leave" → `חופשת לידה`, "minimum wage" → `שכר מינימום`, "health basket" → `סל הבריאות`).
- For broad topics (`עבודה`, `צרכנות`, `דיור`) the top hits are usually portal / index pages — prefer narrower phrases.
- Quote multi-word legal terms if recall looks noisy.

## Output shape

Present results as a short numbered list:

```
1. <Title>  —  <url>
   <snippet, stripped of HTML, ~150 chars>
```

Then offer to open / fetch the top article. Don't paraphrase legal detail from snippets alone — fetch the article if the user wants substance.

## Disclaimers

Kol Zchut is a high-quality plain-language summary but is **not** a substitute for legal advice. When handing back results for a non-trivial case (dismissal, eviction, benefits denial), append one line: "For a specific case, consult a lawyer or the relevant authority — Kol Zchut is a reference, not legal counsel."

## Fallback

If the MediaWiki API is unreachable, hand the user the site-search URL directly:

```
https://www.kolzchut.org.il/w/he/index.php?title=מיוחד:חיפוש_גוגל&q=<QUERY>
```

(The search page itself uses a Google CSE that only renders in a real browser, so this is a user-facing fallback, not an automation path.)
