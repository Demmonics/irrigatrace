<!--
Source Experiments: Exp 2 (SPMP), Exp 4 (PM Tools & Agile Backlog).
Figures Included: None (Tabular & equation representations).
Downstream Notes: IEEE Section 3 formatting. Equations numbered (1) to (6). Inline citations [2], [9], [10] used.
-->

# Chapter 3: Software Project Management Plan

## 3.1 Agile Process Model and Lifecycle Methodology
The development of IrrigaTrace followed an **Incremental Agile Lifecycle** compliant with IEEE Std 1058-1998 [2]. In mission-critical software systems where algorithmic models interface with immutable database triggers, traditional Waterfall methodologies introduce catastrophic integration risks: database schema invariants and trigger constraints would only be validated in late lifecycle phases.

The project lifecycle was partitioned into five concurrent, synchronized work tracks:
- **Track A (Backend Core & Persistence):** Pure functional FAO-56 domain engine, SQLite WAL schema, database triggers, repository implementations, and FastAPI routes.
- **Track B (Intelligence & AI Services):** Ollama LLM integration, regex `NumberConsistencyValidator`, Google Gemini multilingual translations, and Qdrant/SQL similarity indexing.
- **Track C (Design System & Stitch Pipeline):** Design tokens, Nocturne Canopy Observatory aesthetic styling, screen generation (S1 to S8), and accessibility audits.
- **Track D (Frontend Web Application):** Next.js 14 App Router implementation, floating pill navigation, orbit timeline scrubber, and interactive Lab Bench simulator.
- **Track E (Quality Assurance & Compliance):** Automated pytest execution, cryptographic tamper-detection testing, and software documentation.

---

## 3.2 Work Breakdown Structure (WBS)
The hierarchical decomposition of project deliverables is structured across four primary phases:

### TABLE IV: WORK BREAKDOWN STRUCTURE
| Phase / Task ID | Task Description | Deliverables | Assigned Track |
|---|---|---|---|
| **1.0 Foundation** | Hardware profiling, Ollama setup, and environment verification. | Model download verification, Stitch tooling, assumptions register. | Phase 0 |
| **2.0 Core Architecture** | Implement domain models, pure FAO-56 engine, and SQLite triggers. | `models.py`, `engine.py`, `schema.sql`, `triggers.sql`, `test_engine.py`. | Track A |
| **3.0 Orchestration & Replay** | Services implementation: Recorder, Review, Replay, Compare, Integrity. | `recorder.py`, `review.py`, `replay.py`, `integrity.py`, hash-chain proof. | Track A / B |
| **4.0 Intelligence & Evaluation** | Local LLM operator briefing and regex consistency validator. | `narration.py`, `validator.py`, 20/20 LLM evaluation suite. | Track B |
| **5.0 Frontend & UI Observatory** | Next.js screens (S1–S8), split-number components, orbit scrubber. | `app/(screens)`, `components/ui`, responsive layout tokens. | Track C / D |
| **6.0 Verification & Lab Defense** | End-to-end integration tests, STD register, and viva defense guide. | 24 automated tests passing, final IEEE documentation, viva guide. | Track E |

---

## 3.3 Project Schedule and Sprint Cadence
The development timeline was executed across intensive sprint iterations, tracking milestones from initial environment configuration to final testing and report delivery.

### TABLE V: PROJECT SPRINT CADENCE & MILESTONES
| Sprint / Period | Start Date | End Date | Primary Focus | Milestone Output |
|---|---|---|---|---|
| **Sprint 0** | 2026-10-20 | 2026-10-20 | Environment & Tooling | Ollama `qwen2.5:3b` pulled; Python 3.13 / Node 20 verified. |
| **Sprint 1** | 2026-10-21 | 2026-10-21 | Domain & Storage Engine | Pure engine passing worked examples; SQLite triggers rejecting updates. |
| **Sprint 2** | 2026-10-22 | 2026-10-22 | Services & Cryptography | SHA-256 hash ledger functional; FastAPI endpoints responding. |
| **Sprint 3** | 2026-10-22 | 2026-10-23 | AI Grounding & UI Scaffolding | `NumberConsistencyValidator` passing; Stitch UI screens generated. |
| **Sprint 4** | 2026-10-23 | 2026-10-23 | End-to-End Testing & OOSE Docs | 24 pytest tests passing in 30.27s; IEEE report suite completed. |

---

## 3.4 Software Effort and Cost Estimation

### 3.4.1 Function Point (FP) Analysis
Software sizing was performed using the International Function Point Users Group (IFPUG) Counting Practices Manual Release 4.3.1 standards [10].

#### 1. Unadjusted Function Points (UFP)
The system components are classified across five function types:
- **External Inputs (EI):** 8 inputs (Sensor telemetry ingestion, human review submission, outcome recording, scenario slider inputs, farm plot registration, ruleset modification, decision comparison query, reproduce check trigger). Average complexity weight = 4.
  $$\text{EI Points} = 8 \times 4 = 32$$
- **External Outputs (EO):** 6 outputs (Recommendation generation, hash-chain proof verification, flip sensitivity matrix, SSE event stream, reproduce diff report, audit ledger export). High complexity weight = 6.
  $$\text{EO Points} = 6 \times 6 = 36$$
- **External Inquiries (EQ):** 5 inquiries (Case file lookup, plot telemetry query, KPI aggregate metrics, similar past decisions query, system health query). Low complexity weight = 3.
  $$\text{EQ Points} = 5 \times 3 = 15$$
