# 06 — API Spec (FastAPI, `/api`)

Auth: header `X-Demo-User: <user_id>`; server resolves role. 401 if missing, 403 if role insufficient. All mutating endpoints reject AUDITOR.
Errors: RFC 7807-style `{type,title,detail,status}`. Illegal lifecycle transition → 409.

| Method & path | Role | Purpose |
|---|---|---|
| `GET /health` | any | `{db, ollama, qdrant, gemini, models:{llm,embed}}` each `up/down/degraded` |
| `GET /users` | any | Demo users for role switcher |
| `GET /plots` · `GET /plots/{id}` | any | Plot list/detail incl. latest reading, decision history summary |
| `POST /plots` | ADMIN | Create plot |
| `POST /sensor-readings` | SUP/ADMIN | Manual reading |
| `POST /weather-snapshots` | SUP/ADMIN | Manual weather |
| `POST /simulator/step` | ADMIN | Advance simulator for a plot with scenario params (moisture drift, temp, rain) and create new reading + snapshot |
| `POST /engine/preview` | any | Stateless: inputs → engine output + factors. Writes nothing (powers Lab bench live preview) |
| `POST /decisions` | SUP/ADMIN | `{plot_id, sensor_reading_id?, weather_snapshot_id?}` → generates decision (uses latest if omitted). Returns decision + explanation |
| `GET /decisions` | any | Filters: `plot, status[], overridden, ruleset, date_from, date_to, action[], q, page, page_size` |
| `GET /decisions/{id}` | any | Case file: decision, snapshot, explanations (deterministic + narrative), reviews, outcome, integrity badge |
| `POST /decisions/{id}/review` | SUP/ADMIN | `{action, reason_code?, reason_text?, final_action?, final_duration_h?}`; validation per DDL; returns review + new status |
| `POST /decisions/{id}/action` | SUP/ADMIN | `{actual_duration_h, executed_at}` |
| `POST /decisions/{id}/outcome` | SUP/ADMIN | Outcome fields (see DDL) |
| `GET /decisions/{id}/replay` | any | Ordered timeline + per-step state view-model |
| `GET /decisions/{id}/replay/state?at=ISO` | any | State at time `t` |
| `POST /decisions/{id}/reproduce` | any | Re-run pinned engine on snapshot → `{match, recorded, reproduced, diffs}`; appends `REPRODUCTION_CHECKED` (system actor) |
| `GET /decisions/{id}/stream` | any | SSE of new events (used while generating & narrating) |
| `GET /decisions/{id}/similar` | any | Qdrant similar decisions (top 5, with payload filters) |
| `POST /decisions/{id}/translate` | SUP/ADMIN | `{language: hi|kn}` → Gemini translation of advisory text, stored as TRANSLATION explanation |
| `GET /compare?a=&b=` | any | `DecisionComparison` (+ optional LLM summary stored as COMPARISON_SUMMARY) |
| `GET /plots/{id}/previous-decision?before=` | any | Helper for default compare target |
| `GET /analytics/summary` | any | KPIs, override rate, reasons breakdown, followed vs modified, outcomes counts, series by week |
| `GET /audit/verify?decision_id=` · `GET /audit/verify-all` | any | Integrity results |
| `POST /search` | any | `{query}` → semantic search over reasons/narratives (Qdrant) |
| `POST /query/parse` | any | NL → validated filter JSON (local LLM) |
| `POST /admin/reindex` | ADMIN | Rebuild Qdrant from SQL |
| `POST /admin/seed` | ADMIN | Idempotent demo seed |

## Key response shapes (sketch — OpenAPI is the source of truth; export `openapi.json` and generate `web/lib/types.ts`)
```jsonc
// GET /decisions/{id}
{
  "id": "IRR-2026-018", "plot": {"id":"...","code":"SG-104"}, "status":"FINALIZED",
  "recommendation": {"action":"IRRIGATE","duration_h":2.8,"confidence":0.84,"ruleset_version":"rules-v1.4.2"},
  "final": {"action":"IRRIGATE","duration_h":2.0,"source":"HUMAN_MODIFIED"},
  "snapshot": {"inputs":{"soil_moisture_pct":21,"temperature_c":33,"rain_probability_pct":12,"crop_stage":"GRAND_GROWTH","days_since_last_irrigation":9},"engine_version":"1.4.2","snapshot_sha256":"..."},
  "explanation": {"deterministic":{"factors":[...],"fired_rules":["R-TRIGGER-LOW","R-RAIN-NONE"]},"narrative":{"text":"...","provenance":{...}}},
  "reviews":[{"action":"MODIFY","reviewer":"...","reason_code":"LOCAL_FIELD_CONDITIONS","reason_text":"...","final_duration_h":2.0,"created_at":"..."}],
  "outcome": null,
  "integrity": {"valid":true,"events":6}
}
// GET /compare
{ "a":"IRR-...","b":"IRR-...","input_deltas":[{"field":"soil_moisture_pct","a":29,"b":21,"delta":-8,"unit":"pp"}],
  "output_deltas":[{"field":"action","a":"WAIT","b":"IRRIGATE"}],
  "rule_deltas":{"added":["R-TRIGGER-LOW"],"removed":["R-RAIN-HIGH"]},
  "flips":[{"input":"rain_probability_pct","alone_flips_action":true,"from":"WAIT","to":"IRRIGATE"},{"input":"soil_moisture_pct","alone_flips_action":false}],
  "summary":{"text":"...","source":"template|ollama"} }
```
Backend rule: `POST /decisions/{id}/review` writes exactly one `human_reviews` row plus events in one transaction; if any step fails, nothing persists.
