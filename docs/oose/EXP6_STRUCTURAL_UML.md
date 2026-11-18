# Experiment 6: Structural UML Modeling

**Course:** Object-Oriented Software Engineering (OOSE Lab)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
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
    +str name
    +float area_hectares
    +str crop_type
    +str soil_type
    +CropStage stage
  }

  class SensorReading {
    +str plot_id
    +datetime timestamp
    +float soil_moisture_pct
    +float ambient_temp_c
    +float humidity_pct
    +float electrical_conductivity
  }

  class WeatherSnapshot {
    +datetime forecast_time
    +float temp_max_c
    +float temp_min_c
    +float rain_probability_pct
    +float expected_rain_mm
    +float wind_speed_kmh
  }

  class Recommendation {
    +RecommendedAction action
    +float recommended_duration_h
    +float confidence
    +List~str~ fired_rules
    +Map factors
  }

  class EngineInputs {
    +FarmPlot plot
    +SensorReading sensor
    +WeatherSnapshot weather
    +float days_since_last_irrigation
  }

  class IrrigationEngine {
    +RuleSet ruleset
    +evaluate(inputs) Recommendation
    +preview(inputs) Map
  }

  class RuleSet {
    +str version
    +Map~CropStage, StageParam~ stage_params
  }

  class StageParam {
    +float target_moisture_pct
    +float critical_moisture_pct
    +float max_duration_h
  }

  class DecisionSnapshot {
    +str id
    +str decision_id
    +datetime snapshot_time
    +EngineInputs inputs
    +Recommendation recommendation
  }

  class HumanReview {
    +str id
    +str decision_id
    +ReviewAction action
    +float final_duration_h
    +str modified_by
    +str reason_code
    +str justification_notes
  }

  class DecisionExplanation {
    +str decision_id
    +List factors
    +str narrative_summary
    +str provenance
    +datetime generated_at
  }

  class DecisionEvent {
    +str id
    +str decision_id
    +int seq
    +int seq_in_chain
    +EventType event_type
    +str actor_id
    +str payload_json
    +str prev_hash
    +str this_hash
  }

  class OutcomeRecord {
    +str id
    +str decision_id
    +float actual_duration_h
    +float soil_moisture_after_pct
    +float observed_rainfall_mm
    +bool water_stress_observed
    +str notes
  }

  class IrrigationDecision {
    +str id
    +str plot_id
    +DecisionStatus status
    +datetime created_at
    +DecisionSnapshot snapshot
    +Optional~HumanReview~ review
    +Optional~DecisionExplanation~ explanation
    +Optional~OutcomeRecord~ outcome
    +List~DecisionEvent~ events
  }

  %% Relationships
  IrrigationDecision *-- DecisionSnapshot : composition
  IrrigationDecision o-- HumanReview : aggregation (0..1)
  IrrigationDecision *-- DecisionExplanation : composition
  IrrigationDecision o-- OutcomeRecord : aggregation (0..1)
  IrrigationDecision *-- DecisionEvent : has audit stream (1..*)
  DecisionSnapshot o-- FarmPlot : references
  DecisionSnapshot o-- SensorReading : contains
  DecisionSnapshot o-- WeatherSnapshot : contains
  DecisionSnapshot o-- Recommendation : contains
  IrrigationEngine ..> EngineInputs : consumes
  IrrigationEngine ..> Recommendation : produces
  IrrigationEngine o-- RuleSet : uses
  RuleSet *-- StageParam : contains
