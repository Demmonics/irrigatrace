<!--
Source Experiments: Exp 3 (IEEE 830 SRS), Mini Project SRS Specification.
Figures Included: None (Tabular specifications).
Downstream Notes: IEEE Section 2 formatting. Numbered requirements FR-01 to FR-12, NFR-01 to NFR-05. Inline citations [3], [4] used.
-->

# Chapter 2: Requirements Engineering

## 2.1 Elicitation Methodology and User Personas
The software requirements for IrrigaTrace were engineered following the IEEE Std 830-1998 [3] and ISO/IEC/IEEE Std 29148:2018 [4] standards. Requirements were elicited through continuous collaboration with sugarcane agronomists and irrigation field supervisors associated with KJS-AGR-01.

Three primary operational personas govern system access:
- **Field Supervisor Persona:** Requires a streamlined interface to inspect automated recommendations, evaluate input telemetry, and submit overrides with minimal friction while enforcing accountability.
- **Farm Administrator Persona:** Requires macro-level visibility into plot telemetry, parameter customization across sugarcane growth stages, and scenario simulation capabilities.
- **Regulatory Auditor Persona:** Requires mathematically verifiable transparency, automated tamper-detection routines, and exportable audit reports.

---

## 2.2 Functional Requirements (FR)

The functional requirements are detailed in TABLE I, categorized by unique identifiers, descriptive titles, detailed operational specifications, and development priority.

### TABLE I: FUNCTIONAL REQUIREMENTS SPECIFICATION
| Req. ID | Requirement Title | Detailed Specification | Priority |
|---|---|---|---|
| **FR-01** | Deterministic Engine Calculation | The system shall compute irrigation action (`IRRIGATE`, `WAIT`, `DEFER_RAIN`) and required duration in hours using a pure, deterministic implementation of FAO-56 Penman-Monteith water-balance equations [1]. | Mandatory (P0) |
| **FR-02** | Immutable Input Snapshot | At the exact moment an irrigation recommendation is computed, the system shall capture and freeze all ambient inputs (soil moisture, temperature, rain probability, forecast rainfall, crop stage) into an immutable `DecisionSnapshot` record. | Mandatory (P0) |
| **FR-03** | Recommendation Immutability | The underlying storage engine shall enforce an append-only trigger (`dec_core_immutable`) that aborts any SQL `UPDATE` or `DELETE` executed against original recommendation attributes (`id`, `plot_id`, `created_at`, `ruleset_version`, `recommended_action`, `recommended_duration_h`, `confidence`). | Mandatory (P0) |
| **FR-04** | Human Review Segregation | The system shall record supervisor reviews (`APPROVE`, `MODIFY`, `REJECT`) as separate, first-class `HumanReview` domain entities. If an action is modified or rejected, the system shall strictly mandate a standardized reason code and explanatory text. | Mandatory (P0) |
| **FR-05** | Append-Only Cryptographic Ledger | Every lifecycle event shall be recorded as an immutable `DecisionEvent` linked sequentially via SHA-256 cryptographic hashing, satisfying $H_i = \text{SHA-256}(D_{\text{id}} \parallel i \parallel \text{event\_type} \parallel \text{payload} \parallel H_{i-1})$. | Mandatory (P0) |
| **FR-06** | Historical State Replay | The system shall provide an API and interface to reconstruct the complete system state and timeline at any arbitrary historical timestamp $t$ along the decision lifecycle. | High (P1) |
| **FR-07** | Reproduce Verification | The system shall re-execute the current active engine logic against historical inputs stored in a snapshot, returning an automated diff report identifying ruleset or logic drift. | High (P1) |
| **FR-08** | Decision Comparison & Sensitivity Flips | The system shall support pairwise comparison between any two decisions, computing delta parameters and executing single-variable flip sensitivity analysis. | High (P2) |
| **FR-09** | Local LLM Narration & Grounding | The system shall generate operator briefings using a local LLM (`qwen2.5:3b`), and shall pass all generated text through a strict regex-based `NumberConsistencyValidator` that rejects any text containing ungrounded numerals. | High (P2) |
| **FR-10** | Multilingual Translation | The system shall translate verified operator briefings into Hindi and Kannada while preserving all technical and numerical quantities verbatim. | Medium (P2) |
| **FR-11** | Interactive Lab Bench Simulator | The system shall provide an interactive simulator allowing administrators to adjust environmental sliders and receive real-time preview telemetry via a stateless API (`POST /api/engine/preview`). | High (P2) |
| **FR-12** | Observational Outcome Tracking | The system shall enable operators to log realized field moisture and crop health 72 hours post-irrigation, accompanied by mandatory non-causal disclosures. | Medium (P1) |

---

## 2.3 Non-Functional Requirements (NFR)

The non-functional performance, security, and quality attributes are detailed in TABLE II.

### TABLE II: NON-FUNCTIONAL REQUIREMENTS SPECIFICATION
| NFR ID | Category | Specification Metric & Standard | Verification Method |
|---|---|---|---|
| **NFR-01** | Performance & Latency | Stateless engine calculation latency shall not exceed $50\text{ ms}$; SQLite query latency shall not exceed $10\text{ ms}$ under Write-Ahead Logging (WAL) mode. | Automated benchmarking via test suite. |
| **NFR-02** | Tamper Resistance | Zero unauthorized modifications shall be permitted on stored decision snapshots or audit events; violations must raise immediate database-level aborts. | SQLite trigger unit testing (`test_triggers_and_invariants.py`). |
| **NFR-03** | Reliability & Graceful Degradation | If external cloud services (Qdrant Cloud, Gemini API) experience network timeouts, the system shall seamlessly degrade to local deterministic SQL similarity search without service interruption. | Automated network timeout simulation test. |
| **NFR-04** | Cryptographic Verifiability | 100% of decision lifecycles must produce an unbroken, mathematically verifiable SHA-256 chain proof verifiable via independent cryptographic tools. | Automated hash verification tests (`test_lifecycle_and_integrity.py`). |
| **NFR-05** | Accessibility & Contrast | The user interface shall comply with WCAG 2.1 AA standards, maintaining a minimum $7:1$ contrast ratio for secondary telemetry text and responsiveness across 390px to 1440px viewports. | Manual visual inspection and CSS design-token audit. |

