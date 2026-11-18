# IrrigaTrace — Antigravity build pack

Everything the agent needs to build IrrigaTrace (OOSE mini project, use case KJS-AGR-01) end to end.

## Your 6-minute setup (the only manual steps)
1. Create an empty project folder, e.g. `irrigatrace/`, and copy **everything in this pack into it** (keep the folder structure, including the hidden `.agent/` folder).
2. Put the **taste-skill** repo in `.agent/skills/taste-skill/` (clone it there). If you skip this, the agent will ask once and keep working on other tracks.
3. In Antigravity, connect the **Stitch MCP** server.
4. Create `.env` in the project root with your real keys (never paste keys into chat or into any .md):
   ```
   GEMINI_API_KEY=...
   QDRANT_URL=...
   QDRANT_API_KEY=...
   ```
5. Install **Ollama** from ollama.com/download (the agent starts the model downloads for you).
6. Open the folder in Antigravity, open the **Agent Manager**, and paste the kickoff prompt below.

## Kickoff prompt (paste into Antigravity)
```
Read AGENTS.md first, then docs/00_MASTER_PLAN.md, and follow them exactly.

Build IrrigaTrace end to end. Start with Phase 0. As part of Phase 0, check my hardware, pick the local-model tier from docs/04_LOCAL_LLM_SETUP.md, and START the model downloads in the background with scripts/pull_models (qwen3:4b and nomic-embed-text, or whatever tier fits). Do NOT wait for them: continue with other work immediately, and check readiness with scripts/check_models.py at natural breakpoints.

Then run the tracks in parallel as defined in the master plan: Track A (backend), Track B (AI services), Track C (Stitch design with self-approval per docs/11), Track E (OOSE documents). Start Track D (frontend) only after the design is self-approved and the OpenAPI schema exists.

Rules: obey the invariants in AGENTS.md section 2, read the taste-skill before any UI work, use my Gemini and Qdrant keys only through .env, log every assumption in docs/ASSUMPTIONS.md instead of stopping to ask, tick docs/15_TASK_BOARD.md with evidence as you go, and finish with make demo passing the 7-minute script in docs/14.
```

## File map
| File | Purpose |
|---|---|
| `AGENTS.md` | Master rules and invariants (read first) |
| `docs/00_MASTER_PLAN.md` | Phases, parallel tracks, background-task protocol, milestones |
| `docs/01_PRODUCT_SPEC.md` | Concept, requirements (FR/NFR), roles, non-goals |
| `docs/02_ARCHITECTURE.md` | Layers, graded class names, patterns, lifecycle, repo layout |
| `docs/03_TECH_STACK.md` | Every tech choice with rejects, env vars |
| `docs/04_LOCAL_LLM_SETUP.md` | Model choice, background download, guardrails, validator, prompts |
| `docs/05_DATA_MODEL.md` | DDL, append-only triggers, hash chain, events |
| `docs/06_API_SPEC.md` | Endpoints and response shapes |
| `docs/07_RULE_ENGINE.md` | Deterministic engine, worked example, flip analysis |
| `docs/08_QDRANT_GEMINI.md` | Vector index design, Gemini's three narrow jobs |
| `docs/09_UI_DESIGN_SYSTEM.md` | Tokens (hex), type, components, motion, anti-patterns |
| `docs/10_SCREENS.md` | Every screen's layout and copy |
| `docs/11_STITCH_AND_TASTE_WORKFLOW.md` | Self-approving design loop, rubric, prompts, art generation |
| `docs/12_TESTING.md` | 30 test cases tied to requirements |
| `docs/13_OOSE_DELIVERABLES.md` | Exp 1-9 mapping, UML list, viva prep |
| `docs/14_SEED_DATA_AND_DEMO.md` | Seed scenario, 7-minute demo script, fallback plan |
| `docs/15_TASK_BOARD.md` | Checklist per track |
| `scripts/` | Background model pull (sh + ps1), readiness check |
| `context/` | Your use-case docx and OOSE lab templates |
| `design/reference/` | The BeanMachine reference screenshot |
