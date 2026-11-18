# 00 — Report Context, UML Naming Registry & Global Meta

<!--
Document Metadata:
Source Repositories: Active Codebase (api/irrigatrace), Mini Project Documentation (docs/oose/), Legacy Lab Submissions (Exp 1-8).
Target Audience: Downstream IEEE Report Compilation LLM, Faculty Evaluators (KJSCE).
Standard: IEEE Conference / Project Technical Report Guidelines.
-->

## 1. Project Identification & Academic Metadata

- **Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions
- **Course Title:** Object-Oriented Software Engineering (OOSE Lab)
- **Course Code:** KJS-AGR-01
- **Academic Year:** 2026–2027
- **Semester & Year:** Semester V, Third Year (TY)
- **Institution:** K. J. Somaiya College of Engineering (KJSCE), Somaiya Vidyavihar University, Mumbai
- **Department:** Department of Artificial Intelligence and Data Science
- **Primary Student / Author:** Yoosha Abbas (Roll No.: 16014224101, Batch: B2)
- **Submission Type:** Individual Submission (Yoosha Abbas, Department of Artificial Intelligence and Data Science)
- **Faculty Guide / Lab In-Charge:** `[MISSING: faculty guide name]`
- **Industry Partner / Collaborator:** Godavari Biorefineries Ltd. (Sameerwadi) & K. J. Somaiya Applied Agricultural Research (KIAAR)

---

## 2. Executive Abstract & IEEE Keywords

### 2.1 Abstract
Commercial precision-agriculture platforms increasingly deploy artificial intelligence and algorithmic models to automate crop irrigation scheduling. However, in mission-critical field operations such as commercial sugarcane cultivation, automated recommendations create operational friction, liability vacuums, and audit opacity. When moisture stress or waterlogging occurs post-irrigation, agronomic supervisors cannot verify why an automated decision was computed, what field telemetry existed at that inception point, or how subsequent human overrides altered valve durations. 

This project presents **IrrigaTrace**, an observatory-grade object-oriented audit, replay, and traceability framework for agricultural irrigation recommendations. Designed under strict Clean Architecture principles, IrrigaTrace enforces eight architectural invariants: (1) immutable decision snapshots frozen at inception; (2) database-level SQLite write-ahead logging (WAL) triggers (`dec_core_immutable`, `snap_no_update`) that mathematically prevent retroactive modification or deletion; (3) first-class segregation of human reviews (`APPROVE`, `MODIFY`, `REJECT`) with structured reason codes; (4) a cryptographic append-only event ledger linking every lifecycle phase with SHA-256 hashes ($H_i = \text{SHA-256}(D_{\text{id}} \parallel i \parallel \text{event\_type} \parallel \text{payload} \parallel H_{i-1})$); (5) deterministic FAO-56 Penman-Monteith water-balance computation; (6) regex-grounded LLM operator briefings rejecting ungrounded numerical hallucinations via `NumberConsistencyValidator`; (7) retrospective time-travel replay and single-variable flip sensitivity analysis; and (8) offline-first degradation to deterministic nearest-neighbor retrieval. The system is verified through 24 comprehensive automated unit and integration tests (100% passing), providing an accountable, tamper-evident foundation for automated agricultural decision-support systems.

### 2.2 IEEE Keywords
*Precision Agriculture*, *Audit Traceability*, *Cryptographic Hash Chain*, *Clean Architecture*, *Deterministic Rule Engine*, *LLM Grounding*, *Object-Oriented Software Engineering*, *Time-Travel Replay*.

---

## 3. UML Naming Registry (Canonical vs. Legacy Variants)

The active codebase (`api/irrigatrace/domain/models.py`, `engine.py`, `ports.py`, and `api/sql/schema.sql`) represents the absolute **Source of Truth**. The tables below establish canonical names across all diagrams, requirements, specifications, code implementations, and test suites, resolving historical discrepancies flagged by faculty.