```

---

## 2. Object Diagram: Instance IRR-2026-018 (Hero Case)

```mermaid
classDiagram
    direction TB
    
    class dec_018["irr_018 : IrrigationDecision"] {
        id = "IRR-2026-018"
        plot_id = "SG-104"
        status = "FINALIZED"
        created_at = "2026-10-24 10:05:00"
    }

    class snap_018["snap_018 : DecisionSnapshot"] {
        snapshot_time = "2026-10-24 10:05:00"
        inputs_hash = "e3b0c442..."
    }

    class rec_018["rec_018 : Recommendation"] {
        action = "IRRIGATE"
        recommended_duration_h = 2.8
        confidence = 0.94
        fired_rules = ["SOIL_MOISTURE_CRITICAL", "STAGE_CANOPY_ACTIVE"]
    }

    class rev_018["rev_018 : HumanReview"] {
        action = "MODIFY"
        final_duration_h = 2.0
        modified_by = "usr-sup-rajesh"
        reason_code = "WEATHER_UNEXPECTED"
        justification_notes = "Rain expected within 6h"
    }

    class event1["ev_1 : DecisionEvent"] {
        seq = 1
        event_type = "DECISION_CREATED"
        prev_hash = "GENESIS"
        this_hash = "a7f1...e9"
    }

    class event2["ev_2 : DecisionEvent"] {
        seq = 2
        event_type = "REVIEW_MODIFIED"
        prev_hash = "a7f1...e9"
        this_hash = "b2c3...f4"
    }

    dec_018 --> snap_018
    snap_018 --> rec_018
    dec_018 --> rev_018
    dec_018 --> event1
    dec_018 --> event2
```

---

## 3. Component Diagram

```mermaid
graph TD
    subgraph Presentation Layer [Next.js App Router]
        WebUI["Observatory UI (React + Tailwind)"]
        OrbitScrubber["Orbit Timeline Component"]
        LabSimulator["Lab Bench Interactive Slider"]
    end

    subgraph Service & API Layer [FastAPI Core]
        APIEndpoints["REST & SSE Endpoints"]
        DecRecorder["DecisionRecorder Facade"]
        RevService["ReviewService"]
        ReplaySvc["DecisionReplayService"]
        IntegritySvc["IntegrityService (SHA-256)"]
        NarrationSvc["NarrationService (Strategy)"]
        Validator["NumberConsistencyValidator (Regex)"]
    end

    subgraph Domain Engine Layer [Pure Python]
        DomainModels["Domain Entities (Pydantic)"]
        RuleEngine["FAO-56 IrrigationEngine (Pure)"]
    end

    subgraph Storage & External Services
        SQLite["SQLite WAL + Triggers (irrigatrace.db)"]
        Ollama["Local Ollama LLM (Qwen2.5:3b)"]
        GeminiAPI["Google Gemini API (Cloud)"]
        Qdrant["Qdrant Cloud / SQL Fallback"]
    end

    WebUI --> APIEndpoints
    APIEndpoints --> DecRecorder
    APIEndpoints --> RevService
    APIEndpoints --> ReplaySvc
    APIEndpoints --> IntegritySvc
    APIEndpoints --> NarrationSvc

    DecRecorder --> RuleEngine
    DecRecorder --> SQLite
    RevService --> SQLite
    IntegritySvc --> SQLite

    NarrationSvc --> Validator
    NarrationSvc --> Ollama
    NarrationSvc --> GeminiAPI
```

---

## 4. Deployment Diagram

```mermaid
deploymentDiagram
    node "Client Device (Browser)" {
        artifact "Next.js Web Client (Port 3000)" as WebClient
    }

    node "Host Machine (Windows / Linux)" {
        node "Python Runtime (Port 8000)" {
            artifact "FastAPI Application Server" as APIServer
            artifact "IrrigaTrace Domain & Services" as Services
        }

        node "Database Storage" {
            database "irrigatrace.db (SQLite WAL Mode)" as SQLiteDB
        }

        node "Ollama Inference Daemon (Port 11434)" {
            artifact "Qwen 2.5:3b Local LLM" as OllamaModel
        }
    }

    node "External Cloud Services (TLS)" {
        cloud "Google Gemini AI API" as GeminiCloud
        cloud "Qdrant Cloud Vector Service" as QdrantCloud
    }

    WebClient --> APIServer : HTTP / SSE (Port 8000)
    APIServer --> SQLiteDB : Local File I/O (WAL)
    APIServer --> OllamaModel : HTTP REST (Port 11434)
    APIServer --> GeminiCloud : HTTPS API (gRPC / REST)
    APIServer --> QdrantCloud : HTTPS REST / Graceful Fallback
```
