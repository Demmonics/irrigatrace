# 08 — Qdrant + Gemini

Keys come from `.env` (`QDRANT_URL`, `QDRANT_API_KEY`, `GEMINI_API_KEY`). Never echo them. First task: write `scripts/smoke_services.py` that checks each service and prints only `ok/fail` + error class.

## Qdrant (derived index; SQL stays authoritative)
| Collection | Vector | Payload | Purpose |
|---|---|---|---|
| `decisions_v1` | 768-d cosine (`nomic-embed-text`) | `decision_id, plot_code, action, status, overridden, ruleset_version, created_at(ts int), reason_code, crop_stage` | "Similar past decisions" + semantic search over narratives/reasons |
| `reasons_v1` | 768-d cosine | `decision_id, review_id, reason_code, action, plot_code` | Cluster/search human override reasons ("find overrides like this") |
| `kb_v1` (P2) | 768-d cosine | `source, section` | Small agronomy/use-case notes for "What does this stage mean?" tooltips — sourced from the KJS-AGR-01 doc only; no invented agronomy |

**What gets embedded**: a canonical text per decision, e.g. `"Plot SG-104 grand growth. Soil moisture 21%, temperature 33C, rain probability 12%. Recommended irrigate 2.8 h. Final: modified to 2.0 h. Reason: local field conditions."` Build it deterministically (`DecisionTextBuilder`) so reindexing is reproducible. Point id = UUID5(decision_id).

**Indexing flow**: Observer on event publisher → on `DECISION_FINALIZED`, `REVIEW_*`, `OUTCOME_RECORDED` re-upsert that decision (idempotent). `scripts/reindex_qdrant.py` rebuilds both collections from SQL.

**Similar decisions**: embed query decision text → search top 5 with filter `plot_code` (same plot) or none → return score + the *differences* in inputs (computed from SQL, not from vectors). UI label: "Similar past decisions (semantic match — not proof of causal similarity)".

**Fallback**: if Qdrant is down, `/similar` returns a SQL-based nearest-neighbour on normalized inputs (moisture, temp, rain, stage) and labels `source: "sql-fallback"`.

**Tests** use `QdrantClient(":memory:")`.

## Ollama embeddings
`POST /api/embed` with `model: nomic-embed-text`. Batch up to 16. If embeddings are unavailable, skip indexing, set health `degraded`, retry on next event.

## Gemini (cloud) — three narrow jobs
1. **Multilingual advisory (P2)**: translate the *validated* English narrative/advisory into Hindi (`hi`) and Kannada (`kn`). Prompt: "Translate faithfully. Do not add or remove information. Keep numbers and units unchanged." Validator: same number set before/after. Store as `TRANSLATION` explanation with provenance, UI badge **"Machine-translated · not reviewed by a native speaker"**.
2. **Hero & section art (P2, build-time, not runtime)**: generate the illustrated night-landscape layers for the web app with the image model (see doc 11 for prompts). Save PNG/WebP to `web/public/art/`, record prompt + model in `design/approved/art-manifest.md`. Never generate at request time.
3. **Fallback narrator**: only if Ollama is down and `ALLOW_CLOUD_FALLBACK=true`; same prompts and validator, provenance `source: gemini`. Only the deterministic JSON (no PII) is sent.

Model names: call the Gemini list-models endpoint at setup, choose a current fast text model and a current image-generation model, write them to `.env` and `docs/ASSUMPTIONS.md`. Handle 429/5xx with exponential backoff (max 3) and fall back gracefully.

## Health endpoint semantics
`up` = working; `degraded` = failing but app fully usable via fallback; `down` = not configured. The top bar shows a tiny status dot cluster (DB · Local model · Vector · Cloud) with tooltip — quietly styled, not alarming.
