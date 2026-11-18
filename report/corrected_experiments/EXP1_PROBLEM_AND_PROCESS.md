# Experiment 1: Problem Statement and Process Model (Corrected)

**Course:** Object-Oriented Software Engineering (OOSE Lab, Semester 5)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Institution:** K. J. Somaiya College of Engineering (KJSCE), Somaiya Vidyavihar University  
**Student:** Yoosha Abbas (Roll No.: 16014224101, Batch: B2)  
**Date:** 2026-10-23  
**Course Outcome:** CO1  

---

## 1. Problem Statement
Commercial precision agriculture increasingly deploys automated decision-support systems to optimize crop water efficiency. In sugarcane cultivation (*Saccharum officinarum*), water stress during vegetative phases impairs sucrose accumulation, while over-irrigation induces nutrient leaching and inflates pumping costs. However, deploying automated algorithmic recommendations directly to irrigation valves creates severe operational and accountability dilemmas:
1. **The "Black-Box" Blame Game:** When a crop suffers moisture stress or waterlogging 72 hours after pumping, farm supervisors cannot reconstruct *why* the automated algorithm recommended a specific duration or *what* environmental inputs existed at that split second.
2. **Untracked Human Overrides:** Field supervisors frequently override automated recommendations based on local intuition or power outages. In existing systems, these overrides overwrite the original recommendation in place, destroying the audit trail and preventing retrospective algorithmic evaluation.
3. **Audit Vulnerability:** Conventional database records can be retroactively edited, deleted, or falsified in regulatory disputes without tamper evidence.
4. **LLM Hallucinations:** When generative AI is introduced for operator briefings, models invent ungrounded numerical figures and moisture values, destroying trust.

**IrrigaTrace solves this by introducing a formal audit, replay, and governance lifecycle:**
- Freezing immutable sensor and weather snapshots at decision inception.
- Preserving the original AI recommendation as permanently unalterable via database triggers.
- Structuring human reviews as first-class domain entities.
- Chaining all lifecycle events in a cryptographic SHA-256 hash ledger ($H_i = \text{SHA-256}(D_{\text{id}} \parallel i \parallel \text{event\_type} \parallel \text{payload} \parallel H_{i-1})$).
- Enabling retrospective "time-travel" replay, reproduce verification, and single-variable flip sensitivity analysis.

---

## 2. Chosen Process Model: Incremental / Agile Model

### 2.1 Justification for Incremental / Agile Development
The IrrigaTrace project selected an **Incremental Agile Lifecycle** organized across five synchronized work tracks:

| Track / Phase | Focus | Key Deliverables | Rationale for Incremental Model |
|---|---|---|---|
| **Phase 0: Foundation** | Hardware profiling & tooling | Model downloads (`qwen2.5:3b`), assumptions log | Verifies GPU/Ollama capabilities and environment before architectural commitments. |
| **Track A: Backend Core** | Core domain & invariants | FAO-56 pure engine, SQLite triggers, append-only ledger | Enforces mathematical and database constraints first. If triggers fail, downstream UI work is invalid. |
| **Track B: AI Services** | Narration, vectors & grounding | Ollama narration, `NumberConsistencyValidator`, Qdrant/SQL similarity | Layers AI services and validation harnesses on top of verified REST endpoints. |
| **Track C: Design & Tokens** | Nocturne Observatory aesthetic | Design tokens, Stitch screen generation (S1–S8), rubric self-review | Enforces high aesthetic standards and WCAG 2.1 AA accessibility. |
| **Track D: Frontend Web** | Next.js 14 web application | App Router, orbit timeline scrubber, split numbers, Lab Bench | Delivers interactive operator screens connected to real backend APIs. |
| **Track E: OOSE Deliverables** | Academic compliance & verification | IEEE documentation, UML models, 24 automated tests passing | Guarantees formal verification and academic excellence. |

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
  - Multi-persona role-based workflows (Field Supervisor, Farm Administrator, Regulatory Auditor).
  - Time-travel orbit scrubber and single-variable flip sensitivity analysis.
  - Local Ollama LLM narration with strict regex number consistency validation.
- **Out-of-Scope:**
  - Physical electrical actuator hardware wiring (interfacing via simulated hardware telemetry).
  - Real-time satellite synthetic aperture radar raster processing.
  - Causal crop yield claims (strictly observational outcome tracking).
