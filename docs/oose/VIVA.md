# IrrigaTrace Viva Voce Defense Guide (25 Questions & Answers)

**Course:** Object-Oriented Software Engineering (OOSE Lab)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Repository:** `C:\Study\OOSE\Mini Project`

---

### Q1: Why isn't the irrigation engine a black-box deep learning model?
**Answer:**
Irrigation control on real agricultural farms is safety-critical. A black-box deep learning model can produce unpredictable hallucinations, lack mathematical guarantees, and cannot be audited cleanly after the fact. In IrrigaTrace, the core agronomic engine is an immutable, purely functional expert system implementing standard FAO-56 Penman-Monteith water-balance equations. The novelty of IrrigaTrace is not in inventing an unexplainable ML model, but in the **comprehensive audit, replay, and governance lifecycle**: recording exact input snapshots, preserving immutable AI recommendations, enforcing append-only cryptographically hashed event ledgers, and enabling retrospective replay and flip analysis.

---

### Q2: What is the crucial difference between "Replay" and "Reproduce"? Why do both exist?
**Answer:**
- **Replay:** Retrieves the *exact historical state* at time $t$ from stored immutable snapshots and event streams. It answers: *"What did the system record at 10:05 AM on October 24, 2026?"* Even if code or rulesets change later, replay always returns the historical facts.
- **Reproduce:** Takes historical inputs $(I_t)$ and re-executes the *current* engine codebase $(E_{current})$ against them: $\hat{R} = E_{current}(I_t)$. It checks whether $\hat{R} == R_{historical}$.
- Both exist because code evolves (e.g., ruleset upgrades from v1.4.1 to v1.4.2). If a farm manager asks why an irrigation pump failed 3 months ago, Replay shows what was decided then, while Reproduce reveals if modern engine logic would make the same decision.

---

### Q3: How do you guarantee the original AI recommendation is never overwritten after a human supervisor modifies it?
**Answer:**
We guarantee immutability through three distinct, mutually reinforcing architectural layers:
1. **SQLite Database Triggers:** At the database engine level, an `UPDATE` trigger (`dec_core_immutable`) rejects any modification to `recommended_duration_h`, `decision_snapshots`, or `recommendations`. Any attempt raises an immediate `sqlite3.IntegrityError: original recommendation is immutable`.
2. **Domain Model Design:** In `models.py`, `HumanReview` is modeled as a distinct entity with its own `final_duration_h`, `modified_by`, and `reason_code`. The domain layer provides no mutation setters on `Recommendation`.
3. **Cryptographic Hash Chain:** The initial AI recommendation is sealed in the genesis event (`DECISION_CREATED`). Any alteration of historical records invalidates subsequent event hashes ($\text{prev\_hash} \to \text{this\_hash}$), failing audit verification.

---

### Q4: What does the SHA-256 hash chain prove, and what does it NOT prove?
**Answer:**
- **What it proves:** Tamper-evidence within the application. It mathematically proves that no row in the `decision_events` ledger was modified, inserted out of sequence, or deleted without breaking the hash link:
  $$H_i = \text{SHA-256}(D_{\text{id}} \parallel i \parallel \text{type} \parallel \text{payload} \parallel H_{i-1})$$
- **What it does NOT prove:** It does not prove external truth (i.e. whether a physical sensor was faulty in the field), nor does it prevent an adversary with root database privileges from recalculating the entire chain from scratch if they possess the private signing keys.

---

### Q5: Why is Qdrant treated as a derived vector index? What happens if Qdrant Cloud is unreachable?
**Answer:**
SQLite WAL is the single source of truth for all transactional decisions, snapshots, and audit events. Qdrant is strictly an auxiliary derived index used for natural-language semantic search.
Under Invariant 8 (Offline-first & graceful degradation), if Qdrant Cloud or the network times out (as observed on IPv4 restrictions), the `SimilaritySearchService` gracefully degrades to a deterministic SQL nearest-neighbor query based on Euclidean distance across normalized numerical inputs (soil moisture, temperature, rain probability). The UI continues to function seamlessly with a subtle provenance badge (`source: "sql-fallback"`).