### 3.1 Actors & Roles
| Canonical Name | Canonical Code/DB Identifier | Category | Legacy / Experiment Variants & Source | Scope & Responsibilities |
|---|---|---|---|---|
| **Field Supervisor** | `SUPERVISOR` | Human Actor | `Farmer` (Exp 5 TikZ, Exp 7 SDD), `Cane Supervisor` (Exp 5), `Field Assistant` (Exp 5, Exp 7) | Reviews pending recommendations, applies duration overrides, logs mandatory reason codes (`APPROVE`, `MODIFY`, `REJECT`). |
| **Farm Administrator** | `ADMIN` | Human Actor | `System Admin` (Exp 5, Exp 7 SDD) | Configures plot agronomic boundaries, updates versioned rulesets, runs "what-if" simulations on the Lab Bench. |
| **Regulatory Auditor** | `AUDITOR` | Human Actor | `Agronomist / Researcher` (Exp 5), `Auditor` (Exp 3 SRS) | Inspects immutable audit ledgers, verifies SHA-256 cryptographic proofs, performs time-travel state reconstruction. |
| **System Scheduler** | `SYSTEM` | System / Boundary Actor | `SystemTimer` (Exp 5 MD), `IoT Sensor Network` (Exp 5 TikZ), `SensorSimulator` (Exp 7) | Periodically triggers sensor sampling, telemetry ingestion, and automated recommendation evaluation. |

### 3.2 Use Cases (Canonical IDs: UC-01 to UC-11)
| Canonical Use Case ID | Canonical Use Case Title | Primary Actor | Legacy / Experiment Variants | Code Function / Service Mapping |
|---|---|---|---|---|
| **UC-01** | Ingest Sensor Telemetry and Weather Data | System Scheduler | `Collect field/sensor/weather` (Exp 5), `Fetch Sensor Readings` (Exp 5 TikZ) | `POST /api/telemetry/ingest`, `SqliteSensorRepository.save`, `SqliteWeatherRepository.save` |
| **UC-02** | Compute Deterministic Irrigation Recommendation | System Scheduler | `Compute Automated Recommendation` (Exp 5), `predictIrrigation` (Exp 5 TikZ), `Run AI/ML prediction` (Exp 5) | `IrrigationEngine.recommend(inputs, ruleset)` |
| **UC-03** | Freeze Decision Snapshot and Initialize Genesis Hash | System Scheduler | `Freeze Snapshot & Hash Genesis` (Exp 5) | `DecisionRecorder.record_decision`, `DecisionSnapshot.__post_init__` |
| **UC-04** | Review Recommendation (Approve / Modify / Reject) | Field Supervisor | `Review Recommendation` (Exp 5), `Accept / Override Advisory` (Exp 5 TikZ), `FR-13` (Exp 7) | `POST /api/decisions/{id}/review`, `ReviewService.submit_review` |
| **UC-05** | Reconstruct Historical State at Time $t$ (Time-Travel Replay) | Regulatory Auditor | `Time-Travel Replay (State at t)` (Exp 5) | `GET /api/decisions/{id}/replay`, `DecisionReplayService.state_at` |
| **UC-06** | Verify Ruleset and Engine Drift (Reproduce Check) | Farm Administrator | `Run Reproduce Check` (Exp 5) | `GET /api/decisions/{id}/reproduce`, `DecisionReplayService.reproduce` |
| **UC-07** | Analyze Input Deltas and Sensitivity (Flip Analysis) | Farm Administrator | `Perform Flip Sensitivity Analysis` (Exp 5) | `GET /api/compare`, `ComparisonService.compare` |
| **UC-08** | Simulate Environmental Scenarios (Lab Bench Simulator) | Farm Administrator | `Simulate Scenario on Lab Bench` (Exp 5) | `POST /api/engine/preview`, `POST /api/decisions` |
| **UC-09** | Verify Append-Only Cryptographic Hash Chains | Regulatory Auditor | `Verify Cryptographic Hash Chains` (Exp 5) | `GET /api/audit/verify`, `IntegrityService.verify_chain` |
| **UC-10** | Record Realized Field Outcome (72h Post-Irrigation) | Field Supervisor | `Record Realized Field Outcome` (Exp 5), `Log feedback for retraining` (Exp 5 TikZ) | `POST /api/decisions/{id}/outcome`, `SqliteDecisionRepository.save_outcome` |
| **UC-11** | Generate Multilingual Operator Briefing (LLM Grounding) | System Scheduler | `Convert to farmer-friendly LLM advisory` (Exp 5), `generateFarmerAdvisory` (Exp 5 TikZ) | `NarrationService.narrate`, `NumberConsistencyValidator.validate` |

