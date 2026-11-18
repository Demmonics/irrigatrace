# Experiment 6: Structural UML Modeling (Corrected)

**Course:** Object-Oriented Software Engineering (OOSE Lab, Semester 5)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Institution:** K. J. Somaiya College of Engineering (KJSCE), Somaiya Vidyavihar University  
**Student:** Yoosha Abbas (Roll No.: 16014224101, Batch: B2)  
**Date:** 2026-10-23  
**Course Outcome:** CO3  

---

## 1. Domain Class Diagram (14 Core Entities)
*Generated directly from active codebase AST (`api/irrigatrace/domain/models.py` & `engine.py`).*

```mermaid
classDiagram
    direction TB

    class FarmPlot {
        +str id
        +str code
        +str name
        +float area_ha
        +str soil_type
        +str planting_date
        +float application_rate_mm_h
        +str crop
        +str variety
        +str irrigation_method
        +str geojson
        +crop_stage_on(date) CropStage
    }

    class SensorReading {
        +str id
        +str plot_id
        +str ts
        +float soil_moisture_pct
        +float temperature_c
        +str source
        +str quality_flag
        +is_stale(now_iso, threshold_hours) bool
    }

    class WeatherSnapshot {
        +str id
        +str plot_id
        +str captured_at
        +float rain_probability_pct
        +float forecast_rain_mm
        +int horizon_h
        +str source
    }

    class EngineInputs {
        +float soil_moisture_pct
        +float temperature_c
        +float rain_probability_pct
        +float forecast_rain_mm
        +CropStage crop_stage
        +int days_since_last_irrigation
        +float application_rate_mm_h
        +int active_root_zone_mm
        +str sensor_reading_ts
        +to_dict() dict
    }

    class Recommendation {
        +RecommendedAction action
        +float duration_h
        +float confidence
        +List~str~ fired_rules
    }

    class RuleSet {
        +str version
        +dict stage_params
        +dict temperature
        +dict rain
        +dict duration
        +dict confidence
        +from_yaml(yaml_content) RuleSet
        +to_json() str
        +sha256() str
    }

    class IrrigationEngine {
        +str VERSION
        +engine_code_sha256() str
        +recommend(inputs, ruleset) Recommendation
        +build_deterministic_explanation(inputs, ruleset, rec) dict
    }

    class DecisionSnapshot {
        +str decision_id
        +str sensor_reading_id
        +str weather_snapshot_id
        +str inputs_json
        +str ruleset_json
        +str engine_version
        +str engine_code_sha256
        +str snapshot_sha256
        +sha256() str
    }

    class HumanReview {
        +str id
        +str decision_id
        +str reviewer_id
        +ReviewAction action
        +RecommendedAction final_action
        +float final_duration_h
        +str created_at
        +str reason_code
        +str reason_text
    }

    class DecisionEvent {
        +int seq
        +str decision_id
        +EventType event_type
        +str actor_id
        +str actor_role
        +str occurred_at
        +str payload_json
        +str prev_hash
        +str event_hash
        +calculate_hash(params) str
    }

    class IrrigationDecision {
        +str id
        +str plot_id
        +str created_at
        +str ruleset_version
        +RecommendedAction recommended_action
        +float recommended_duration_h
        +float confidence
        +DecisionStatus status
        +DecisionSnapshot snapshot
        +DecisionExplanation explanation
        +List~HumanReview~ reviews
        +List~DecisionEvent~ events
    }

    class OutcomeRecord {
        +str id
        +str decision_id
        +str recorded_by
        +str recorded_at
        +float actual_duration_h
        +float soil_moisture_after_pct
        +float actual_rainfall_mm
        +int water_stress_observed
        +str crop_health_note
        +str notes
    }

    FarmPlot "1" <-- "*" IrrigationDecision : targets
    IrrigationDecision "1" *-- "1" DecisionSnapshot : contains
    IrrigationDecision "1" *-- "*" HumanReview : evaluated by
    IrrigationDecision "1" *-- "*" DecisionEvent : audited by
    IrrigationDecision "1" o-- "0..1" OutcomeRecord : observes
    DecisionSnapshot ..> EngineInputs : serializes
    IrrigationEngine ..> Recommendation : computes
    IrrigationEngine ..> RuleSet : configures
```