---

### Q6: How do you prevent the local LLM (Ollama / Qwen) from hallucinating or inventing numbers in decision summaries?
**Answer:**
We implement the `NumberConsistencyValidator` (`services/narration.py`). The LLM never makes decisions; it only produces English, Hindi, or Kannada narrations from a structured context dictionary.
Before any narration is displayed or saved:
1. The validator extracts all numbers, floats, and percentages from the generated text via regular expressions.
2. It verifies that every extracted number matches an authoritative domain field in the frozen snapshot (e.g. soil moisture 18.2%, recommended duration 2.8 h, rain probability 15%).
3. If the LLM invents or hallucinates any ungrounded figure, the validator rejects the output, and the system automatically falls back to an authoritative deterministic template (`TemplateNarrationStrategy`).

---

### Q7: What is "Flip Analysis", and what are its agronomic and computational limits?
**Answer:**
- **Definition:** When comparing two decisions ($A$ and $B$) with different actions (e.g., $A$ = "Wait", $B$ = "Irrigate"), flip analysis performs single-variable sensitivity testing. For each changed input $k$, it creates a synthetic input vector keeping all features of $A$ except feature $k$ (taken from $B$), runs the engine, and checks if that single change is sufficient to flip the recommendation.
- **Limits:** It assumes single-variable independence. It does not account for multi-variable non-linear interactions (e.g., high heat combined simultaneously with high wind speed) unless higher-order combinations are explicitly evaluated.

---

### Q8: Which object-oriented design patterns are implemented in IrrigaTrace?
**Answer:**
1. **Strategy Pattern:** `NarrationStrategy` protocol with concrete strategies (`OllamaNarrationStrategy`, `GeminiNarrationStrategy`, `TemplateNarrationStrategy`).
2. **Repository Pattern:** `DecisionRepository` and `PlotRepository` abstracting SQLite queries and transactional persistence.
3. **Value Object Pattern:** `SensorReading`, `WeatherSnapshot`, `Recommendation` (immutable data carriers without independent lifecycle).
4. **State Pattern:** Decision lifecycle states (`COLLECTED` $\to$ `RECOMMENDED` $\to$ `RECORDED` $\to$ `REVIEWED` $\to$ `FINALIZED`).
5. **Observer / Event Stream Pattern:** SSE (`/decisions/{id}/stream`) emitting timeline events to frontend subscribers.
6. **Facade Pattern:** `DecisionRecorder` providing a unified atomic interface over engine calculation, snapshot freezing, and hash-chain genesis.

---

### Q9: Why was the Incremental / Agile process model chosen over the Waterfall model?
**Answer:**
IrrigaTrace was built across 4 prioritized tiers (P0 Core Domain, P1 Traceability & Replay, P2 Intelligence & Compare, P3 Hardening & Polish).
Agile / Incremental development allowed verifying core mathematical invariants and SQLite append-only triggers in Phase 1 before layering on asynchronous local LLM narration and frontend UI components in subsequent increments. Waterfall would have deferred end-to-end integration testing to the end, risking late discovery of trigger constraints or schema mismatches.

---

### Q10: How do software requirements (SRS) trace to test cases (STD)?
**Answer:**
Every Functional Requirement (FR) maps directly to one or more automated test cases in `api/tests`:
- **FR-01 (Engine calculation):** Tested by `test_engine.py` (FAO-56 threshold calculations across crop stages).
- **FR-02 (Snapshot immutability):** Tested by `test_triggers_and_invariants.py::test_update_recommendation_fails_trigger`.
- **FR-03 (Human review preservation):** Tested by `test_lifecycle_and_integrity.py::test_supervisor_modification_lifecycle`.
- **FR-04 (Cryptographic chain verification):** Tested by `test_lifecycle_and_integrity.py::test_hash_chain_tamper_detection`.
- **FR-05 (Replay vs Reproduce):** Tested by `test_lifecycle_and_integrity.py::test_replay_vs_reproduce`.
- **FR-06 (Flip analysis):** Tested by `test_comparison_flips.py::test_flip_analysis`.