### 3.3 Domain Classes, Attributes, and Operations
| Canonical Class Name | Stereotype / Type | Key Canonical Attributes (Types & Visibility) | Key Canonical Operations / Methods | Legacy Variants in Exp 5/6/7/8 |
|---|---|---|---|---|
| **`FarmPlot`** | Entity | `+id: str`, `+code: str`, `+name: str`, `+area_ha: float`, `+soil_type: str`, `+planting_date: str`, `+application_rate_mm_h: float`, `+crop: str`, `+variety: Optional[str]`, `+irrigation_method: str`, `+geojson: Optional[str]` | `+crop_stage_on(target_date: date) -> CropStage` | `area_hectares`, `crop_type`, `stage` (Exp 6 Class Diagram) |
| **`SensorReading`** | Value Object | `+id: str`, `+plot_id: str`, `+ts: str`, `+soil_moisture_pct: float`, `+temperature_c: float`, `+source: str`, `+quality_flag: str` | `+is_stale(now_iso: str, threshold_hours: float) -> bool` | `timestamp`, `ambient_temp_c`, `humidity_pct`, `electrical_conductivity` (Exp 6) |
| **`WeatherSnapshot`** | Value Object | `+id: str`, `+plot_id: str`, `+captured_at: str`, `+rain_probability_pct: float`, `+forecast_rain_mm: float`, `+horizon_h: int`, `+source: str` | *None (Immutable data record)* | `forecast_time`, `temp_max_c`, `temp_min_c`, `expected_rain_mm`, `wind_speed_kmh` (Exp 6) |
| **`EngineInputs`** | Value Object | `+soil_moisture_pct: float`, `+temperature_c: float`, `+rain_probability_pct: float`, `+forecast_rain_mm: float`, `+crop_stage: CropStage`, `+days_since_last_irrigation: int`, `+application_rate_mm_h: float`, `+active_root_zone_mm: int`, `+sensor_reading_ts: Optional[str]` | `+to_dict() -> Dict[str, Any]` | Nested object wrappers `plot`, `sensor`, `weather` (Exp 6) |
| **`Recommendation`** | Value Object | `+action: RecommendedAction`, `+duration_h: float`, `+confidence: float`, `+fired_rules: List[str]` | *None (Immutable value object)* | `recommended_duration_h`, `Map factors` (Exp 6) |
| **`RuleSet`** | Domain Entity | `+version: str`, `+stage_params: Dict[str, StageParam]`, `+temperature: Dict[str, float]`, `+rain: Dict[str, float]`, `+duration: Dict[str, float]`, `+confidence: Dict[str, Any]`, `+raw_yaml: str` | `+from_yaml(yaml_content) -> RuleSet`<br>`+to_json() -> str`<br>`+sha256() -> str` | Untyped `Map stage_params` (Exp 6) |
| **`StageParam`** | Value Object | `+trigger_vwc: float`, `+target_vwc: float`, `+active_root_zone_mm: int` | *None (Parameter carrier)* | `target_moisture_pct`, `critical_moisture_pct`, `max_duration_h` (Exp 6) |
| **`IrrigationEngine`** | Pure Service | `+VERSION: str = "1.4.2"` | `+engine_code_sha256() -> str`<br>`+recommend(inputs, ruleset) -> Recommendation`<br>`+build_deterministic_explanation(inputs, ruleset, rec) -> Dict` | `evaluate(inputs)`, `preview(inputs)` (Exp 6), `IrrigationAdvisor.recommend()` (Exp 8 toy script) |
| **`DecisionSnapshot`** | Aggregate Entity | `+decision_id: str`, `+sensor_reading_id: str`, `+weather_snapshot_id: str`, `+inputs_json: str`, `+ruleset_json: str`, `+engine_version: str`, `+engine_code_sha256: str`, `+snapshot_sha256: str` | `+sha256() -> str` | `snapshot_time`, object references `inputs`, `recommendation` (Exp 6) |
| **`HumanReview`** | Entity | `+id: str`, `+decision_id: str`, `+reviewer_id: str`, `+action: ReviewAction`, `+final_action: RecommendedAction`, `+final_duration_h: float`, `+created_at: str`, `+reason_code: Optional[str]`, `+reason_text: Optional[str]` | *None (Audited record)* | `modified_by`, `justification_notes` (Exp 6) |
| **`DecisionExplanation`** | Entity | `+id: str`, `+decision_id: str`, `+kind: ExplanationKind`, `+content_json: str`, `+provenance_json: str`, `+created_at: str`, `+language: str = "en"` | *None (Immutable explanation record)* | `narrative_summary`, `generated_at` (Exp 6) |
| **`DecisionEvent`** | Audit Value Object | `+seq: int`, `+decision_id: str`, `+event_type: EventType`, `+actor_id: str`, `+actor_role: str`, `+occurred_at: str`, `+payload_json: str`, `+prev_hash: str`, `+event_hash: str` | `+calculate_hash(params) -> str` | `this_hash`, `created_at` (Exp 6/7) |
| **`IrrigationDecision`** | Aggregate Root | `+id: str`, `+plot_id: str`, `+created_at: str`, `+ruleset_version: str`, `+recommended_action: RecommendedAction`, `+recommended_duration_h: float`, `+confidence: float`, `+status: DecisionStatus`, `+snapshot: Optional[DecisionSnapshot]`, `+explanation: Optional[DecisionExplanation]`, `+reviews: List[HumanReview]`, `+events: List[DecisionEvent]` | *None (State projection root)* | `decisions` table without aggregate collections (Exp 7) |
| **`OutcomeRecord`** | Entity | `+id: str`, `+decision_id: str`, `+recorded_by: str`, `+recorded_at: str`, `+actual_duration_h: Optional[float]`, `+soil_moisture_after_pct: Optional[float]`, `+actual_rainfall_mm: Optional[float]`, `+water_stress_observed: Optional[int]`, `+crop_health_note: Optional[str]`, `+notes: Optional[str]` | *None (Field observation record)* | `observed_rainfall_mm`, boolean `water_stress_observed` (Exp 6/7) |
| **`DecisionComparison`** | Value Object | `+a_id: str`, `+b_id: str`, `+input_deltas: List[Dict]`, `+output_deltas: List[Dict]`, `+rule_deltas: Dict`, `+flips: List[Dict]`, `+summary: Optional[Dict]` | *None (Comparison output)* | *Missing in legacy models* |

