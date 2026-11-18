# 00 — Master Plan

## Goal
Ship IrrigaTrace: working, beautiful, demo-ready, with OOSE documents derivable from the code. Priority order of features (build and polish in this order; never start a lower tier while a higher tier is unfinished):

| Tier | Feature | Why |
|---|---|---|
| P0 | Decision recorder (snapshot + events + hash chain) | Core invariant |
| P0 | Rule engine v1.4.2 + deterministic explanation | Produces decisions |
| P0 | Human review (approve / modify / reject + reason) | Core workflow |
| P0 | Replay timeline + Reproduce check | Heart of the product |
| P0 | Compare ("Why did it change?") with flip analysis | Signature feature |
| P1 | Dashboard with filters, case-file page, outcome tracking | Demo surface |
| P1 | Local LLM narration (Ollama) with validator + provenance | AI element for the rubric |
| P1 | Qdrant "similar past decisions" + semantic search over reasons | Differentiator |
| P2 | Gemini: multilingual advisory (Hindi/Kannada), hero art, fallback narrator | Use-case match (LLM multilingual advisory) |
| P2 | Plot map (MapLibre, synthetic polygons), analytics page, NL query (⌘K) | Polish |
| P3 | Live sensor ingestion, satellite imagery, ML model | **Out of scope** unless everything above is done |

## Phases and parallel tracks
Run these as parallel agents in the Antigravity Agent Manager. `→` means "blocked until".

```
PHASE 0  Bootstrap (single agent, ~15 min)
  0.1 repo skeleton, git init, .gitignore, .env.example, Makefile
  0.2 START BACKGROUND DOWNLOADS: scripts/pull_models  qwen3:4b  nomic-embed-text   (do not wait)
  0.3 install taste-skill into .agent/skills, verify Stitch MCP + Gemini key + Qdrant key work (smoke tests)
  0.4 copy reference image is already in design/reference/

PHASE 1  (all parallel after Phase 0)
  Track A  Backend domain + DB + engine + events + API      (docs 02,05,06,07)
  Track B  LLM + Qdrant + Gemini services                    (docs 04,08)  → needs A's schema stub only
  Track C  Design: Stitch generation + self-approval         (docs 09,10,11)  ← NO dependency on A/B
  Track E  OOSE documents + diagrams (Mermaid/PlantUML)      (doc 13) ← draws from 02,05,07

PHASE 2
  Track D  Frontend build (Next.js)  → blocked by C approved AND A's OpenAPI schema
  Track A2 Seed data + simulator + tests                     (docs 12,14)

PHASE 3  Integration, polish, e2e, Lighthouse, demo rehearsal, docs freeze
```

## Background-task protocol (important)
- Model downloads are slow. Start them in Phase 0 and **keep working**.
- Check readiness any time with `python scripts/check_models.py`. Log: `.logs/pull-*.log`.
- Until models exist, the API's `NarrationService` returns the deterministic template and tags it `provenance.source = "template"`. When models appear, no code change should be needed.
- Qdrant/Gemini calls are also optional at runtime: every feature that uses them must have a no-network fallback and a visible "degraded" state in `/api/health`.

## Milestones & evidence
| ID | Milestone | Evidence to attach in task board |
|---|---|---|
| M1 | Engine + DB + events pass unit tests | pytest output |
| M2 | Full lifecycle via API (generate→review→finalize→outcome) | httpx test log |
| M3 | Design self-approved (all 8 screens ≥ 85/100) | `docs/design/approvals.md` + screenshots |
| M4 | Frontend wired, replay + compare working | Playwright run, screen recording |
| M5 | LLM narration + Qdrant similar-decisions live | screenshots |
| M6 | Demo script passes; docs generated | `make demo` + exported docs folder |

## Risk list
- 4B local model gives mediocre Hindi/Kannada → use Gemini for translation and label "machine-translated".
- Stitch output is HTML/Tailwind, not React → agent converts; keep tokens in one `tokens.css` so conversion is mechanical.
- Windows path/shell differences → use `scripts/*.ps1` variants; Makefile targets must also work through `uv run` / `pnpm` without bash-only features.