---

### Q11: What is the distinction between "Outcome Record" and "Model Correctness"? Why don't you claim causal correctness?
**Answer:**
An `OutcomeRecord` documents observational field measurements 72 hours post-irrigation (e.g., realized soil moisture, natural rainfall, visible crop stress).
IrrigaTrace strictly avoids claiming that the AI recommendation "caused" a positive or negative crop yield. Weather shifts, soil compaction, valve clogging, or unmetered rainfall also impact crop health. Claiming direct causality would be unscientific; therefore, all analytics screens display a mandatory disclaimer: *"Observations only — weather, execution, and field conditions also affect results."*

---

### Q12: How would IrrigaTrace scale to 25,000 commercial farms?
**Answer:**
1. **Database:** Migrate from SQLite WAL to distributed PostgreSQL with partitioned tables for `decision_events` (partitioned by farm tenant and date).
2. **Event Queue:** Offload LLM narration and Qdrant indexing to asynchronous Celery/Redis background task workers.
3. **Storage:** Store raw sensor telemetry streams in time-series engines (TimescaleDB / ClickHouse) while storing immutable decision snapshots in object storage (S3/GCS with Object Lock).
4. **Security:** Multi-tenant row-level security (RLS) with per-tenant cryptographic signing keys.

---

### Q13: Explain the SQLite Write-Ahead Logging (WAL) mode used in IrrigaTrace.
**Answer:**
SQLite defaults to rollback journal mode, which locks the entire database file during writes. By executing `PRAGMA journal_mode=WAL;`, IrrigaTrace enables Write-Ahead Logging. In WAL mode, readers do not block writers, and writers do not block readers. This permits concurrent background sensor ingestion while the frontend streams SSE decision events and operators submit human reviews.

---

### Q14: What is the purpose of the 4-tab layout on the Case File screen (S3)?
**Answer:**
The 4 tabs segregate concerns for distinct persona workflows:
1. **Overview:** Daily farm manager view showing AI-vs-Human split numbers, current status, and factor explanations.
2. **Replay:** Agronomist view featuring the orbit scrubber to reconstruct state at time $t$ and run reproduce checks.
3. **Audit:** Compliance and regulatory auditor view inspecting the raw append-only ledger and cryptographic chain.
4. **Outcome:** Field technician view recording actual post-irrigation measurements and observations.

---

### Q15: How does the system handle sensor latency or stale sensor data?
**Answer:**
The `SensorReading` entity includes a `timestamp` and a computed property `age_minutes`. In `IrrigationEngine.evaluate()`, if `sensor_age_minutes > 180` (3 hours), the rule engine flags a `STALE_SENSOR_DATA` advisory rule, reduces irrigation confidence, and requires explicit supervisor confirmation before pumping.

---

### Q16: Why are database triggers preferred over ORM application-level validations for immutability?
**Answer:**
Application-level validations (e.g. in Pydantic or SQLAlchemy) only execute when requests pass through that specific code path. If a developer runs a raw SQL script, migration, or debug console, application hooks are bypassed. Database triggers execute inside the SQLite storage engine itself, guaranteeing that no rogue script, ORM bug, or external connection can violate append-only invariants.

---

### Q17: What is the time complexity of the hash chain verification algorithm?
**Answer:**
For a decision with $N$ events, verification processes events sequentially from seq $1$ to $N$. Computing SHA-256 over string payloads is $O(M)$ where $M$ is payload byte length. Therefore, verifying a decision's integrity proof is strictly $O(N \cdot M)$, completing in less than 2 milliseconds for typical chains ($N \approx 5$).

---

### Q18: What role does the `ReviewService` play when an operator rejects a recommendation?
**Answer:**
When an operator chooses `REJECT`, the AI recommendation remains intact in `recommendations` and `decision_snapshots`. The `ReviewService` records a new `HumanReview` with `action: REJECT`, `final_duration_h: 0.0`, and mandatory `reason_code`. An event of type `REVIEW_REJECTED` is appended to the hash chain, and the decision status transitions to `FINALIZED`. Pumping duration is set to zero without erasing what the AI proposed.

