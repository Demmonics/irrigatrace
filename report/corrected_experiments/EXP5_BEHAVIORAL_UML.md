# Experiment 5: Behavioral UML Modeling (Corrected)

**Course:** Object-Oriented Software Engineering (OOSE Lab, Semester 5)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Institution:** K. J. Somaiya College of Engineering (KJSCE), Somaiya Vidyavihar University  
**Student:** Yoosha Abbas (Roll No.: 16014224101, Batch: B2)  
**Date:** 2026-10-23  
**Course Outcome:** CO3  

---

## 1. Use Case Diagram (Canonical Specification)

```mermaid
flowchart LR
    subgraph Actors["Primary and Supporting Actors"]
        Supervisor["Field Supervisor\n(Role: SUPERVISOR)"]
        Admin["Farm Administrator\n(Role: ADMIN)"]
        Auditor["Regulatory Auditor\n(Role: AUDITOR)"]
        SystemScheduler["System Scheduler /\nTelemetry Ingestion"]
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

    SystemScheduler --> UC01
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
```

---

## 2. Sequence Diagrams

### 2.1 Sequence 1: Automated Recommendation & Hash Genesis
```mermaid
sequenceDiagram
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
```

### 2.2 Sequence 2: Human Review Workflow (Supervisor Override)
```mermaid
sequenceDiagram
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
```

### 2.3 Sequence 3: Replay & Reproduce Check
```mermaid
sequenceDiagram
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
```

---

## 3. Activity Diagram (Decision Governance Lifecycle)

```mermaid
flowchart TD
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
```

---

## 4. State Machine Diagram (Canonical DecisionStatus Lifecycle)

```mermaid
stateDiagram-v2
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
```
