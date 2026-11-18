# Experiment 7: System Design Document (SDD) (Corrected)

**Course:** Object-Oriented Software Engineering (OOSE Lab, Semester 5)  
**Standard:** IEEE Std 1016-2009  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Institution:** K. J. Somaiya College of Engineering (KJSCE), Somaiya Vidyavihar University  
**Student:** Yoosha Abbas (Roll No.: 16014224101, Batch: B2)  
**Date:** 2026-10-23  
**Course Outcome:** CO3  

---

## 1. Architectural Overview & Style
IrrigaTrace adheres to a **Clean Hexagonal / Layered Architecture** with strict decoupling between Domain, Service, Infrastructure, and Presentation layers:
1. **Domain Layer (`api/irrigatrace/domain`):** Pure functional agronomic entities and calculations (`IrrigationEngine`, `models.py`). Zero third-party I/O or network dependencies.
2. **Service Layer (`api/irrigatrace/services`):** Use-case orchestration (`DecisionRecorder`, `ReviewService`, `DecisionReplayService`, `IntegrityService`, `NarrationService`).
3. **Infrastructure Layer (`api/irrigatrace/infra`):** SQLite connection pool with WAL mode, append-only triggers, repository implementations, and external LLM/vector clients.
4. **Presentation Layer (`api/irrigatrace/api` & `web`):** FastAPI REST/SSE endpoints and Next.js frontend observatory interface.

---

## 2. Data Design: Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    users ||--o{ human_reviews : conducts
    users ||--o{ outcome_records : records
    farm_plots ||--o{ sensor_readings : yields
    farm_plots ||--o{ weather_snapshots : forecasts
    farm_plots ||--o{ irrigation_decisions : targets

    irrigation_decisions ||--|| decision_snapshots : freezes
    irrigation_decisions ||--o| human_reviews : reviewed_by
    irrigation_decisions ||--o{ decision_explanations : explained_by
    irrigation_decisions ||--|{ decision_events : audited_by
    irrigation_decisions ||--o| outcome_records : observes

    users {
        string id PK
        string name
        string role "SUPERVISOR | ADMIN | AUDITOR"
    }

    farm_plots {
        string id PK
        string code UK
        string name
        float area_ha
        string soil_type
        string crop "default: sugarcane"
        string variety
        string planting_date
        string irrigation_method "DRIP"
        float application_rate_mm_h
        string geojson
    }

    sensor_readings {
        string id PK
        string plot_id FK
        string ts
        float soil_moisture_pct
        float temperature_c
        string source "SIMULATED | MANUAL"
        string quality_flag "OK | SUSPECT"
    }

    weather_snapshots {
        string id PK
        string plot_id FK
        string captured_at
        float rain_probability_pct
        float forecast_rain_mm
        int horizon_h "48"
        string source "SIMULATED | MANUAL"
    }

    irrigation_decisions {
        string id PK
        string plot_id FK
        string created_at
        string ruleset_version
        string recommended_action "IRRIGATE | WAIT | DEFER_RAIN"
        float recommended_duration_h
        float confidence
        string status "GENERATED | PENDING_REVIEW | APPROVED | MODIFIED | REJECTED | FINALIZED | ACTION_RECORDED | OUTCOME_RECORDED"
    }

    decision_snapshots {
        string decision_id PK,FK
        string sensor_reading_id
        string weather_snapshot_id
        string inputs_json
        string ruleset_json
        string engine_version
        string engine_code_sha256
        string snapshot_sha256
    }

    human_reviews {
        string id PK
        string decision_id FK
        string reviewer_id FK
        string action "APPROVE | MODIFY | REJECT"
        string reason_code
        string reason_text
        string final_action "IRRIGATE | WAIT | DEFER_RAIN"
        float final_duration_h
        string created_at
    }

    decision_events {
        int seq PK
        string decision_id FK
        string event_type
        string actor_id
        string actor_role
        string occurred_at
        string payload_json
        string prev_hash
        string event_hash
    }

    decision_explanations {
        string id PK
        string decision_id FK
        string kind "DETERMINISTIC | LLM_NARRATIVE | TRANSLATION"
        string language "en | hi | kn"
        string content_json
        string provenance_json
        string created_at
    }

    outcome_records {
        string id PK
        string decision_id FK
        string recorded_by FK
        string recorded_at
        float actual_duration_h
        float soil_moisture_after_pct
        float actual_rainfall_mm
        int water_stress_observed "0 or 1"
        string crop_health_note
        string notes
    }
```

---

## 3. Detailed Design Patterns & Class References

| Design Pattern | Purpose in IrrigaTrace | Active Class References in Code |
|---|---|---|
| **Strategy Pattern** | Pluggable LLM narration generation with automatic template fallback. | `NarrationStrategy`, `OllamaNarrationStrategy`, `GeminiNarrationStrategy`, `TemplateNarrationStrategy`. |
| **Repository Pattern** | Persistence abstraction isolating domain logic from SQLite SQL syntax. | `PlotRepository`, `SensorRepository`, `DecisionRepository` protocols implemented by `SqliteDecisionRepository`, etc. |
| **State Pattern** | Decision lifecycle state management and illegal transition prevention. | `DecisionStatus` enumeration and state machine projection checks in `ReviewService`. |
| **Factory Pattern** | Encapsulated instantiation of decisions and versioned rulesets. | `DecisionFactory.from_inputs()` and `RuleSet.from_yaml()`. |
| **Observer Pattern** | Asynchronous event distribution to SSE web streams and Qdrant indexers. | `EventPublisher` protocol broadcasting `DecisionEvent` payloads. |
| **Value Object Pattern** | Immutability and structural equality for measurements and calculations. | `@dataclass(frozen=True)` classes: `Recommendation`, `EngineInputs`, `SensorReading`, `WeatherSnapshot`. |
| **Facade Pattern** | Unified, atomic transactional entry point for decision generation. | `DecisionRecorder.record_decision()`. |

---

## 4. SQLite Storage Engine Invariants & Triggers
The SQLite storage engine enforces immutability via database-level triggers declared in `api/sql/triggers.sql`:
- `dec_core_immutable`: Aborts any attempt to modify original recommendation columns on `irrigation_decisions`.
- `dec_no_delete`: Aborts any attempt to delete historical decisions.
- `snap_no_update`, `snap_no_delete`: Enforces permanent immutability on input snapshots.
- `events_no_update`, `events_no_delete`: Enforces append-only constraints on the audit ledger.
- `rev_no_update`, `rev_no_delete`: Guarantees human review adjustments cannot be retroactively tampered with.
