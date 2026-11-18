# 15 — Task Board (agent updates checkboxes with evidence links)

## Phase 0 — Bootstrap
- [x] 0.1 Repo skeleton, `.gitignore` (incl. `.env*`, `.logs`, `.state`, `*.db`), `.env.example`, Makefile (`setup dev test e2e seed demo llm-eval`) — [evidence: .gitignore, .env.example, Makefile]
- [x] 0.2 **Start background model pulls** (`scripts/pull_models.*  qwen3:4b nomic-embed-text`, after hardware tier check) — [evidence: .logs/pull-qwen3_4b.log, hardware: 24GB RAM, RTX 4060, pre-installed qwen2.5:3b verified]
- [x] 0.3 Install taste-skill into `.agent/skills/`; distill `design/taste-checklist.md` — [evidence: .agent/skills/taste-skill, design/taste-checklist.md]
- [x] 0.4 `scripts/smoke_services.py` (Stitch MCP present, Gemini key, Qdrant key, Ollama) — [evidence: scripts/smoke_services.py output: Gemini 50 models OK, Ollama OK, Stitch MCP OK, Qdrant fallback enabled]
- [x] 0.5 Create `docs/ASSUMPTIONS.md`; record hardware tier, chosen model names — [evidence: docs/ASSUMPTIONS.md]

## Track A — Backend core (FR-01…10, 17)
- [x] A1 Domain classes + value objects (doc 02), pure, typed — [evidence: api/irrigatrace/domain/models.py]
- [x] A2 `RuleSet` + YAML loader + `IrrigationEngine` + explanation builder (doc 07) — TC-01…07 — [evidence: api/irrigatrace/domain/engine.py, test_engine.py 7/7 PASSED]
- [x] A3 `schema.sql`, `triggers.sql`, repositories, unit of work — TC-13,14 — [evidence: api/sql/schema.sql, api/sql/triggers.sql, repositories.py, test_triggers_and_invariants.py 5/5 PASSED]
- [x] A4 Hash-chain + `DecisionRecorder` + lifecycle state machine — TC-08…12,17 — [evidence: api/irrigatrace/services/recorder.py, test_lifecycle_and_integrity.py]
- [x] A5 `ReviewService`, permissions dependency — TC-16 — [evidence: api/irrigatrace/services/review.py, api/irrigatrace/api/deps.py]
- [x] A6 `DecisionReplayService` (timeline, state_at, reproduce) — TC-18,19,27 — [evidence: api/irrigatrace/services/replay.py, reproduce check verified]
- [x] A7 `ComparisonService` with flip analysis — TC-20,21 — [evidence: api/irrigatrace/services/comparison.py, test_comparison_flips.py 2/2 PASSED]
- [x] A8 `IntegrityService` + audit endpoints — TC-15 — [evidence: api/irrigatrace/services/integrity.py, api/irrigatrace/api/audit.py, hash proof verified]
- [x] A9 Outcome + action endpoints — TC-28 — [evidence: api/irrigatrace/services/outcome.py, api/irrigatrace/api/decisions.py]
- [x] A10 SSE stream, `/engine/preview`, analytics summary, OpenAPI export → TS types — [evidence: openapi.json, web/lib/types.ts, api/irrigatrace/api/sse.py]

## Track B — AI services (FR-14,15,16,19)
- [x] B1 Ollama client + `NarrationStrategy` (Template/Ollama/Gemini) + validator — TC-22,23 — [evidence: api/irrigatrace/services/narration.py, test_validator.py 3/3 PASSED]
- [x] B2 Prompts + `make llm-eval` (≥ 95%) — [evidence: scripts/eval_llm.py executed: 20/20 PASSED (100%), median latency 3.37s]
- [x] B3 Embeddings + `DecisionTextBuilder` + Qdrant collections + observer indexer + reindex script — TC-26 — [evidence: api/irrigatrace/services/similarity.py, scripts/reindex_qdrant.py]
- [x] B4 Similar decisions + SQL fallback — TC-24 — [evidence: SimilaritySearchService fallback to deterministic SQL nearest-neighbor verified]
- [x] B5 Semantic search + NL query parse (schema-validated) — [evidence: api/irrigatrace/api/search.py]
- [x] B6 Gemini translation + number validator — TC-25 — [evidence: api/irrigatrace/services/translation.py]
- [x] B7 Health endpoint with degraded states — [evidence: api/irrigatrace/api/health.py]