---

## 2. Concrete Object Diagram (Instance IRR-2026-018 on Plot SG-104)

```mermaid
classDiagram
    direction TB
    note "Concrete Object Graph for Decision IRR-2026-018 on Plot SG-104"

    class plot_SG104 {
        id = "plot-104"
        code = "SG-104"
        name = "West Cane Plateau"
        crop = "sugarcane"
        soil_type = "Clay Loam"
        area_ha = 4.2
        application_rate_mm_h = 14.0
    }

    class reading_read104 {
        id = "read-104"
        plot_id = "plot-104"
        ts = "2026-10-24T09:41:58Z"
        soil_moisture_pct = 21.0
        temperature_c = 33.0
    }

    class weather_wsnap104 {
        id = "wsnap-104"
        plot_id = "plot-104"
        rain_probability_pct = 12.0
        forecast_rain_mm = 0.0
    }

    class dec_IRR2026018 {
        id = "IRR-2026-018"
        plot_id = "plot-104"
        ruleset_version = "rules-v1.4.2"
        recommended_action = IRRIGATE
        recommended_duration_h = 2.8
        confidence = 0.84
        status = MODIFIED
    }

    class snap_IRR2026018 {
        decision_id = "IRR-2026-018"
        engine_version = "1.4.2"
        snapshot_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }

    class rev_rev104 {
        id = "rev-018"
        reviewer_id = "usr-sup-01"
        action = MODIFY
        final_action = IRRIGATE
        final_duration_h = 2.0
        reason_code = "R-POWER"
        reason_text = "3-phase power window restricted to 2.0 hours"
    }

    class event_seq1 {
        seq = 1
        event_type = SENSOR_RECEIVED
        prev_hash = "GENESIS"
        event_hash = "9f83c68a..."
    }

    class event_seq4 {
        seq = 4
        event_type = REVIEW_MODIFIED
        prev_hash = "3a72b14c..."
        event_hash = "7d41f09e..."
    }

    class outcome_out104 {
        id = "out-018"
        actual_duration_h = 2.0
        soil_moisture_after_pct = 36.5
        water_stress_observed = 0
    }

    dec_IRR2026018 --> plot_SG104
    dec_IRR2026018 --> snap_IRR2026018
    dec_IRR2026018 --> rev_rev104
    dec_IRR2026018 --> event_seq1
    dec_IRR2026018 --> event_seq4
    dec_IRR2026018 --> outcome_out104
    snap_IRR2026018 --> reading_read104
    snap_IRR2026018 --> weather_wsnap104
```

---

## 3. Package, Component, and Deployment Diagrams

### 3.1 Package Diagram (Layered Dependencies)
```mermaid
flowchart TD
    subgraph WebApp["web/ Layer (Presentation: Next.js)"]
        Screens["app/(screens): S1-S8"]
        Components["components/ui & decision"]
    end

    subgraph APIPkg["api/irrigatrace/api/ Layer (Routing & DTOs)"]
        Routers["routers/ (decisions, review, lab, health)"]
        Schemas["schemas/ (Pydantic DTOs)"]
        Deps["deps.py & sse.py (Auth & Streaming)"]
    end

    subgraph ServicesPkg["api/irrigatrace/services/ Layer (Orchestration)"]
        Recorder["DecisionRecorder (Facade)"]
        ReviewSvc["ReviewService"]
        ReplaySvc["DecisionReplayService"]
        IntegritySvc["IntegrityService"]
        NarrationSvc["NarrationService"]
    end

    subgraph DomainPkg["api/irrigatrace/domain/ Layer (Core Business Domain)"]
        DomainModels["models.py (Entities & Value Objects)"]
        DomainEngine["engine.py (Pure FAO-56 Engine)"]
        DomainPorts["ports.py (Protocols)"]
    end

    subgraph InfraPkg["api/irrigatrace/infra/ Layer (Infrastructure)"]
        DBInfra["db/ connection & Sqlite repositories"]
        AIInfra["clients for ollama, gemini, qdrant"]
    end

    WebApp -->|HTTP / JSON / SSE| APIPkg
    APIPkg --> ServicesPkg
    ServicesPkg --> DomainPkg
    ServicesPkg --> DomainPorts
    InfraPkg -->|implements| DomainPorts
    InfraPkg --> DomainPkg
    ServicesPkg --> InfraPkg
```