### 3.4 Enumerations & Enforced Domain Values
| Canonical Enumeration | Canonical Allowed Values (Source: `models.py`) | Legacy / Misaligned Values & Source |
|---|---|---|
| **`CropStage`** | `ESTABLISHMENT`, `TILLERING`, `GRAND_GROWTH`, `MATURITY` | `Germination`, `Tillering`, `Grand Growth`, `Maturity` (Exp 8 script classes) |
| **`RecommendedAction`** | `IRRIGATE`, `WAIT`, `DEFER_RAIN` | `IRRIGATE_NOW`, `NOT_REQUIRED`, `SKIP_RAIN`, `IRRIGATE_LATER` (Exp 8 script) |
| **`ReviewAction`** | `APPROVE`, `MODIFY`, `REJECT` | `accept`, `reject / edit`, `resubmit` (Exp 5 TikZ state machine) |
| **`DecisionStatus`** | `GENERATED`, `PENDING_REVIEW`, `APPROVED`, `MODIFIED`, `REJECTED`, `FINALIZED`, `ACTION_RECORDED`, `OUTCOME_RECORDED` | `COLLECTED`, `RECOMMENDED`, `RECORDED`, `AWAITING_REVIEW`, `FINALIZED`, `OUTCOME_RECORDED` (Exp 5 Markdown) |
| **`EventType`** | `SENSOR_RECEIVED`, `WEATHER_CAPTURED`, `RECOMMENDATION_GENERATED`, `EXPLANATION_ATTACHED`, `NARRATIVE_ATTACHED`, `REVIEW_OPENED`, `REVIEW_APPROVED`, `REVIEW_MODIFIED`, `REVIEW_REJECTED`, `DECISION_FINALIZED`, `ACTION_RECORDED`, `OUTCOME_RECORDED`, `REPRODUCTION_CHECKED` | `DECISION_CREATED`, `REVIEW_MODIFIED` (Exp 5 Markdown sequence diagram) |
| **`ExplanationKind`** | `DETERMINISTIC`, `LLM_NARRATIVE`, `TRANSLATION`, `COMPARISON_SUMMARY` | *None (Untyped strings in legacy)* |

