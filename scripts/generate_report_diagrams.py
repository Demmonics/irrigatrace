import os
import sys
import base64
import urllib.request
from pathlib import Path

DIAGRAMS = {
    "fig_4_1_use_case_diagram": """flowchart LR
    subgraph Actors["Primary and Supporting Actors"]
        Supervisor["Field Supervisor\\n(Role: SUPERVISOR)"]
        Admin["Farm Administrator\\n(Role: ADMIN)"]
        Auditor["Regulatory Auditor\\n(Role: AUDITOR)"]
        SystemTimer["System Scheduler /\\nTelemetry Ingestion"]
    end

    subgraph System["IrrigaTrace Observatory System Boundary"]
        UC01["UC-01: Ingest Sensor Telemetry & Weather Forecast"]
        UC02["UC-02: Compute Deterministic Irrigation Recommendation"]
        UC03["UC-03: Freeze Decision Snapshot & Initialize Genesis Hash"]
        UC04["UC-04: Review Recommendation (Approve / Modify / Reject)"]
        UC05["UC-05: Reconstruct Historical State at Time t (Replay)"]
        UC06["UC-06: Verify Ruleset & Engine Code Drift (Reproduce)"]
        UC07["UC-07: Analyze Input Deltas & Sensitivity (Flip Analysis)"]
        UC08["UC-08: Simulate Environmental Scenarios (Lab Bench)"]
        UC09["UC-09: Verify Append-Only Cryptographic Hash Chains"]
        UC10["UC-10: Record Realized Field Outcome (72h Post-Irrigation)"]
        UC11["UC-11: Generate Operator Briefing (LLM Grounding)"]
    end

    SystemTimer --> UC01
    UC01 --> UC02
    UC02 --> UC03
    UC02 -.->|<<include>>| UC11

    Supervisor --> UC04
    Supervisor --> UC05
    Supervisor --> UC10

    Admin --> UC07
    Admin --> UC08
    Admin --> UC06

    Auditor --> UC05
    Auditor --> UC09
""",

    "fig_4_2_sequence_genesis": """sequenceDiagram
    autonumber
    actor Timer as System Scheduler
    participant API as FastAPI Router (/decisions)
    participant Rec as DecisionRecorder
    participant Eng as IrrigationEngine
    participant Repo as SqliteDecisionRepository
    participant DB as SQLite WAL (Triggers)
    participant Bus as EventPublisher (SSE / Indexer)

    Timer->>API: POST /api/decisions (plot_id, inputs)
    API->>Rec: record_decision(plot_id, inputs)
    Rec->>Eng: recommend(inputs, ruleset)
    Eng-->>Rec: Recommendation(action, duration_h, confidence, fired_rules)
    Rec->>Repo: save_snapshot(DecisionSnapshot)
    Repo->>DB: INSERT INTO decision_snapshots
    Note over DB: snap_no_update trigger active
    Rec->>Repo: save_decision(IrrigationDecision)
    Repo->>DB: INSERT INTO irrigation_decisions
    Note over DB: dec_core_immutable trigger active
    Rec->>Repo: save_event(seq=1, SENSOR_RECEIVED, prev="GENESIS")
    Repo->>DB: INSERT INTO decision_events
    Rec->>Repo: save_event(seq=2, RECOMMENDATION_GENERATED)
    Repo->>DB: INSERT INTO decision_events
    Rec->>Bus: publish(DecisionEvent)
    Rec-->>API: IrrigationDecision (status=GENERATED)
    API-->>Timer: 201 Created (IRR-2026-XXX)
""",

    "fig_4_3_sequence_override": """sequenceDiagram
    autonumber
    actor Sup as Field Supervisor
    participant API as FastAPI Router (/review)
    participant Svc as ReviewService
    participant Repo as SqliteDecisionRepository
    participant DB as SQLite WAL (Triggers)
    participant Bus as EventPublisher

    Sup->>API: POST /api/decisions/{id}/review (action=MODIFY, duration=2.0h, reason=R-POWER)
    API->>Svc: submit_review(id, review_data, reviewer_id)
    Svc->>Repo: get_by_id(id)
    Repo->>DB: SELECT * FROM irrigation_decisions
    DB-->>Repo: decision (status=PENDING_REVIEW)
    Svc->>Repo: save_review(HumanReview)
    Repo->>DB: INSERT INTO human_reviews
    Note over DB: Original AI duration preserved!
    Svc->>Repo: update_status(id, status=MODIFIED)
    Repo->>DB: UPDATE irrigation_decisions SET status='MODIFIED'
    Note over DB: Only status projection can change
    Svc->>Repo: save_event(seq=4, REVIEW_MODIFIED, prev_hash=H3)
    Repo->>DB: INSERT INTO decision_events
    Svc->>Bus: publish(DecisionEvent)
    Svc-->>API: Updated IrrigationDecision
    API-->>Sup: 200 OK (Decision MODIFIED & Finalized)
""",

    "fig_4_4_sequence_replay": """sequenceDiagram
    autonumber
    actor Aud as Regulatory Auditor
    participant API as FastAPI Router
    participant Rep as DecisionReplayService
    participant Eng as IrrigationEngine
    participant Repo as SqliteDecisionRepository
    participant DB as SQLite WAL

    Aud->>API: GET /api/decisions/{id}/reproduce
    API->>Rep: reproduce(decision_id)
    Rep->>Repo: get_snapshot(decision_id)
    Repo->>DB: SELECT * FROM decision_snapshots
    DB-->>Rep: DecisionSnapshot (historical inputs, ruleset)
    Rep->>Eng: recommend(snapshot.inputs, current_ruleset)
    Eng-->>Rep: current_recommendation
    Rep->>Rep: diff(snapshot.inputs, current_recommendation)
    Rep-->>API: DecisionComparison (deltas, match=true/false)
    API-->>Aud: 200 OK (Reproduce Report)
""",

    "fig_4_5_activity_lifecycle": """flowchart TD
    subgraph Ingestion["Field Telemetry & Ingestion"]
        Start([Telemetry Arrives]) --> ReadSensors[Sample Soil Moisture & Ambient Temp]
        ReadSensors --> FetchWeather[Capture Weather Forecast & Rain Prob]
        FetchWeather --> FreezeSnap[Freeze Immutable Inputs Snapshot]
    end

    subgraph Engine["Deterministic Engine & Storage"]
        FreezeSnap --> ExecEngine[Execute Pure FAO-56 Engine]
        ExecEngine --> CalcDeficit[Calculate Root-Zone Moisture Deficit]
        CalcDeficit --> GenRec[Generate Recommendation Value Object]
        GenRec --> GenesisHash[Compute Genesis SHA-256 Hash]
        GenesisHash --> StoreDB[(Store with DB Triggers)]
    end

    subgraph Review["Supervisor Review & Override"]
        StoreDB --> NeedsReview{Requires Review?}
        NeedsReview -- Auto Finalize --> Finalize[Set Status: FINALIZED]
        NeedsReview -- Human Queue --> Queue[Display in Supervisor Queue]
        Queue --> ActionChoice{Supervisor Action}
        ActionChoice -- Approve --> AppReview[Record HumanReview: APPROVE]
        ActionChoice -- Modify --> ModReview[Record HumanReview: MODIFY + Reason]
        ActionChoice -- Reject --> RejReview[Record HumanReview: REJECT + Reason]
        AppReview --> AppendChain[Append Event to SHA-256 Chain]
        ModReview --> AppendChain
        RejReview --> AppendChain
        AppendChain --> Finalize
    end

    subgraph Audit["Audit Ledger & Outcome"]
        Finalize --> FieldApply[Apply Water to Plot SG-104]
        FieldApply --> Wait72[Wait 72 Hours Observational Window]
        Wait72 --> LogOutcome[Record OutcomeRecord: Actual Moisture & Health]
        LogOutcome --> AppendOutcome[Append OUTCOME_RECORDED Event]
        AppendOutcome --> End([Decision Lifecycle Complete])
    end
""",

    "fig_4_6_state_machine_lifecycle": """stateDiagram-v2
    [*] --> GENERATED : Telemetry Ingested & Engine Evaluated
    GENERATED --> PENDING_REVIEW : Snapshot Frozen & Genesis Hash Sealed
    
    PENDING_REVIEW --> APPROVED : Review Action: APPROVE (Duration Accepted)
    PENDING_REVIEW --> MODIFIED : Review Action: MODIFY (Duration Adjusted + Reason)
    PENDING_REVIEW --> REJECTED : Review Action: REJECT (Duration Zeroed + Reason)
    
    APPROVED --> FINALIZED : Decision Finalized for Actuation
    MODIFIED --> FINALIZED : Decision Finalized for Actuation
    REJECTED --> FINALIZED : Decision Closed (No Pumping)
    
    FINALIZED --> ACTION_RECORDED : Pump Actuation Executed / Deferred
    ACTION_RECORDED --> OUTCOME_RECORDED : 72h Realized Field Observations Logged
    OUTCOME_RECORDED --> [*] : Lifecycle Immutable & Archived
""",

    "fig_4_7_class_diagram": """classDiagram
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
""",

    "fig_4_8_object_diagram": """classDiagram
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
""",

    "fig_5_1_system_architecture": """flowchart LR
    subgraph Client["Presentation Layer (Client Browser)"]
        UI["Next.js 14 App Router\\n(Screens S1-S8: Dashboard, Case File, Replay, Compare, Lab, Audit)"]
    end

    subgraph Service["Application & Service Layer (FastAPI)"]
        Router["FastAPI REST & SSE Routers"]
        Recorder["DecisionRecorder (Facade)"]
        ReviewSvc["ReviewService"]
        ReplaySvc["DecisionReplayService"]
        IntegritySvc["IntegrityService"]
        NarrationSvc["NarrationService (Strategy)"]
        Validator["NumberConsistencyValidator"]
    end

    subgraph Domain["Domain Model Layer (Pure Functional OO)"]
        Engine["IrrigationEngine (v1.4.2)"]
        Models["Domain Entities & Value Objects"]
        Ports["Repository & Clock Protocols"]
    end

    subgraph Storage["Storage & Persistence Layer"]
        DB[("SQLite Database (WAL Mode)\\nTriggers: dec_core_immutable, snap_no_update")]
        Repos["Sqlite Repositories"]
    end

    subgraph AI["AI Inference & Vector Engines"]
        Ollama[["Local Ollama Daemon\\nqwen2.5:3b (Briefings)"]]
        Gemini[["Google Gemini API\\n(Fallback & Multilingual)"]]
        Qdrant[("Qdrant Vector DB /\\nDeterministic SQL Fallback")]
    end

    UI <-- REST / SSE --> Router
    Router --> Recorder
    Router --> ReviewSvc
    Router --> ReplaySvc
    Router --> IntegritySvc
    Recorder --> Engine
    Recorder --> Repos
    ReviewSvc --> Repos
    IntegritySvc --> Repos
    Repos --> DB
    NarrationSvc --> Validator
    NarrationSvc --> Ollama
    NarrationSvc -.-> Gemini
    Recorder -.-> Qdrant
""",

    "fig_5_2_package_diagram": """flowchart TD
    subgraph WebApp["web/ (Next.js Frontend)"]
        Screens["app/(screens)"]
        Components["components/ui & decision"]
    end

    subgraph APIPkg["api/irrigatrace/api/ (Presentation)"]
        Routers["routers/"]
        Schemas["schemas/"]
        Deps["deps.py & sse.py"]
    end

    subgraph ServicesPkg["api/irrigatrace/services/ (Orchestration)"]
        Services["recorder, review, replay, compare, integrity, narration"]
    end

    subgraph DomainPkg["api/irrigatrace/domain/ (Core Business Logic)"]
        DomainModels["models.py"]
        DomainEngine["engine.py"]
        DomainPorts["ports.py (Protocols)"]
    end

    subgraph InfraPkg["api/irrigatrace/infra/ (Infrastructure)"]
        DBInfra["db/ connection & repositories"]
        AIInfra["ollama, gemini, qdrant"]
    end

    WebApp -->|HTTP / JSON| APIPkg
    APIPkg --> ServicesPkg
    ServicesPkg --> DomainPkg
    ServicesPkg --> DomainPorts
    InfraPkg ..|> DomainPorts
    InfraPkg --> DomainPkg
    ServicesPkg --> InfraPkg
""",

    "fig_5_3_component_diagram": """componentDiagram
    component [Next.js Web Client] as WebUI
    component [FastAPI Gateway Router] as Gateway
    component [DecisionRecorder] as RecorderComp
    component [ReviewService] as ReviewComp
    component [DecisionReplayService] as ReplayComp
    component [IntegrityService] as IntegrityComp
    component [IrrigationEngine] as EngineComp
    component [NarrationService] as NarrationComp
    component [SqliteDecisionRepository] as RepoComp
    database "SQLite Storage Engine\\n(WAL + Triggers)" as SQLiteDB
    component [Local Ollama Client] as OllamaComp

    portin " " as p1
    portin " " as p2

    WebUI ..> Gateway : REST / SSE
    Gateway ..> RecorderComp
    Gateway ..> ReviewComp
    Gateway ..> ReplayComp
    Gateway ..> IntegrityComp

    RecorderComp ..> EngineComp : inputs -> Recommendation
    RecorderComp ..> RepoComp : persist aggregate
    ReviewComp ..> RepoComp : record override
    IntegrityComp ..> RepoComp : verify hashes
    NarrationComp ..> OllamaComp : generate text

    RepoComp ..> SQLiteDB : SQL execute
""",

    "fig_5_4_deployment_diagram": """deploymentDiagram
    node "Client Device Node" <<Device>> {
        node "Web Browser Environment" {
            artifact "Next.js Static Bundle & React Hydration"
        }
    }

    node "On-Premises Application Server Node" <<Execution Environment>> {
        node "Python 3.12/3.13 Runtime" {
            artifact "Uvicorn ASGI Server"
            artifact "FastAPI Application Service"
            artifact "Clean Architecture Domain & Service Modules"
        }
        node "Embedded Storage Subsystem" {
            database "irrigatrace.db (SQLite WAL Mode)"
            artifact "Append-Only SQL Triggers"
        }
    }

    node "Local AI Workstation Node" <<Hardware Device>> {
        node "Ollama Inference Runtime" {
            artifact "qwen2.5:3b Model Weights"
            artifact "nomic-embed-text Model Weights"
        }
    }

    node "External Cloud Infrastructure Node" <<Cloud Provider>> {
        node "Google AI Cloud" {
            artifact "Gemini 2.5 Flash Multilingual API"
        }
        node "Qdrant Cloud (Optional)" {
            artifact "Sugarcane Vector Similarity Index"
        }
    }

    "Client Device Node" -- "HTTPS / TLS 1.3 (Port 3000 / 8000)" -- "On-Premises Application Server Node"
    "On-Premises Application Server Node" -- "Local IPC / HTTP (Port 11434)" -- "Local AI Workstation Node"
    "On-Premises Application Server Node" -- "Outbound HTTPS (REST)" -- "External Cloud Infrastructure Node"
""",

    "fig_5_5_erd": """erDiagram
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
"""
}

def main():
    out_dir = Path(r"c:\Study\OOSE\Mini Project\report\diagrams")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {len(DIAGRAMS)} diagrams in {out_dir}...")
    
    for name, code in DIAGRAMS.items():
        mmd_file = out_dir / f"{name}.mmd"
        png_file = out_dir / f"{name}.png"
        
        # 1. Write MMD source
        with open(mmd_file, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[OK] Wrote {mmd_file.name}")
        
        # 2. Download PNG render via mermaid.ink
        try:
            enc = base64.urlsafe_b64encode(code.strip().encode("utf-8")).decode("utf-8")
            url = f"https://mermaid.ink/img/{enc}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                with open(png_file, "wb") as pf:
                    pf.write(data)
            print(f"  [OK] Rendered {png_file.name} ({len(data)} bytes)")
        except Exception as e:
            print(f"  [WARN] Failed to render PNG for {name}: {e}")

if __name__ == "__main__":
    main()