### 3.2 Component Diagram
```mermaid
flowchart TB
    subgraph Client["Next.js Web Frontend"]
        WebUI["Web UI Component (S1-S8 Screens)"]
    end

    subgraph APIComp["FastAPI Gateway"]
        Gateway["REST & SSE API Router"]
    end

    subgraph Services["Orchestration Services"]
        RecorderComp["DecisionRecorder Component"]
        ReviewComp["ReviewService Component"]
        ReplayComp["DecisionReplayService Component"]
        IntegrityComp["IntegrityService Component"]
        NarrationComp["NarrationService Component"]
    end

    subgraph DomainComp["Core Domain"]
        EngineComp["IrrigationEngine (Pure FAO-56)"]
        RulesetComp["RuleSet Specification"]
    end

    subgraph Persistence["Storage Subsystem"]
        RepoComp["Sqlite Repositories Component"]
        DB[("SQLite Storage Engine (WAL Mode)\nTriggers: dec_core_immutable, snap_no_update")]
    end

    subgraph External["External AI & Telemetry"]
        OllamaComp[["Local Ollama Daemon (qwen2.5:3b)"]]
        GeminiComp[["Google Gemini Cloud API"]]
    end

    WebUI <-->|REST & SSE| Gateway
    Gateway --> RecorderComp
    Gateway --> ReviewComp
    Gateway --> ReplayComp
    Gateway --> IntegrityComp
    RecorderComp --> EngineComp
    EngineComp --> RulesetComp
    RecorderComp --> RepoComp
    ReviewComp --> RepoComp
    IntegrityComp --> RepoComp
    NarrationComp --> OllamaComp
    NarrationComp -.-> GeminiComp
    RepoComp --> DB
```

### 3.3 Deployment Diagram
```mermaid
flowchart TB
    subgraph DeviceNode["Client Device Node (Field Supervisor / Farm Admin / Auditor)"]
        Browser["Modern Web Browser (Desktop / Mobile)<br/>Next.js Client Bundle & SSR Hydration"]
    end

    subgraph AppServerNode["On-Premises Application Server Node"]
        subgraph PythonRuntime["Python 3.12 / 3.13 Runtime"]
            Uvicorn["Uvicorn ASGI Server"]
            FastAPI["FastAPI Web Framework"]
            DomainCode["IrrigaTrace Clean Architecture Modules"]
        end
        subgraph StorageSystem["Embedded Storage Subsystem"]
            SQLiteFile[("irrigatrace.db (WAL Mode)")]
            Triggers["Append-Only DB Triggers"]
        end
    end

    subgraph AINode["Local AI Workstation Node"]
        subgraph OllamaRuntime["Ollama Local Inference Runtime"]
            ModelWeights[["qwen2.5:3b LLM Weights"]]
            EmbedWeights[["nomic-embed-text Weights"]]
        end
    end

    subgraph CloudNode["External Cloud Infrastructure Node"]
        GeminiAPI[["Google Gemini 2.5 Flash API<br/>(Fallback & Translation)"]]
        QdrantCloud[("Qdrant Cloud Vector Index<br/>(With Deterministic SQL Fallback)")]
    end

    Browser <-->|"HTTPS / TLS 1.3 (Ports 3000 / 8000)"| Uvicorn
    Uvicorn --> FastAPI
    FastAPI --> DomainCode
    DomainCode --> SQLiteFile
    SQLiteFile --- Triggers
    DomainCode <-->|"HTTP REST (Port 11434)"| OllamaRuntime
    DomainCode -.->|"Outbound HTTPS REST (TLS)"| CloudNode
```
