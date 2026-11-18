import os
import base64
import urllib.request
from pathlib import Path

FIXED_DIAGRAMS = {
    "fig_4_2_sequence_genesis": """sequenceDiagram
    autonumber
    actor Timer as System Scheduler
    participant API as FastAPI Router
    participant Rec as DecisionRecorder
    participant Eng as IrrigationEngine
    participant Repo as SqliteDecisionRepository
    participant DB as SQLite WAL
    participant Bus as EventPublisher

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
    participant API as FastAPI Router
    participant Svc as ReviewService
    participant Repo as SqliteDecisionRepository
    participant DB as SQLite WAL
    participant Bus as EventPublisher

    Sup->>API: POST /api/decisions/{id}/review (action=MODIFY, duration=2.0h, reason=R-POWER)
    API->>Svc: submit_review(id, review_data, reviewer_id)
    Svc->>Repo: get_by_id(id)
    Repo->>DB: SELECT * FROM irrigation_decisions
    DB-->>Repo: decision (status=PENDING_REVIEW)
    Svc->>Repo: save_review(HumanReview)
    Repo->>DB: INSERT INTO human_reviews
    Note over DB: Original AI duration preserved
    Svc->>Repo: update_status(id, status=MODIFIED)
    Repo->>DB: UPDATE irrigation_decisions SET status='MODIFIED'
    Note over DB: Only status projection can change
    Svc->>Repo: save_event(seq=4, REVIEW_MODIFIED, prev_hash=H3)
    Repo->>DB: INSERT INTO decision_events
    Svc->>Bus: publish(DecisionEvent)
    Svc-->>API: Updated IrrigationDecision
    API-->>Sup: 200 OK (Decision MODIFIED & Finalized)
""",

    "fig_5_2_package_diagram": """flowchart TD
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
""",

    "fig_5_3_component_diagram": """flowchart TB
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
        DB[("SQLite Storage Engine (WAL Mode)\\nTriggers: dec_core_immutable, snap_no_update")]
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
""",

    "fig_5_4_deployment_diagram": """flowchart TB
    subgraph DeviceNode["Client Device Node (Farmer / Supervisor / Auditor)"]
        Browser["Modern Web Browser (Desktop / Mobile)\\nNext.js Client Bundle & SSR Hydration"]
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
        GeminiAPI[["Google Gemini 2.5 Flash API\\n(Fallback & Translation)"]]
        QdrantCloud[("Qdrant Cloud Vector Index\\n(With Deterministic SQL Fallback)")]
    end

    Browser <-->|HTTPS / TLS 1.3 (Ports 3000 / 8000)| Uvicorn
    Uvicorn --> FastAPI
    FastAPI --> DomainCode
    DomainCode --> SQLiteFile
    SQLiteFile --- Triggers
    DomainCode <-->|HTTP REST (Port 11434)| OllamaRuntime
    DomainCode -.->|Outbound HTTPS REST (TLS)| CloudNode
"""
}

def main():
    out_dir = Path(r"c:\Study\OOSE\Mini Project\report\diagrams")
    for name, code in FIXED_DIAGRAMS.items():
        mmd_file = out_dir / f"{name}.mmd"
        png_file = out_dir / f"{name}.png"
        with open(mmd_file, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            enc = base64.urlsafe_b64encode(code.strip().encode("utf-8")).decode("utf-8")
            url = f"https://mermaid.ink/img/{enc}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                with open(png_file, "wb") as pf:
                    pf.write(data)
            print(f"[OK] Rendered {png_file.name} ({len(data)} bytes)")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")

if __name__ == "__main__":
    main()
