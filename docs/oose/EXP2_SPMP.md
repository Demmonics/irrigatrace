# Experiment 2: Software Project Management Plan (SPMP)

**Course:** Object-Oriented Software Engineering (OOSE Lab)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Date:** 2026-10-23  
**Course Outcome:** CO2

---

## 1. Work Breakdown Structure (WBS)
The project is partitioned into five concurrent work tracks:
- **Track A (Backend Core):** Schema & triggers, pure FAO-56 engine, repositories, services (Recorder, Review, Replay, Compare, Integrity), FastAPI endpoints.
- **Track B (AI Services):** Ollama narration strategy, NumberConsistencyValidator, Gemini translation, Qdrant vector indexer with SQL fallback.
- **Track C (Design & Stitch Pipeline):** Design tokens, Stitch screen generation (S1–S8), self-review rubric (100 pts), parallax art assets.
- **Track D (Frontend Web Application):** Next.js App Router, floating pill navigation, orbit timeline with scrubber, AI-vs-Human split numbers, Lab Bench simulator.
- **Track E (OOSE Deliverables):** Academic documentation, UML behavioral/structural models, STD test registers, Viva defense guide.

---

## 2. Project Schedule (Mermaid Gantt Chart)

```mermaid
gantt
    title IrrigaTrace Development Schedule
    dateFormat  YYYY-MM-DD
    section Phase 0: Setup
    Hardware check & model pull :done, p0_1, 2026-10-20, 1d
    Tooling & smoke tests       :done, p0_2, 2026-10-20, 1d
    section Track A: Backend
    DB schema & WAL triggers    :done, a1, 2026-10-21, 1d
    Domain engine & models      :done, a2, 2026-10-21, 1d
    Services & hash chain       :done, a3, 2026-10-22, 1d
    FastAPI endpoints & tests   :done, a4, 2026-10-22, 1d
    section Track B: AI Services
    Ollama narration & validator:done, b1, 2026-10-22, 1d
    Similarity & fallback       :done, b2, 2026-10-22, 1d
    LLM evaluation (20/20)      :done, b3, 2026-10-23, 1d
    section Track C: Design
    Stitch generation & tokens  :done, c1, 2026-10-22, 1d
    Rubric self-review & art    :done, c2, 2026-10-23, 1d
    section Track D: Frontend
    Next.js scaffolding & types :active, d1, 2026-10-23, 1d
    Screens S1-S8 implementation:active, d2, 2026-10-23, 1d
    section Track E: OOSE
    Exp 1-4 Management & Req    :done, e1, 2026-10-23, 1d
    Exp 5-8 UML & Testing       :active, e2, 2026-10-23, 1d
    Exp 9 Reverse & Viva        :active, e3, 2026-10-23, 1d
```

---

## 3. Software Effort & Size Estimation

### 3.1 Function Point (FP) Analysis
Based on IFPUG Function Point counting standards:
- **External Inputs (EI):** 8 inputs (Sensor reading ingest, human review submission, outcome recording, scenario slider inputs, plot creation, ruleset update, compare query, reproduce trigger). Weight: Average (4) = 32 FP.
- **External Outputs (EO):** 6 outputs (Recommendation generation, hash-chain proof verification, flip analysis matrix, SSE event stream, reproduce diff report, PDF/JSON audit export). Weight: High (6) = 36 FP.
- **External Inquiries (EQ):** 5 inquiries (Decision case file query, plot telemetry lookup, KPI aggregate summary, similar decisions search, audit status). Weight: Low (3) = 15 FP.
- **Internal Logical Files (ILF):** 5 files (`farm_plots`, `decision_snapshots`, `human_reviews`, `decision_events`, `outcome_records`). Weight: High (10) = 50 FP.
- **External Interface Files (EIF):** 3 interfaces (Ollama local API, Gemini translation API, Qdrant Cloud API). Weight: Average (7) = 21 FP.

$$\text{Unadjusted Function Points (UFP)} = 32 + 36 + 15 + 50 + 21 = 154\text{ FP}$$
$$\text{Value Adjustment Factor (VAF)} = 0.65 + (0.01 \times 35) = 1.00$$
$$\text{Adjusted Function Points (AFP)} = 154 \times 1.00 = 154\text{ FP}$$

### 3.2 COCOMO-Basic Effort Estimation
Converting 154 FP to Python/TypeScript Lines of Code (conversion factor $\approx 50$ SLOC/FP):
$$\text{Estimated Size} = 154 \times 50 = 7,700\text{ SLOC} = 7.7\text{ KLOC}$$

Using the **Organic Mode** COCOMO formulas:
$$\text{Effort} = a \times (\text{KLOC})^b = 2.4 \times (7.7)^{1.05} \approx 2.4 \times 8.48 \approx 20.35\text{ Person-Months}$$
$$\text{Development Time} = c \times (\text{Effort})^d = 2.5 \times (20.35)^{0.38} \approx 2.5 \times 3.14 \approx 7.85\text{ Months}$$
*(Note: With automated agentic pair programming and modern Python/Next.js frameworks, this effort is compressed into intensive sprint increments).*

---

## 4. Risk Management Register

| Risk ID | Description | Likelihood | Impact | Severity | Mitigation Strategy |
|---|---|---|---|---|---|
| **R-01** | Local Ollama LLM hallucinating values | Medium | High | **Critical** | `NumberConsistencyValidator` regex grounding check; fallback to `TemplateNarrationStrategy`. |
| **R-02** | External Qdrant Cloud network timeout (IPv4) | High | Medium | **High** | Invariant 8 fallback: deterministic SQL nearest-neighbor calculation. |
| **R-03** | Unauthorized mutation of past recommendation | Low | Catastrophic | **Critical** | Database-level SQLite trigger `dec_core_immutable` + SHA-256 tamper-evident hash chain. |
| **R-04** | SQLite concurrency bottlenecks | Low | Medium | **Medium** | Enable Write-Ahead Logging (`PRAGMA journal_mode=WAL`) on all connections. |
| **R-05** | CSS styling slop / generic dashboard look | Medium | High | **High** | Enforce `design-taste-frontend` rules and strict 100-pt rubric self-review. |

---

## 5. Team Roles & Organizational Structure
- **Product Manager & Agronomic Lead:** Defines FAO-56 business rules, sugarcane stage thresholds, and user persona stories.
- **Backend & Database Engineer:** Implements SQLite triggers, WAL connection pooling, domain models, and FastAPI routes.
- **AI & Evaluation Engineer:** Configures local Ollama models, prompt engineering, Gemini translations, and validation test harnesses.
- **Frontend & UI/UX Engineer:** Restyles shadcn components, implements orbit scrubber, responsive layouts, and parallax artwork.
- **Quality Assurance & Compliance Lead:** Maintains traceability matrix, executes Pytest suites, runs Playwright E2E tests.