---

## 2.4 Constraints and Assumptions

### 2.4.1 Technical and Architectural Constraints
1. **Zero Domain Framework Dependencies:** The core agronomic domain layer (`api/irrigatrace/domain`) must remain pure Python, free from any third-party framework, I/O, or database imports.
2. **Local Inference Feasibility:** To accommodate rural server deployments with intermittent Internet connectivity, generative briefings must be deliverable locally using quantized 3-billion-parameter LLMs.
3. **Database Write-Ahead Logging:** SQLite must operate with `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON` to ensure concurrency across simultaneous ingestion and review transactions.

### 2.4.2 Operational Assumptions
1. Telemetry readings arriving from capacitance moisture probes are pre-calibrated for volumetric water content (VWC) within the range of $0.0\%$ to $100.0\%$.
2. Weather forecasts provide reliable 48-hour rainfall probability and cumulative precipitation estimates.
3. Field supervisors possess fundamental digital literacy to interact with touch-screen tablet interfaces in English, Hindi, or Kannada.

---

## 2.5 Traceability Matrix: Requirements to Design and Test Modules

TABLE III defines the bidirectional traceability matrix mapping each functional requirement to its corresponding Use Case, structural domain class, and verifying automated test suite.

### TABLE III: REQUIREMENTS TRACEABILITY MATRIX
| Req. ID | Target Use Case | Primary Domain Class / Module | Verifying Test Function | Test File |
|---|---|---|---|---|
| **FR-01** | UC-02 | `IrrigationEngine` | `test_worked_example_1_irrigate`<br>`test_worked_example_2_defer_rain`<br>`test_wait_when_moisture_sufficient` | `test_engine.py` |
| **FR-02** | UC-03 | `DecisionSnapshot` | `test_tc08_generate_decision_atomic` | `test_lifecycle_and_integrity.py` |
| **FR-03** | UC-03 | `irrigation_decisions` (SQL Triggers) | `test_tc14_decision_core_immutable`<br>`test_tc13_snapshots_immutable` | `test_triggers_and_invariants.py` |
| **FR-04** | UC-04 | `HumanReview`, `ReviewService` | `test_tc09_approve_lifecycle`<br>`test_tc10_and_tc11_modify_lifecycle`<br>`test_tc12_reject_lifecycle` | `test_lifecycle_and_integrity.py` |
| **FR-05** | UC-09 | `DecisionEvent`, `IntegrityService` | `test_tc08_generate_decision_atomic`<br>`test_tc15_tamper_detection` | `test_lifecycle_and_integrity.py` |
| **FR-06** | UC-05 | `DecisionReplayService` | `test_tc27_replay_state_at` | `test_lifecycle_and_integrity.py` |
| **FR-07** | UC-06 | `DecisionReplayService` | `test_tc18_reproduce_check`<br>`test_case_file_and_reproduce` | `test_lifecycle_and_integrity.py`<br>`test_api_endpoints.py` |
| **FR-08** | UC-07 | `DecisionComparison`, `ComparisonService` | `test_tc20_and_tc21_comparison_flip_analysis`<br>`test_compare_and_audit` | `test_comparison_flips.py`<br>`test_api_endpoints.py` |
| **FR-09** | UC-11 | `NumberConsistencyValidator` | `test_tc22_number_consistency_validator_pass`<br>`test_tc22_number_consistency_validator_injected_number`<br>`test_tc22_number_consistency_validator_action_contradiction` | `test_validator.py` |
| **FR-10** | UC-11 | `NarrationService` | `test_case_file_and_reproduce` | `test_api_endpoints.py` |
| **FR-11** | UC-08 | `FastAPI Router (/lab)` | `test_api_plots_and_preview` | `test_api_endpoints.py` |
| **FR-12** | UC-10 | `OutcomeRecord` | `test_api_plots_and_preview` | `test_api_endpoints.py` |
| **NFR-01** | All | `FastAPI Router`, `SqliteDecisionRepository` | `test_api_health_endpoint` | `test_api_endpoints.py` |
| **NFR-02** | UC-03, 09 | SQLite Triggers (`triggers.sql`) | `test_tc13_events_immutable`<br>`test_tc13_reviews_immutable` | `test_triggers_and_invariants.py` |
| **NFR-03** | UC-07 | `SimilaritySearchService` | `test_tc24_similar_decisions_fallback` | `test_api_endpoints.py` |
| **NFR-04** | UC-09 | `IntegrityService` | `test_tc15_tamper_detection` | `test_lifecycle_and_integrity.py` |
| **NFR-05** | All | Next.js Frontend Tokens | Manual Review & CSS Token Audit | Design System Verification |

---

*Summary:* This chapter formalized the functional requirements, non-functional constraints, and bidirectional traceability matrix for IrrigaTrace. The subsequent chapter outlines the project management, estimation, and scheduling methodologies.
