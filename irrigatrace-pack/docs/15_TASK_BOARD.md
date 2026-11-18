# 15 — Task Board (agent updates checkboxes with evidence links)

## Phase 0 — Bootstrap
- [ ] 0.1 Repo skeleton, `.gitignore` (incl. `.env*`, `.logs`, `.state`, `*.db`), `.env.example`, Makefile (`setup dev test e2e seed demo llm-eval`)
- [ ] 0.2 **Start background model pulls** (`scripts/pull_models.*  qwen3:4b nomic-embed-text`, after hardware tier check) — then continue immediately
- [ ] 0.3 Install taste-skill into `.agent/skills/`; distill `design/taste-checklist.md`
- [ ] 0.4 `scripts/smoke_services.py` (Stitch MCP present, Gemini key, Qdrant key, Ollama) — print only ok/fail
- [ ] 0.5 Create `docs/ASSUMPTIONS.md`; record hardware tier, chosen model names

## Track A — Backend core (FR-01…10, 17)
- [ ] A1 Domain classes + value objects (doc 02), pure, typed
- [ ] A2 `RuleSet` + YAML loader + `IrrigationEngine` + explanation builder (doc 07) — TC-01…07
- [ ] A3 `schema.sql`, `triggers.sql`, repositories, unit of work — TC-13,14
- [ ] A4 Hash-chain + `DecisionRecorder` + lifecycle state machine — TC-08…12,17
- [ ] A5 `ReviewService`, permissions dependency — TC-16
- [ ] A6 `DecisionReplayService` (timeline, state_at, reproduce) — TC-18,19,27
- [ ] A7 `ComparisonService` with flip analysis — TC-20,21
- [ ] A8 `IntegrityService` + audit endpoints — TC-15
- [ ] A9 Outcome + action endpoints — TC-28
- [ ] A10 SSE stream, `/engine/preview`, analytics summary, OpenAPI export → TS types

## Track B — AI services (FR-14,15,16,19)
- [ ] B1 Ollama client + `NarrationStrategy` (Template/Ollama/Gemini) + validator — TC-22,23
- [ ] B2 Prompts + `make llm-eval` (≥ 95%)
- [ ] B3 Embeddings + `DecisionTextBuilder` + Qdrant collections + observer indexer + reindex script — TC-26
- [ ] B4 Similar decisions + SQL fallback — TC-24
- [ ] B5 Semantic search + NL query parse (schema-validated)
- [ ] B6 Gemini translation + number validator — TC-25
- [ ] B7 Health endpoint with degraded states

## Track C — Design (no code dependency)
- [ ] C1 Stitch tool inventory; reference notes
- [ ] C2 Generate + self-approve S1 landing (≥ 85)
- [ ] C3 S2 dashboard · C4 S3 case file (all tabs) · C5 S4 compare · C6 S5 lab bench
- [ ] C7 S6–S8 · C8 consistency pass → `tokens.css`
- [ ] C9 Illustration layers via Gemini image model (+ SVG fallback), `art-manifest.md`

## Track D — Frontend (after C approved + A10)
- [ ] D1 Next.js scaffold, tokens, fonts, Tailwind, restyled primitives
- [ ] D2 Layout: pill nav, role switcher, status dots, footer label
- [ ] D3 Landing with parallax layers
- [ ] D4 Dashboard + filters + queue
- [ ] D5 Case file (overview, review panel, audit, outcome)
- [ ] D6 Orbit timeline + scrubber + reproduce card
- [ ] D7 Compare page
- [ ] D8 Lab bench with SSE live timeline
- [ ] D9 Plots (+ map P2), Analytics, Audit page, ⌘K palette
- [ ] D10 States (loading/empty/error/read-only), responsive 390/768/1440, reduced-motion
- [ ] D11 Parity screenshots vs approved design; fix gaps

## Track E — Documents
- [ ] E1 SPMP · E2 SRS · E3 Board setup · E4 Behavioral UML · E5 Structural UML · E6 SDD · E7 STD (with real results) · E8 Viva Q&A · E9 Reverse-engineering (ask which repo)

## Phase 3 — Hardening
- [ ] H1 Seed + `make demo` · H2 Playwright demo path (TC-29) · H3 axe/Lighthouse · H4 Offline-mode rehearsal · H5 Demo backup screenshots/recording · H6 Final README