---

### Q19: How are translations (Hindi, Kannada) handled without introducing factual distortion?
**Answer:**
`TranslationService` utilizes Gemini 2.5 Flash to translate the validated English narrative into Hindi or Kannada. Post-translation, `NumberConsistencyValidator` is re-run on the translated string to verify that all numerals (e.g., 2.8, 18.2) remain identical and uncorrupted by language tokens.

---

### Q20: Explain the purpose of the Lab Bench (`/lab`) simulator screen.
**Answer:**
The Lab Bench provides an interactive sandbox for farm supervisors and students to test "what-if" hypotheses. By manipulating soil moisture, temperature, and rain probability sliders, users observe live factor calculations via stateless API calls (`/api/engine/preview`). Clicking "Generate Decision" submits the scenario to the live database, streaming real-time SSE audit events.

---

### Q21: What are the primary reason codes supported during human review?
**Answer:**
The system enforces standardized agronomic reason codes:
- `WEATHER_UNEXPECTED`: Impending unforecasted cloud cover or local rain.
- `SOIL_SATURATION_OBSERVED`: Manual soil core inspection indicates higher moisture than sensor readout.
- `EQUIPMENT_MAINTENANCE`: Drip lines, filters, or pumps undergoing cleaning/servicing.
- `POWER_CURTAILMENT`: Rural feeder electricity outage or scheduled tariff blackout.
- `CROP_STRESS_SIGNS`: Visual signs of leaf curl or wilting requiring emergency supplemental hydration.

---

### Q22: What is the significance of the 7-minute live demo script in docs/14?
**Answer:**
The 7-minute demo script is an end-to-end evaluation scenario structured for the OOSE lab evaluation:
- **Min 0–1:** The Observatory Landing page and architectural vision.
- **Min 1–2:** Dashboard navigation and KPI monitoring.
- **Min 2–4:** Hero Case File (IRR-2026-018) displaying AI vs Human split, factors, and hash audit.
- **Min 4–5:** Time travel replay with the orbit scrubber and reproduce check.
- **Min 5–6:** Decision comparison and single-variable flip analysis.
- **Min 6–7:** Live simulation on Lab Bench, SSE event animation, and cryptographic chain verification.

---

### Q23: How does IrrigaTrace prevent CSS / design "slop"?
**Answer:**
IrrigaTrace follows the strict `design-taste-frontend` rules:
- Avoids generic Tailwind blue/purple gradients and default shadcn styles.
- Adheres to a curated, high-contrast nocturnal palette (`#06052A` void, `#14116B` indigo cards, `#C8F5C9` mint CTA).
- Uses purposeful typography pairing: Urbanist for human narrative, JetBrains Mono with tabular lining for telemetry and cryptographic hashes.
- Implements layered atmospheric depth with parallax WebP artwork rather than flat boxes.

---

### Q24: What is the purpose of the Software Project Management Plan (SPMP)?
**Answer:**
The SPMP (Experiment 2) formalizes project execution: defining the Work Breakdown Structure (WBS) across Tracks A–E, scheduling milestones via Mermaid Gantt diagrams, estimating development effort using COCOMO-basic and Function Point analysis, and managing risks via an explicit Risk Register with mitigation strategies.

---

### Q25: How does IrrigaTrace align with ABET / NBA course outcomes for OOSE?
**Answer:**
- **CO1 (Process & Agile):** Incremental sprint development tracked through WBS and task boards.
- **CO2 (Project Planning):** Effort estimation, Gantt scheduling, and risk analysis in SPMP.
- **CO3 (Analysis & Design):** Formal SRS with IEEE 830 structure, UML behavioral and structural models, and design patterns in SDD.
- **CO4 (Testing & Quality):** Software Test Documentation (STD) with unit, trigger, lifecycle, and API test suites achieving 100% pass rates.