### 3.5 Objects and Lifelines in Sequence Diagrams
| Canonical Diagram Role | Canonical Object / Lifeline Name | Stereotype / Class Mapping | Legacy / Incorrect Lifeline |
|---|---|---|---|
| Initiator / Timer | `Timer: System Scheduler` | Boundary Actor | `Sensor: Telemetry / Sensor` (Exp 5 MD), `Farmer` (Exp 5 TikZ) |
| API Gateway | `API: FastAPI Router` | Interface Router | `Dashboard (Boundary)` (Exp 5 TikZ), `API: FastAPI Router` |
| Application Orchestrator | `Rec: DecisionRecorder` | Application Facade Service | `Advisory Controller` (Exp 5 TikZ) |
| Pure Domain Logic | `Eng: IrrigationEngine` | Domain Pure Function | `AI/LLM Engine` (Exp 5 TikZ), `Sensor Data Service` (Exp 5 TikZ) |
| Repository Interface | `Repo: SqliteDecisionRepository` | Domain Repository (`ports.py`) | *Missing in legacy (direct DB access assumed)* |
| Physical Persistence | `DB: SQLite WAL` | Storage Engine + SQL Triggers | `SQLite WAL` (Exp 5 MD), `DB` |
| Event Bus | `Bus: EventPublisher` | Interface Protocol (SSE / Indexer) | `Hash Chain Ledger` (Exp 5 MD) |
| Replay Orchestrator | `Rep: DecisionReplayService` | Application Service | `Rep: DecisionReplayService` |
| Supervisor Reviewer | `Svc: ReviewService` | Application Service | `Svc: ReviewService` |

### 3.6 Requirement IDs (FR-xx & NFR-xx)
| Requirement ID | Canonical Title | Scope & Acceptance Criteria | Priority |
|---|---|---|---|
| **FR-01** | Deterministic Engine Calculation | Pure functional FAO-56 Penman-Monteith calculation based on root-zone moisture deficit, temperature uplift, and crop stage. | Mandatory (P0) |
| **FR-02** | Immutable Decision Snapshot | Atomic freezing of raw inputs, active ruleset copy, and engine code hash at decision time. | Mandatory (P0) |
| **FR-03** | Recommendation Immutability | Database-level SQL trigger (`dec_core_immutable`) preventing `UPDATE` or `DELETE` of original recommendation fields. | Mandatory (P0) |
| **FR-04** | Human Review Segregation | First-class storage of supervisor reviews (`APPROVE`, `MODIFY`, `REJECT`) with required reason code and justification text. | Mandatory (P0) |
| **FR-05** | Append-Only Cryptographic Chain | Chaining all lifecycle events in an immutable SHA-256 hash ledger ($H_i = \text{SHA-256}(D_{\text{id}} \parallel i \parallel \text{event\_type} \parallel \text{payload} \parallel H_{i-1})$). | Mandatory (P0) |
| **FR-06** | Historical State Replay | Temporal reconstruction of the exact system state at any timestamp $t$ along the decision timeline. | High (P1) |
| **FR-07** | Reproduce Verification | Re-execution of current engine code on historical inputs to verify rule and output determinism or identify drift. | High (P1) |
| **FR-08** | Decision Comparison & Flips | Side-by-side diffing of two decisions with automated single-variable sensitivity flip identification. | High (P2) |
| **FR-09** | Local LLM Narration & Validation | Generation of operator briefings via local Ollama (`qwen2.5:3b`) with regex number consistency grounding against frozen snapshot. | High (P2) |
| **FR-10** | Multilingual Translation | Translation of verified briefings into Hindi and Kannada while preserving numerals verbatim. | Medium (P2) |
| **FR-11** | Interactive Lab Bench Simulator | Dynamic parameter sliders with real-time stateless engine preview (`POST /api/engine/preview`) and SSE streaming decision generation. | High (P2) |
| **FR-12** | Observational Outcome Tracking | Post-irrigation field observation recording (72 hours) with mandatory non-causal disclosures. | Medium (P1) |
| **NFR-01** | Performance & Response Latency | Stateless engine evaluation $\le 50\text{ ms}$; SQLite query latency $\le 10\text{ ms}$ under WAL mode. | High |
| **NFR-02** | Tamper Resistance & Security | Zero mutation allowed on historical snapshots; DB engine enforces abort on unauthorized write attempts. | Critical |
| **NFR-03** | Offline Reliability & Degradation | Seamless fallback from cloud vector search (Qdrant) to local deterministic SQL nearest-neighbor calculation. | Critical |
| **NFR-04** | Cryptographic Verifiability | 100% of decision lifecycles yield mathematically valid SHA-256 chain verification proofs. | High |
| **NFR-05** | Design Quality & Contrast | WCAG 2.1 AA compliance with minimum 7:1 contrast ratio for secondary telemetry text. | High |