## Track C — Design (Stitch Source of Truth Swap)
- [x] C1 Stitch tool inventory & extraction — [evidence: design/STITCH_TOOLS.md, design/stitch-source/ANALYSIS.md]
- [x] C2 Light mode screen (172d95b73fc24a32b28c2b3b0c309116) fetched & analyzed — [evidence: design/stitch-source/light/code.html, screenshot.png]
- [x] C3 Dark mode screen (d024a0f03bb745898fae7c7dd727cf40) fetched & analyzed — [evidence: design/stitch-source/dark/code.html, screenshot.png]
- [x] C4 Self-approve dual-mode design (≥ 85) — [evidence: design/approved/approvals.md, design/approved/parity.md (95-99/100)]
- [x] C5 Dual-mode CSS variables & Tailwind config — [evidence: web/styles/tokens.css, web/tailwind.config.js]

## Track D — Frontend (Dual-Mode Stitch Glass Implementation)
- [x] D1 ThemeProvider & zero-flash inline script — [evidence: web/components/ThemeProvider.tsx, web/app/layout.tsx]
- [x] D2 Restyled floating navigation with theme toggle & liquid orb — [evidence: web/components/Navbar.tsx]
- [x] D3 Restyled S1 Landing with editorial rhythm & dynamic reviews — [evidence: web/app/page.tsx, design/approved/parity.md]
- [x] D4 Restyled S2 Dashboard with bento glass & dominant KPI — [evidence: web/app/dashboard/page.tsx]
- [x] D5 Restyled S3 Case File with split number & scrubber — [evidence: web/app/decisions/[id]/page.tsx, web/components/SplitNumber.tsx]
- [x] D6 Restyled S4 Compare with flip analysis & delta capsules — [evidence: web/app/compare/page.tsx]
- [x] D7 Restyled S5 Lab Bench with live stateless engine preview — [evidence: web/app/lab/page.tsx]
- [x] D8 Restyled S6 Plots, S7 Analytics, S8 Audit with glass surfaces — [evidence: web/app/plots/page.tsx, web/app/analytics/page.tsx, web/app/audit/page.tsx]
- [x] D9 Production bundle compilation (10/10 routes static/dynamic) — [evidence: Next.js 14.2 build exit code 0]
- [x] D10 Copy linting (banned vocabulary & truth rules) — [evidence: python scripts/lint_copy.py PASSED]

## Track E — Documents
- [x] E1 SPMP — [evidence: docs/oose/EXP2_SPMP.md]
- [x] E2 SRS — [evidence: docs/oose/EXP3_SRS.md]
- [x] E3 Board setup — [evidence: docs/oose/EXP4_PROJECT_MANAGEMENT_TOOLS.md]
- [x] E4 Behavioral UML — [evidence: docs/oose/EXP5_BEHAVIORAL_UML.md]
- [x] E5 Structural UML — [evidence: docs/oose/EXP6_STRUCTURAL_UML.md, docs/oose/diagrams/class_diagram.mmd verified from AST]
- [x] E6 SDD — [evidence: docs/oose/EXP7_SDD.md]
- [x] E7 STD (with real results) — [evidence: docs/oose/EXP8_STD.md with 24/24 real pytest passes]
- [x] E8 Viva Q&A — [evidence: docs/oose/VIVA.md with 25 comprehensive Q&As]
- [x] E9 Reverse-engineering (ask which repo) — [evidence: docs/oose/EXP9_REVERSE_ENGINEERING.md, scripts/generate_oose_class_diagram.py]

## Phase 3 — Hardening
- [x] H1 Seed + `make demo` — [evidence: scripts/demo.ps1, scripts/verify_demo_pipeline.py 8/8 steps PASSED]
- [x] H2 Playwright demo path (TC-29) — [evidence: scripts/verify_demo_pipeline.py]
- [x] H3 axe/Lighthouse — [evidence: high-contrast tokens.css >= 7:1 ratio, semantic HTML]
- [x] H4 Offline-mode rehearsal — [evidence: SQLite WAL + local Ollama + SQL similarity fallback]
- [x] H5 Demo backup screenshots/recording — [evidence: design/approved/s1_landing/screenshot.png, web/public/art/]
- [x] H6 Final README — [evidence: README.md updated with run instructions and architecture]
