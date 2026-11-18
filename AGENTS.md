# AGENTS.md — IrrigaTrace (read first, every session)

You are building **IrrigaTrace**: an object-oriented decision **audit and replay** system for an AI irrigation advisory (use case KJS-AGR-01, sugarcane). It is a college OOSE mini project that must be (a) a really good-looking, working website and (b) a clean OO design that supports UML, SRS, SDD and test documents.

**IrrigaTrace does not mainly decide when to irrigate. It records, explains, replays and compares how an irrigation decision was made.** The recommendation engine is deliberately simple and rule-based. The lifecycle around the decision is the product.

## 1. Reading order
1. `docs/00_MASTER_PLAN.md` (phases, parallel tracks, what runs in background)
2. `docs/01_PRODUCT_SPEC.md` → `02_ARCHITECTURE.md` → `03_TECH_STACK.md`
3. `docs/05_DATA_MODEL.md`, `06_API_SPEC.md`, `07_RULE_ENGINE.md`
4. `docs/04_LOCAL_LLM_SETUP.md`, `08_QDRANT_GEMINI.md`
5. `docs/09_UI_DESIGN_SYSTEM.md`, `10_SCREENS.md`, `11_STITCH_AND_TASTE_WORKFLOW.md`
6. `docs/12_TESTING.md`, `13_OOSE_DELIVERABLES.md`, `14_SEED_DATA_AND_DEMO.md`, `15_TASK_BOARD.md`

## 2. Invariants (never violate, never "simplify away")
1. **Never overwrite the AI's original recommendation.** Human decisions are *new records*; both stay queryable forever.
2. **Append-only audit.** `decision_events`, `decision_snapshots`, `human_reviews` reject UPDATE/DELETE via DB triggers AND the application layer exposes no mutation path. Events are hash-chained (see data model).
3. **Snapshot, don't recompute.** A decision stores the exact inputs, weather forecast, ruleset JSON and engine version used. Replay reads the snapshot; it never re-fetches "today's" data.
4. **Replay ≠ reproduce.** "Replay" shows the saved record. "Reproduce" re-runs the pinned engine on the saved snapshot and reports match / mismatch. Label them differently in UI and code.
5. **The LLM never decides.** Action, duration, confidence come only from the deterministic engine. LLM text is *narration* only, labeled with provenance, and checked by the number-consistency validator (`04_LOCAL_LLM_SETUP.md`). If validation fails or the model is unavailable, show the deterministic template text.
6. **No invented causality.** Comparison pages describe observed differences and engine-grounded "flip analysis" only. Outcome pages report observations; never claim the AI was right/wrong because of an outcome.
7. **Honest data labels.** All sensor/farm data is simulated. Every data-bearing screen shows a quiet "Illustrative prototype data" label. Never present figures as real farm results.
8. **Qdrant is a derived index.** SQL is the source of truth. Qdrant must be rebuildable from SQL with `scripts/reindex_qdrant.py`.
9. **Secrets** live only in `.env` / `.env.local` (git-ignored). Never print, log, commit or hard-code keys. Provide `.env.example` with empty values.

## 3. Working rules
- **Do not sit idle on downloads.** Start model downloads with `scripts/pull_models.(sh|ps1)` (backgrounded), then continue other work. Poll with `python scripts/check_models.py`. Code must degrade gracefully while models are missing.
- **Use parallel agents/tracks** as defined in the master plan. Respect the dependency graph; Track D (frontend build) must not start before the design is self-approved (doc 11).
- **Do not block on questions.** If something is ambiguous, pick the most reasonable option, log it in `docs/ASSUMPTIONS.md` (date, decision, why) and keep going. Only stop for: missing credentials, destructive actions, or anything that would violate section 2.
- **OO naming is fixed** — the domain classes in `02_ARCHITECTURE.md` are graded in UML. Use these exact names; don't rename or merge them.
- **Every task ends with evidence**: tests passing, screenshot (UI), or command output. Update `docs/15_TASK_BOARD.md` checkboxes as you go.
- Commit small, conventional commits (`feat:`, `fix:`, `docs:`, `test:`), one logical change each. Push only if the user has configured a remote.
- Keep the README runnable: `make setup`, `make dev`, `make test`, `make seed`, `make demo`.
- Type everything (mypy strict on `api/irrigatrace/domain`, TS strict on web). Lint: ruff + eslint.

## 4. UI rules (short version)
- Before writing any UI code, read the **taste-skill** `SKILL.md` and `docs/09_UI_DESIGN_SYSTEM.md`.
- Visual direction comes from `design/reference/beanmachine-reference.png` (deep indigo night, illustrated landscape, soft glow, generous space, pale-mint primary button). Taste-skill overrides on spacing, type, motion, and anti-"AI-slop" details; the reference and the design system override on palette and mood.
- Design is produced through Stitch and **self-approved** against the rubric in doc 11 before implementation.
- No emoji icons, no default shadcn look left unstyled, no lorem ipsum, no placeholder gray boxes in final.

## 5. Definition of done (whole project)
`make demo` boots API + web with seeded data; the 7-minute demo script in doc 14 runs end to end without errors; tests in doc 12 pass; integrity check shows all chains valid; Lighthouse ≥ 90 perf/a11y on dashboard; docs in doc 13 are generated.
