# 12 — Testing (feeds the Software Test Document, CO4)

## Layers
| Layer | Tooling | Scope |
|---|---|---|
| Unit | pytest | Engine (table-driven), RuleSet hashing, stage calc, hash chain, validator, comparison/flip logic |
| Property | hypothesis | Monotonicity, bounds, determinism (see doc 07) |
| Integration | pytest + httpx + temp SQLite | Full lifecycle, permissions, triggers, transactions, projection consistency |
| Service fakes | pytest | Ollama/Qdrant/Gemini fakes; failure + fallback paths |
| E2E | Playwright | Demo path (doc 14) incl. replay scrubber & compare |
| A11y/perf | axe + Lighthouse CI | Dashboard, case file, compare: a11y ≥ 95, perf ≥ 90 |

## Test case register (use these IDs; STD copies this table)
| ID | Case | Expected |
|---|---|---|
| TC-01 | Engine worked example (21%, 33°C, 12%, Grand Growth, 14 mm/h) | IRRIGATE, 2.8 h, rules R-TRIGGER-LOW, R-HOT-UPLIFT, R-RAIN-NONE |
| TC-02 | Rain ≥ 60% | DEFER_RAIN, 0 h |
| TC-03 | Moisture ≥ trigger | WAIT, 0 h |
| TC-04 | Rain 30–59% | Duration reduced by 5% per 10 pp step; R-RAIN-PARTIAL |
| TC-05 | Duration clamps to [0.5, 6.0] | Within bounds |
| TC-06 | Crop stage from planting date boundaries (35/36, 100/101, 270/271) | Correct stage |
| TC-07 | Determinism, 1000 random inputs ×2 | Identical outputs |
| TC-08 | Generate decision writes decision+snapshot+explanation+4 events atomically | All present; chain valid |
| TC-09 | Approve → FINALIZED, final = AI | Events REVIEW_APPROVED, DECISION_FINALIZED |
| TC-10 | Modify without reason | 422; nothing persisted |
| TC-11 | Modify with reason | New review row; original recommendation unchanged (assert equality) |
| TC-12 | Reject requires reason | 422 without; 200 with |
| TC-13 | UPDATE/DELETE on events/snapshots/reviews | DB error (trigger) |
| TC-14 | UPDATE of recommended_duration_h | DB error |
| TC-15 | Tamper (triggers disabled on temp copy, edit a payload) | `verify` → invalid, correct `broken_at_seq` |
| TC-16 | Auditor POST review | 403 |
| TC-17 | Illegal transition (outcome before finalize) | 409 |
| TC-18 | Reproduce on untouched decision | match = true |
| TC-19 | Reproduce after ruleset file edited (snapshot has own copy) | still match = true |
| TC-20 | Compare 29/29°C/72% vs 21/33°C/12% | Deltas −8 pp, +4 °C, −60 pp; flip: rain alone flips; moisture alone does not |
| TC-21 | Compare with differing rulesets | Warning flag present |
| TC-22 | Narrative with injected wrong number | Validator rejects → template fallback, `validated:false` logged |
| TC-23 | Ollama down | Case file loads; template narrative; health = degraded |
| TC-24 | Qdrant down | `/similar` uses SQL fallback, labeled |
| TC-25 | Translation number mismatch | Rejected |
| TC-26 | Reindex idempotent | Point count unchanged on second run |
| TC-27 | Replay state_at(t) before review | Shows no review; later events flagged as not yet happened |
| TC-28 | Outcome saved | Linked to decision; caveat text rendered in UI |
| TC-29 | Playwright demo path | All steps pass, no console errors |
| TC-30 | Reduced-motion | No parallax/looping animation |

## Commands
`make test` (unit+property+integration), `make e2e`, `make a11y`, `make llm-eval`. CI is optional; locally every command must be green before declaring done.
