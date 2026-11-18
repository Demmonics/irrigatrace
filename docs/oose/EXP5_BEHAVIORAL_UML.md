# Experiment 5: Behavioral UML Modeling

**Course:** Object-Oriented Software Engineering (OOSE Lab)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Date:** 2026-10-23  
**Course Outcome:** CO3

---

## 1. Use Case Diagram (3 Actors)

```mermaid
flowchart LR
    subgraph Actors
        Supervisor["Field Supervisor"]
        Admin["Farm Administrator"]
        Auditor["Regulatory Auditor"]
        SystemTimer["System Scheduler / Sensors"]
    end

    subgraph IrrigaTrace System
        UC1["Ingest Telemetry & Weather"]
        UC2["Compute Automated Recommendation"]
        UC3["Freeze Snapshot & Hash Genesis"]
        UC4["Review Recommendation (Approve / Modify / Reject)"]
        UC5["Time-Travel Replay (State at t)"]
        UC6["Run Reproduce Check"]
        UC7["Perform Flip Sensitivity Analysis"]
        UC8["Simulate Scenario on Lab Bench"]
        UC9["Verify Cryptographic Hash Chains"]
        UC10["Record Realized Field Outcome"]
    end

    SystemTimer --> UC1
    UC1 --> UC2
    UC2 --> UC3

    Supervisor --> UC4
    Supervisor --> UC5
    Supervisor --> UC10

    Admin --> UC7
    Admin --> UC8
    Admin --> UC6

    Auditor --> UC5
    Auditor --> UC9
```

---

## 2. Sequence Diagrams

### 2.1 Sequence 1: Automated Recommendation & Hash Genesis
```mermaid
sequenceDiagram
    autonumber
    actor Sensor as Telemetry / Sensor
    participant API as FastAPI Router
    participant Rec as DecisionRecorder
    participant Eng as IrrigationEngine
    participant DB as SQLite WAL
    participant Ledger as Hash Chain Ledger

    Sensor->>API: POST /api/decisions (inputs)
    API->>Rec: record_new_decision(inputs)
    Rec->>Eng: evaluate(inputs)
    Eng-->>Rec: Recommendation(action, duration, rules)
    Rec->>DB: INSERT decision_snapshots (inputs, recommendation)
    Note over DB: Snapshot frozen (triggers prevent UPDATE)
    Rec->>Ledger: append_event(DECISION_CREATED, payload, prev_hash="GENESIS")
    Ledger-->>Rec: event(seq=1, hash=H1)
    Rec-->>API: IrrigationDecision(status=COLLECTED)
    API-->>Sensor: 201 Created (IRR-2026-XXX)
```

### 2.2 Sequence 2: Human Review Workflow (Supervisor Override)
```mermaid
sequenceDiagram
    autonumber
    actor Sup as Field Supervisor
    participant API as FastAPI Router
    participant Svc as ReviewService
    participant DB as SQLite WAL
    participant Ledger as Hash Chain Ledger

    Sup->>API: POST /api/decisions/{id}/review (action=MODIFY, duration=2.0, reason)
    API->>Svc: submit_review(id, review_data)
    Svc->>DB: Check decision.status == AWAITING_REVIEW
    Svc->>DB: INSERT human_reviews (preserves original AI rec)
    Svc->>DB: UPDATE decisions SET status = 'FINALIZED'
    Svc->>Ledger: append_event(REVIEW_MODIFIED, payload, prev_hash=H2)
    Ledger-->>Svc: event(seq=3, hash=H3)
    Svc-->>API: Updated IrrigationDecision
    API-->>Sup: 200 OK (Decision Finalized)
```

### 2.3 Sequence 3: Replay & Reproduce Check
```mermaid
sequenceDiagram
    autonumber
    actor User as Agronomist / Auditor
    participant API as FastAPI Router
    participant Rep as DecisionReplayService
    participant Eng as IrrigationEngine
    participant DB as SQLite WAL

    User->>API: GET /api/decisions/{id}/reproduce
    API->>Rep: check_reproduce(id)
    Rep->>DB: get_decision(id) -> snapshot
    Rep->>Eng: evaluate(snapshot.inputs) using current ruleset
    Eng-->>Rep: current_rec
    Rep->>Rep: diff(snapshot.recommendation, current_rec)
    Rep-->>API: ReproduceReport(match=True/False, deltas)
    API-->>User: 200 OK (Reproduce Result)
```

---

## 3. Activity Diagram (Decision Governance Lifecycle)

```mermaid
flowchart TD
    Start([Sensor Reading Arrives]) --> Freeze[Freeze Immutable Inputs Snapshot]
    Freeze --> EvalEngine[Execute Pure FAO-56 Engine]
    EvalEngine --> GenRec[Generate AI Recommendation]
    GenRec --> HashGenesis[Compute Genesis Hash & Append Event]
    HashGenesis --> AwaitReview{Requires Human Review?}
    
    AwaitReview -- No (Auto-Approve Threshold) --> AutoFinal[Set Status: FINALIZED]
    AwaitReview -- Yes --> DisplayQueue[Display in Supervisor Queue]
    
    DisplayQueue --> SupDecision{Supervisor Action}
    SupDecision -- Approve --> RecApprove[Record HumanReview: APPROVE]
    SupDecision -- Modify Duration --> RecModify[Record HumanReview: MODIFY + Reason Code]
    SupDecision -- Reject Pumping --> RecReject[Record HumanReview: REJECT + Reason Code]
    
    RecApprove --> AppendHash[Append Event to Hash Chain]
    RecModify --> AppendHash
    RecReject --> AppendHash
    
    AppendHash --> AutoFinal
    AutoFinal --> Wait72h[Wait 72 Hours in Field]
    Wait72h --> LogOutcome[Record Field Moisture & Outcome Record]
    LogOutcome --> End([Decision Lifecycle Archived])
```

---

## 4. State Machine Diagram (IrrigationDecision Lifecycle)

```mermaid
stateDiagram-v2
    [*] --> COLLECTED : Sensor & Weather Ingested
    COLLECTED --> RECOMMENDED : Pure Engine Evaluated
    RECOMMENDED --> RECORDED : Snapshot & Genesis Hash Sealed
    
    RECORDED --> AWAITING_REVIEW : Queued for Field Supervisor
    
    AWAITING_REVIEW --> FINALIZED : Review Approved (duration kept)
    AWAITING_REVIEW --> FINALIZED : Review Modified (duration adjusted + reason logged)
    AWAITING_REVIEW --> FINALIZED : Review Rejected (duration = 0.0 + reason logged)
    
    FINALIZED --> OUTCOME_RECORDED : Post-irrigation observations recorded (72h)
    OUTCOME_RECORDED --> [*]
```
