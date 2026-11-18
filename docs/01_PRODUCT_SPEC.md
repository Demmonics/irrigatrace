# 01 — Product Spec

## One-liner
**IrrigaTrace** — an object-oriented decision audit and replay system for AI-based irrigation advisory.

## Context (use case KJS-AGR-01)
Sugarcane irrigation advisory for farmers associated with KIAAR / Godavari Biorefineries. The advisory system recommends an action and duration from soil moisture, temperature, rain forecast, crop stage and irrigation history. IrrigaTrace wraps that system so every recommendation is traceable and reviewable. (Full text: `context/KJS-AGR-01_Use_Case_-_Dr__Shyamal.docx`.)

## The story the product must tell
> A supervisor changes 2.8 h to 2 h. Three days later the farm manager asks: why 2.8? what data? who changed it? why? what was done? what happened after?
> A normal dashboard shows the final irrigation row. IrrigaTrace preserves the whole decision history so the team can investigate instead of guessing.

## Users / roles
| Role | Can do |
|---|---|
| **Supervisor** | Generate/review decisions, approve/modify/reject with reason, record actions and outcomes |
| **Admin** | Everything a supervisor can + manage plots, run simulator, reindex Qdrant |
| **Auditor** (read-only) | Browse, replay, compare, reproduce-check, verify integrity; cannot mutate |

Demo auth: a role switcher in the top bar sets `X-Demo-User`; **the API enforces permissions server-side** (a UI-only check is a bug).

## Functional requirements (become the SRS)
| ID | Requirement | Tier |
|---|---|---|
| FR-01 | Manage plots (code, soil, crop, planting date → crop stage, application rate) | P0 |
| FR-02 | Ingest sensor readings & weather snapshots (simulated/manual) | P0 |
| FR-03 | Generate recommendation (action, duration, confidence) via rule engine | P0 |
| FR-04 | Persist immutable snapshot (inputs, weather, ruleset JSON, engine version) | P0 |
| FR-05 | Persist deterministic structured explanation (factors, thresholds, fired rules) | P0 |
| FR-06 | Human review: approve / modify / reject, reason code + text mandatory for modify/reject | P0 |
| FR-07 | Append-only, hash-chained event log per decision | P0 |
| FR-08 | Replay timeline of a decision with state-at-time scrubber | P0 |
| FR-09 | Reproduce check (re-run pinned engine on snapshot; match/mismatch) | P0 |
| FR-10 | Compare two decisions for a plot: input diff, output diff, fired-rule diff, flip analysis | P0 |
| FR-11 | Record action taken (actual duration) and outcome observations | P1 |
| FR-12 | Dashboard KPIs + filters (plot, date, status, ruleset version, overridden) | P1 |
| FR-13 | Analytics: override rate, reasons, followed vs modified, outcomes observed | P1 |
| FR-14 | Plain-English narration via local LLM, validated, with provenance | P1 |
| FR-15 | Similar-decision search & semantic search over reasons (Qdrant) | P1 |
| FR-16 | Multilingual farmer advisory (EN/HI/KN) via Gemini, labeled machine-translated | P2 |
| FR-17 | Integrity verification page (recompute hash chains, report breaks) | P1 |
| FR-18 | Plot map with synthetic polygons | P2 |
| FR-19 | Natural-language filter query (LLM → validated JSON filter → backend executes) | P2 |

## Non-functional requirements
- **NFR-01 Integrity:** no code path may mutate events/snapshots/reviews.
- **NFR-02 Determinism:** engine is a pure function: same snapshot ⇒ same output.
- **NFR-03 Performance:** dashboard < 1 s with 500 decisions; decision case file < 500 ms (excluding LLM).
- **NFR-04 Degradation:** app fully usable with Ollama, Qdrant and Gemini all offline.
- **NFR-05 Privacy:** no real farmer data; no PII to external APIs.
- **NFR-06 Accessibility:** WCAG AA contrast on the dark theme, keyboard navigable, reduced-motion respected.
- **NFR-07 Usability:** a judge understands the product within 30 seconds of landing.

## Explicit non-goals
Real sensors, satellite imagery, trained ML models, real farm data, mobile app, payments, multi-tenant auth, blockchain.

## Honesty rules (UI copy and docs)
1. Replaying the record is not reproducing the model output; show both separately.
2. Comparison text states observed differences; "flip analysis" is a literal re-run of the engine with one input swapped.
3. Outcomes are observations, not proof of AI correctness or error.
4. All data is illustrative; say so.
