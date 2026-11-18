# Experiment 1: Problem Statement and Process Model

**Course:** Object-Oriented Software Engineering (OOSE Lab)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Date:** 2026-10-23  
**Course Outcome:** CO1

---

## 1. Problem Statement
Commercial and precision agricultural enterprises increasingly adopt automated decision-support systems to optimize crop water efficiency. However, deploying algorithmic or artificial intelligence recommendations directly to irrigation valves creates severe operational and accountability dilemmas:
1. **The "Black-Box" Blame Game:** When a crop suffers water-stress or excessive saturation 72 hours after pumping, farm managers cannot reconstruct *why* the algorithm recommended a specific duration or *what* environmental inputs existed at that split second.
2. **Untracked Human Overrides:** Field supervisors frequently override automated recommendations based on local intuition. In existing systems, these overrides overwrite the original recommendation in place, destroying the audit trail and preventing retrospective algorithmic evaluation.
3. **Audit Vulnerability:** Conventional database records can be retroactively edited, deleted, or falsified in regulatory disputes without tamper evidence.
4. **LLM Hallucinations:** When generative AI is introduced for operator briefings, models invent ungrounded numerical figures and moisture values, destroying trust.

**IrrigaTrace solves this by introducing a formal audit, replay, and governance lifecycle:**
- Freezing immutable sensor and weather snapshots at decision inception.
- Preserving the original AI recommendation as permanently unalterable via database triggers.
- Structuring human reviews as first-class domain entities.
- Chaining all lifecycle events in a cryptographic SHA-256 hash ledger.
- Enabling retrospective "time-travel" replay, reproduce verification, and single-variable flip sensitivity analysis.

---

## 2. Chosen Process Model: Incremental / Agile Model

### 2.1 Justification for Incremental / Agile Development
The IrrigaTrace project selected an **Incremental Agile Lifecycle** organized across four capability tiers (P0 through P3):

| Phase / Tier | Focus | Key Deliverables | Rationale for Incremental Model |
|---|---|---|---|
| **Phase 0: Foundation** | Hardware profiling & tooling | Model downloads, Stitch tools, taste-skill, assumptions log | Verifies GPU/Ollama capabilities and environment before architectural commitments. |
| **P0: Core Domain (Track A)** | Core domain & invariants | FAO-56 pure engine, SQLite triggers, append-only ledger | Enforces mathematical and database constraints first. If triggers fail, downstream UI work is invalid. |
| **P1: Traceability & Replay (Track A/B)** | Replay & API | Timeline reconstruction, state_at(t), reproduce check, FastAPI routes | Validates that historical events can be accurately replayed and queried before building UI views. |
| **P2: Intelligence & Compare (Track B/C)** | Narration, vectors & design | Ollama narration, number validator, Qdrant/SQL similarity, Stitch screens | Layering AI services and frontend screens on a verified, stable REST API. |
| **P3: Polish & Hardening (Track D/E)** | End-to-end integration | Next.js frontend, Playwright tests, OOSE lab documentation | Final system integration, user verification, and lab demo readiness. |

### 2.2 Why Not Waterfall?
In a traditional Waterfall model:
- Schema triggers and append-only constraints would only be validated during late integration testing.
- Discrepancies between LLM narration output and domain fields would require circular redesign of the persistence layer.
- Agile sprint cadences enabled early automated testing of SQLite triggers (`test_triggers_and_invariants.py`) on day one, guaranteeing 100% architectural integrity.

---

## 3. Project Scope & Boundaries
- **In-Scope:**
  - Sugarcane microclimate plots (SG-104 to SG-125).
  - Pure functional FAO-56 irrigation recommendation engine (v1.4.2).
  - Immutable decision snapshots and SQLite WAL trigger enforcement.
  - Cryptographic SHA-256 hash chain per decision lifecycle.
  - Multi-persona role-based workflows (Supervisor, Farm Admin, Auditor).
  - Time-travel orbit scrubber and single-variable flip analysis.
  - Local Ollama LLM narration with strict regex number consistency validation.
- **Out-of-Scope:**
  - Physical hardware actuator wiring (interfacing via simulated hardware telemetry).
  - Real-time satellite imagery ingestion (relies on weather snapshot forecasts).
  - Causal crop yield claims (strictly observational outcome tracking).