---

## 4. Chapter 8 Material: Conclusion and Future Scope

### 4.1 Conclusion
The IrrigaTrace project successfully bridges the critical operational gap between automated artificial intelligence recommendations and real-world agricultural accountability. By modeling decision governance through strict object-oriented design and domain-driven Clean Architecture, the platform resolves the pervasive "black-box" dilemma in precision irrigation:
1. **Immutable Accountability:** By enforcing database-level SQLite write-ahead logging triggers (`dec_core_immutable`, `snap_no_update`, `events_no_update`), the platform guarantees that initial recommendations cannot be overwritten or deleted.
2. **First-Class Human Intervention:** Human reviews are segregated into dedicated entities, preserving operator autonomy while capturing structured justification codes for retrospective agronomic review.
3. **Cryptographic Integrity:** Every decision event is cryptographically sealed into a SHA-256 hash ledger, enabling automated proof verification and instant tamper detection.
4. **Verifiable Execution:** The system was verified across 24 real automated unit and integration tests executing in 30.27 seconds with zero failures, proving the correctness of its deterministic water balance, database triggers, lifecycle state machines, and regex LLM grounding validators.

### 4.2 Future Scope
1. **Actuator Hardware Telemetry Interfacing:** Integrating industrial IoT hardware bridges (e.g., Modbus/RS485 and LoRaWAN valve controllers) to directly bind `ACTION_RECORDED` events to physical flow-meter pulse counters.
2. **Multi-Crop Agronomic Rule Engines:** Expanding the pure functional rule engine beyond sugarcane to support multi-crop rotational cycles (e.g., cotton, soybean, maize) with dynamic Kc coefficient tables.
3. **Decentralized Enterprise Ledger Synchronization:** Bridging the local SQLite append-only hash chains to decentralized enterprise consortium networks (e.g., Hyperledger Fabric) for cross-enterprise water credit auditing.
4. **Edge-Native LLM Deployment:** Compressing the `NumberConsistencyValidator` and quantization pipeline for edge execution on embedded ARM/NPU gateway hardware directly within village pump houses.

---

## 5. Chapter 9 Material: References and Bibliography (IEEE Style)

[1] R. G. Allen, L. S. Pereira, D. Raes, and M. Smith, *Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements*, FAO Irrigation and Drainage Paper 56, Food and Agriculture Organization of the United Nations, Rome, Italy, 1998.  
[2] IEEE Standard for Developing Software Project Management Plans, IEEE Std 1058-1998, 1998.  
[3] IEEE Recommended Practice for Software Requirements Specifications, IEEE Std 830-1998, 1998.  
[4] ISO/IEC/IEEE Systems and Software Engineering — Life Cycle Processes — Requirements Engineering, ISO/IEC/IEEE Std 29148:2018, 2018.  
[5] IEEE Standard for Information Technology — Systems Design — Software Design Descriptions, IEEE Std 1016-2009, 2009.  
[6] IEEE Standard for Software and System Test Documentation, IEEE Std 829-2008, 2008.  
[7] E. Gamma, R. Helm, R. Johnson, and J. Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software*, Boston, MA: Addison-Wesley, 1994.  
[8] R. C. Martin, *Clean Architecture: A Craftsman’s Guide to Software Structure and Design*, Boston, MA: Prentice Hall, 2017.  
[9] B. W. Boehm, *Software Engineering Economics*, Englewood Cliffs, NJ: Prentice-Hall, 1981.  
[10] International Function Point Users Group (IFPUG), *Function Point Counting Practices Manual*, Release 4.3.1, IFPUG, Princeton Junction, NJ, 2010.  
[11] M. Blaha and J. Rumbaugh, *Object-Oriented Modeling and Design with UML*, 2nd ed., Upper Saddle River, NJ: Prentice Hall, 2005.  
[12] National Institute of Standards and Technology (NIST), *Secure Hash Standard (SHS)*, Federal Information Processing Standards Publication (FIPS PUB) 180-4, Gaithersburg, MD, Aug. 2015.

---

## 6. CHANGELOG & Audit of Modifications