- **Internal Logical Files (ILF):** 5 files (`farm_plots`, `decision_snapshots`, `human_reviews`, `decision_events`, `outcome_records`). Average complexity weight = 10.
  $$\text{ILF Points} = 5 \times 10 = 50$$
- **External Interface Files (EIF):** 3 external interfaces (Ollama local API, Google Gemini API, Qdrant Cloud API). Average complexity weight = 7.
  $$\text{EIF Points} = 3 \times 7 = 21$$

Summing the components yields the Unadjusted Function Points (UFP):
$$\text{UFP} = \sum (\text{EI} + \text{EO} + \text{EQ} + \text{ILF} + \text{EIF}) = 32 + 36 + 15 + 50 + 21 = 154\text{ FP} \tag{1}$$

#### 2. Value Adjustment Factor (VAF) and Adjusted Function Points (AFP)
The Value Adjustment Factor evaluates 14 General System Characteristics (GSCs) on a scale of 0 to 5. With $\sum c_i = 35$ across data communications, performance, and security:
$$\text{VAF} = 0.65 + \left(0.01 \times \sum_{i=1}^{14} c_i\right) = 0.65 + (0.01 \times 35) = 1.00 \tag{2}$$

The Adjusted Function Points (AFP) are computed as:
$$\text{AFP} = \text{UFP} \times \text{VAF} = 154 \times 1.00 = 154\text{ FP} \tag{3}$$

---

### 3.4.2 COCOMO-Basic Effort and Schedule Estimation
Using industry-standard empirical conversion ratios [9], 1 Function Point corresponds to approximately 50 Source Lines of Code (SLOC) in modern Python and TypeScript:
$$\text{Size} = 154 \times 50 = 7,700\text{ SLOC} = 7.7\text{ KLOC}$$

Under the **Organic Mode** of Boehm’s Constructive Cost Model (COCOMO) [9], nominal effort $E$ in person-months (PM) is formulated as:
$$E = a \times (\text{KLOC})^b \tag{4}$$
Where $a = 2.4$ and $b = 1.05$. Evaluating for $7.7\text{ KLOC}$:
$$E = 2.4 \times (7.7)^{1.05} = 2.4 \times 8.5273 \approx 20.47\text{ Person-Months}$$

The development schedule $T_{\text{dev}}$ in nominal calendar months is formulated as:
$$T_{\text{dev}} = c \times (E)^d \tag{5}$$
Where $c = 2.5$ and $d = 0.38$. Evaluating for $E = 20.47$:
$$T_{\text{dev}} = 2.5 \times (20.47)^{0.38} = 2.5 \times 3.1493 \approx 7.87\text{ Months}$$

The average staffing level $N$ is calculated as:
$$N = \frac{E}{T_{\text{dev}}} = \frac{20.47\text{ PM}}{7.87\text{ Months}} \approx 2.60 \approx 3\text{ Engineers} \tag{6}$$

*(Note: In modern automated agentic engineering environments with unified typing and rapid prototyping tooling, this theoretical effort was compressed into accelerated sprint increments while maintaining 100% formal verification).*

---

## 3.5 Risk Management and Mitigation Register
Risk management was conducted proactively following SEI Continuous Risk Management paradigms.

### TABLE VI: RISK MANAGEMENT REGISTER
| Risk ID | Identified Risk Event | Probability | Impact | Severity Score | Proactive Mitigation Strategy |
|---|---|---|---|---|---|
| **R-01** | Local Ollama LLM hallucinating ungrounded numerical values. | Medium (0.5) | Critical (0.9) | **High (0.45)** | Enforce strict regex validation via `NumberConsistencyValidator`; automatic fallback to template-based narration on validation failure. |
| **R-02** | External Qdrant Cloud connectivity timeout due to local IPv4/IPv6 routing. | High (0.7) | Moderate (0.5) | **High (0.35)** | Invariant 8 implementation: seamless, non-blocking fallback to deterministic SQLite nearest-neighbor computation. |
| **R-03** | Unauthorized mutation of historical irrigation recommendations. | Low (0.1) | Catastrophic (1.0) | **Critical (0.10)** | Enforce database-level SQLite trigger `dec_core_immutable` combined with sequential SHA-256 event chaining. |
| **R-04** | SQLite concurrency contention under concurrent telemetry ingest. | Low (0.2) | Moderate (0.5) | **Low (0.10)** | Enforce Write-Ahead Logging (`PRAGMA journal_mode=WAL`) and short-lived scoped database connection pooling. |
| **R-05** | Front-end UI aesthetic degradation and inconsistent responsive layout. | Medium (0.4) | Moderate (0.6) | **Medium (0.24)** | Enforce `design-taste-frontend` tokens and execute a strict 100-point UI self-review rubric across desktop and mobile viewports. |

---

## 3.6 Team Organization and Roles
The project responsibilities were allocated across five specialized engineering roles:
1. **Product Manager & Agronomic Lead:** Defines FAO-56 business rules, sugarcane stage thresholds, and user persona stories.
2. **Backend & Database Engineer:** Implements SQLite triggers, WAL connection pooling, domain models, and FastAPI routes.
3. **AI & Evaluation Engineer:** Configures local Ollama models, prompt engineering, Gemini translations, and validation test harnesses.
4. **Frontend & UI/UX Engineer:** Restyles components, implements orbit scrubber, responsive layouts, and parallax artwork.
5. **Quality Assurance & Compliance Lead:** Maintains traceability matrix, executes Pytest suites, and runs verification audits.

---

*Summary:* This chapter formulated the software project management plan, including work breakdown, sprint scheduling, function point counting, COCOMO estimation, and risk management. The following chapter provides the behavioral and structural object-oriented analysis models.
