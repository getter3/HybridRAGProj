---
name: SMT1 Search Skill
description: This skill should be used when the user asks about the Shin Megami Tensei (SNES) walkthrough, SMT1 routes, locations, bosses, items, demons, passwords, or other game-guide details, including requests to find or verify information in the local Hybrid RAG API.
version: 0.1.0
---

# SMT1 Walkthrough Research

Answer questions about the Super Nintendo version of *Shin Megami Tensei* using
the project's local Hybrid RAG API first. Use the bundled Markdown sources only
as a last resort: when the API cannot be reached, or when reasonable API search
and chunk expansion still provide no usable evidence.

## Required lookup order

1. **Search the API first.** Send the user's question, or a concise natural
   language query that preserves its intent, to `GET /search` with `limit=10`.
2. **Improve API coverage before falling back.** If the results are irrelevant,
   too broad, or incomplete, refine the query and search again. Raise the result
   limit only when useful, and never above `20` for this skill.
3. **Expand relevant truncated results.** When a useful result ends mid-topic,
   omits needed adjacent steps, or otherwise appears cut off, call `GET /seek`
   with that result's exact `chunk_id` and `chunk_index`. The endpoint returns
   the target chunk and its immediate neighbors. Inspect the returned chunks
   for the needed context.
4. **Use bundled originals only as the last resort.** Search the files in
   `assets/` only if the API is unreachable or API search and any useful seek
   calls still do not provide evidence sufficient to answer.
5. **Report the evidence source.** Identify the filename and, when available,
   chunk ID/index for API evidence, or filename and heading for asset evidence.
   Separate sourced facts from uncertainty; do not fill gaps with guesses.

Do not skip API search in favor of local files just because local text search
seems faster. A single weak result is a reason to refine the API query, not to
switch immediately to the assets. Do not call `/seek` for an irrelevant result
or invent chunk identifiers.

## Local API

Use the API at `http://localhost:8890`. Search directly; a health check is not
required before the first query.

For the complete, current endpoint and schema contract, consult the
[OpenAPI specification](http://localhost:8890/openapi.json). Check it whenever
an endpoint parameter or response field is unclear.

### Search

`GET /search` accepts:

- `query` — required natural-language query.
- `limit` — optional result count. Start at `10`; increase only as needed and
  cap this skill's requests at `20`.

Use URL-encoded query parameters. For example:

```bash
query='Where is the Cathedral of Shadows and how do I reach it?'
curl --fail --silent --show-error --get 'http://localhost:8890/search' \
  --data-urlencode "query=$query" \
  --data-urlencode 'limit=10'
```

Inspect the JSON `results` array. Relevant fields include `filename`,
`chunk_id`, `chunk_index`, `content`, and `metadata`. Use `content` as the
evidence; use the identifiers to request adjacent context when necessary.

### Seek adjacent context

`GET /seek` requires both positive integer parameters, `chunk_id` and
`chunk_index`. Copy both values from the same search result:

```bash
curl --fail --silent --show-error --get 'http://localhost:8890/seek' \
  --data-urlencode 'chunk_id=123' \
  --data-urlencode 'chunk_index=4'
```

The API schema does not expose a dedicated truncation flag. Decide from the
passage whether a missing beginning, abrupt ending, or absent neighboring step
could change the answer. Seek only when adjacent context is relevant. Use the
neighboring chunks to understand the passage, and cite the chunk(s) that
support the final response.

### API errors

Treat connection failures and unsuccessful HTTP responses as API unavailability
for the current question. Surface that limitation briefly, then use the
bundled originals as the fallback. Do not claim the API confirmed a fact when
it returned an error or no relevant results.

## Last-resort asset lookup

Search `assets/` only after exhausting useful API search/seek evidence, or when
the API is unavailable. Use exact game terms, alternate spellings, character
names, location names, and likely headings to find relevant passages. For
example:

```bash
rg -n -i 'Cathedral of Shadows|Shadows' \
  'skill/SMT1_search_skill/assets'
```

Read the matching section and enough surrounding text to preserve sequence and
conditions. Prefer the walkthrough parts for progression and route questions;
use the focused reference files for their subjects:

- `Shin Megami Tensei Guide and Walkthrough (SNES)_p1.md` through `_p6.md` —
  walkthrough and progression.
- `Shin Megami Tensei - Majin Guide.md` — Majin-related guidance.
- `Shin Megami Tensei Cheats, Codes, and Secrets for Super Nintendo_cheat.md` —
  cheats and secrets.
- `Shin Megami Tensei Consumable Items List (SNES).md` — consumable items.
- `Shin Megami Tensei Demon FAQ (SNES).md` — demon reference.

Keep the fallback explicit in the answer, for example: “The local search API
was unavailable, so I checked the bundled walkthrough.” Cite the asset filename
and its section heading (or matching line when no heading is available).

## Answering guidance

- Answer the specific question directly; preserve the walkthrough's order for
  route or step-by-step requests.
- Include prerequisites, choices, and caveats when the source makes them
  important.
- Prefer concise paraphrases over long excerpts.
- If API and asset evidence disagree, state the conflict and cite both sources;
  do not silently choose one.
- If neither source supports an answer, say what was searched and what remains
  uncertain instead of inventing a walkthrough detail.