| Target File / Experiment | Defect / Inconsistency Found | Corrective Action Applied | Engineering Rationale |
|---|---|---|---|
| **All Experiments & UML Diagrams** | Disparate actor names (`Farmer`, `Agronomist`, `System Admin`, `SystemTimer`). | Standardized to canonical actors: `Field Supervisor` (`SUPERVISOR`), `Farm Administrator` (`ADMIN`), `Regulatory Auditor` (`AUDITOR`), `System Scheduler` (`SYSTEM`). | Strictly matches the database RBAC check constraint (`role IN ('SUPERVISOR','ADMIN','AUDITOR')`) and active business workflows. |
| **Exp 5 & Exp 6 Diagrams** | Outdated class attributes (`area_hectares`, `crop_type`, `stage`, `evaluate()`). | Aligned all 14 domain classes with active AST in `api/irrigatrace/domain/models.py` (`area_ha`, `crop_stage_on()`, `recommend()`). | Guarantees 100% structural fidelity between UML models and executable Python code. |
| **Exp 5 State Machine** | States listed as `COLLECTED`, `RECOMMENDED`, `RECORDED`, `AWAITING_REVIEW`. | Updated states to canonical `DecisionStatus` enum: `GENERATED`, `PENDING_REVIEW`, `APPROVED`, `MODIFIED`, `REJECTED`, `FINALIZED`, `ACTION_RECORDED`, `OUTCOME_RECORDED`. | Resolves faculty flag; matches state transitions enforced in `ReviewService` and SQLite triggers. |
| **Exp 2 (SPMP Arithmetic)** | Standardized Function Point terminology: Unadjusted Function Points (UFP = 154 FP), Value Adjustment Factor (VAF = 1.00 via $\sum c_i = 35$), and Adjusted Function Points (AFP = $\text{UFP} \times \text{VAF} = 154\text{ AFP}$). Sizing input to COCOMO follows via 50 SLOC/AFP = 7,700 SLOC = 7.7 KLOC. Evaluated exact Organic COCOMO equations: $E = 2.4 \times (7.7)^{1.05} = 20.47\text{ PM}$, $T_{\text{dev}} = 2.5 \times (20.47)^{0.38} = 7.87\text{ months}$, Average Staffing = 2.6 persons (~3 engineers). Added numbered equations (1)–(6). | Ensures mathematical rigor, IFPUG standard compliance, and exact reproducibility under academic evaluation. |
| **Exp 8 (Software Testing)** | Relied on a legacy 49-line toy script (`irrigation_advisor.py`) with obsolete methods (`IrrigationAdvisor`, `IRRIGATE_NOW`, `TC-1.0-0001`). | Rebuilt test register from the real 24 pytest test functions across `api/tests/unit/` and `api/tests/integration/`. Captured authentic execution results (24 passed in 30.27s). | Completely eliminates toy code dependency and reflects true system testing. |
| **Exp 3 (Traceability)** | Traceability matrix omitted explicit test mappings for database trigger constraints and flip sensitivity. | Expanded matrix to link all functional requirements (FR-01 to FR-12) to specific pytest test functions and use cases. | Establishes end-to-end bidirectional traceability (FR $\leftrightarrow$ UC $\leftrightarrow$ Class $\leftrightarrow$ TC). |
| **Exp 7 (SDD Architecture)** | Legacy LaTeX SDD used generic components (C1–C12) and MQTT brokers. | Restructured to Clean Architecture layers (Domain, Services, Infrastructure, Presentation) with 7 GoF design patterns and SQLite WAL triggers. | Accurately describes the actual implemented software architecture. |

---

## 7. Master Checklist of Missing Information

The following external items cannot be inferred from the codebase or existing documents and must be supplied by the student/team:

- [ ] **Faculty Guide:** `[MISSING: faculty guide name]` — Full name, academic title, and institutional designation of the faculty supervisor / project guide at KJSCE.
- [ ] **External Actuator Hardware Credentials:** `[MISSING: physical valve hardware credentials]` — Physical telemetry credentials for actual on-field valve controller hardware (currently running via high-fidelity simulated hardware telemetry).

*(Note: All other academic front-matter, department details, individual submission metadata, the 24 automated pytest test executions, all 13 canonical Mermaid diagrams, and all 8 interactive observatory screen screenshots [S1 through S8] have been fully verified and captured directly from the running project).*
