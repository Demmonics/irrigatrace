# IrrigaTrace — Night Field Observatory

> **Audit, Replay, and Traceability Framework for AI Irrigation Decisions**  
> **Course:** Object-Oriented Software Engineering (OOSE Lab, Semester 5)  
> **Project Code:** KJS-AGR-01 · Somaiya School of Engineering  
> **Aesthetic Theme:** Nocturne Canopy Observatory (Inspired by `design/reference/beanmachine-reference.png`)

---

## 1. Quick Start & Execution

### Prerequisites
- Python 3.12+ / 3.13+
- Node.js v20+ / v24+
- Ollama (running locally on `http://localhost:11434`)

### Run Commands
```bash
# 1. Run Complete Automated Test Suite (24/24 passing)
make test

# 2. Run LLM Grounding & NumberConsistencyValidator Evaluation (20/20 passing)
make llm-eval

# 3. Run the 7-Minute Evaluator Demo Script
make demo

# 4. Start Full Development Environment (FastAPI Backend + Next.js Web App)
make dev
```
- **Web Application:** `http://localhost:3000`
- **FastAPI REST API Docs:** `http://localhost:8000/docs`
- **API Health Check:** `http://localhost:8000/api/health`

---

## 2. System Architecture & Core Invariants

IrrigaTrace implements a strict object-oriented Clean Architecture governed by 8 immutable invariants:
1. **The Original Recommendation is Never Overwritten:** Human review adjustments are stored as separate first-class entities (`HumanReview`). SQLite database-level triggers (`dec_core_immutable`, `snap_no_update`) abort any `UPDATE` or `DELETE` attempt at the storage engine level.
2. **Append-Only Cryptographic Audit:** Every lifecycle event produces a SHA-256 block linked sequentially:
   $$H_i = \text{SHA-256}(D_{\text{id}} \parallel i \parallel \text{event\_type} \parallel \text{payload} \parallel H_{i-1})$$
3. **Snapshot, Don't Recompute:** Field measurements and weather forecasts are frozen into an immutable `DecisionSnapshot` at decision inception.
4. **Replay ≠ Reproduce:** Replay reconstructs historical facts at time $t$ via the orbit timeline scrubber; Reproduce re-executes current engine code against historical inputs to detect ruleset drift.
5. **The LLM Never Decides:** Pure deterministic FAO-56 Penman-Monteith logic computes water requirements. Ollama (`qwen2.5:3b`) produces plain-English narrations, verified strictly by `NumberConsistencyValidator` regex grounding before display.
6. **No Invented Causality:** Observational field outcomes are tracked 72h post-irrigation with mandatory non-causal disclosures.
7. **Single-Variable Flip Analysis:** Isolates individual input shifts (e.g. moisture drop vs. rain clearing) to prove why an automated action flipped from `WAIT` to `IRRIGATE`.
8. **Offline-First & Graceful Degradation:** If external cloud services (Qdrant Cloud, Gemini) are unreachable or blocked by local IPv4 routing, the platform seamlessly degrades to deterministic SQL nearest-neighbor search without disruption.

---

## 3. UI Screens (Nocturne Canopy Observatory)
- **S1: Observatory Landing (`/`):** Full-bleed moonlit sugarcane plateau illustration with ringed gas planet, 4 core pillars, and honest prototype statements.
- **S2: Decision Monitoring (`/dashboard`):** Dominant KPI card (125 total decisions), multi-attribute filter bar, decision table with AI-vs-Final mini-pairs, and right-rail review queue.
- **S3: Case File (`/decisions/[id]`):** 4-tab case file (Overview, Replay, Audit, Outcome), signature AI vs Human split number hero, deterministic factors, LLM briefing with Hindi/Kannada translation, and live cryptographic seal.
- **S4: Decision Diff (`/compare`):** Side-by-side comparison, lavender diff glow on delta parameters, and single-variable flip sensitivity card.
- **S5: Lab Bench Simulator (`/lab`):** Interactive environmental sliders, scenario presets, live stateless engine preview, and "Generate Real Decision" with SSE event streaming.
- **S6: Plots & Telemetry (`/plots`):** Microclimate moisture, soil type, and zone specifications across plots SG-104 to SG-125.
- **S7: Operational Analytics (`/analytics`):** Override rate trends, supervisor reason codes breakdown, and observational outcomes.
- **S8: Cryptographic Ledger (`/audit`):** Batch SHA-256 chain verification and tamper-detection proof.

---

## 4. OOSE Lab Deliverables (in `docs/oose/`)
- [EXP1: Problem Statement & Agile Process Model](file:///C:/Study/OOSE/Mini%20Project/docs/oose/EXP1_PROBLEM_AND_PROCESS.md)
- [EXP2: Software Project Management Plan (SPMP)](file:///C:/Study/OOSE/Mini%20Project/docs/oose/EXP2_SPMP.md) (WBS, Mermaid Gantt, COCOMO & FP estimation, Risk register)
- [EXP3: IEEE 830 Software Requirements Specification (SRS)](file:///C:/Study/OOSE/Mini%20Project/docs/oose/EXP3_SRS.md) (FR/NFR tables, Traceability matrix)
- [EXP4: Project Management Tools (JIRA & Trello Setup)](file:///C:/Study/OOSE/Mini%20Project/docs/oose/EXP4_PROJECT_MANAGEMENT_TOOLS.md) (CSV import format, sprint plan)
- [EXP5: Behavioral UML Modeling](file:///C:/Study/OOSE/Mini%20Project/docs/oose/EXP5_BEHAVIORAL_UML.md) (Use Case, Sequence, Activity, State Machine)
- [EXP6: Structural UML Modeling](file:///C:/Study/OOSE/Mini%20Project/docs/oose/EXP6_STRUCTURAL_UML.md) (AST-verified Class Diagram, Object Diagram for IRR-2026-018, Component, Deployment)
- [EXP7: IEEE 1016 System Design Document (SDD)](file:///C:/Study/OOSE/Mini%20Project/docs/oose/EXP7_SDD.md) (Clean Architecture, ERD, 7 Design Patterns)
- [EXP8: IEEE 829 Software Test Documentation (STD)](file:///C:/Study/OOSE/Mini%20Project/docs/oose/EXP8_STD.md) (24 automated tests passing)
- [EXP9: Reverse Engineering Methodology & Pipeline](file:///C:/Study/OOSE/Mini%20Project/docs/oose/EXP9_REVERSE_ENGINEERING.md)
- [Comprehensive 25-Question Viva Voce Defense Guide](file:///C:/Study/OOSE/Mini%20Project/docs/oose/VIVA.md)
