# Experiment 3: Software Requirements Specification (SRS)

**Course:** Object-Oriented Software Engineering (OOSE Lab)  
**Standard:** IEEE Std 830-1998  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Date:** 2026-10-23  
**Course Outcome:** CO3

---

## 1. Introduction
### 1.1 Purpose
This document specifies the software requirements for **IrrigaTrace**, an observatory-grade audit, replay, and governance framework for AI-driven agricultural irrigation recommendations.

### 1.2 Intended Audience
Agronomists, irrigation network operators, compliance officers, and software engineers implementing or auditing precision agriculture platforms.

---

## 2. Overall Description
### 2.1 Product Perspective
IrrigaTrace acts as an authoritative governance layer sitting between field telemetry sensors (soil moisture, microclimate, weather forecasts) and irrigation valve actuators.

### 2.2 User Personas & Actors
1. **Farm Supervisor:** Reviews pending automated recommendations, enters manual duration adjustments, provides structured justification codes.
2. **Farm Administrator:** Configures plot boundaries, updates ruleset parameters, executes "what-if" simulations on the Lab Bench.
3. **Regulatory Auditor:** Inspects append-only audit ledgers, verifies SHA-256 cryptographic hash chains, exports tamper-evident reports.

---

## 3. Functional Requirements (FR)

| Req ID | Requirement Title | Description | Priority |
|---|---|---|---|
| **FR-01** | Deterministic Engine Calculation | Calculate irrigation action and duration using pure FAO-56 Penman-Monteith water balance. | Mandatory (P0) |
| **FR-02** | Immutable Input Snapshot | Record a frozen snapshot of soil moisture, temperature, and weather forecast at decision time. | Mandatory (P0) |
| **FR-03** | Recommendation Immutability | Enforce database trigger preventing any UPDATE or DELETE of the original AI recommendation. | Mandatory (P0) |
| **FR-04** | Human Review Segregation | Record human reviews as distinct entities (`Approve`, `Modify`, `Reject`) with supervisor signature and reason code. | Mandatory (P0) |
| **FR-05** | Append-Only Cryptographic Chain | Link all lifecycle events in an immutable SHA-256 hash ledger ($H_i = \text{SHA-256}(\dots \parallel H_{i-1})$). | Mandatory (P0) |
| **FR-06** | Historical State Replay | Reconstruct the complete system state at any timestamp $t$ along the decision timeline. | High (P1) |
| **FR-07** | Reproduce Verification | Re-execute the current engine logic on historical inputs and report rule/output diffs. | High (P1) |
| **FR-08** | Decision Comparison & Flips | Compare two decisions side-by-side and perform single-variable sensitivity flip analysis. | High (P2) |
| **FR-09** | Local LLM Narration & Validation | Generate plain-English explanations using local Ollama model; reject hallucinated numbers via regex. | High (P2) |
| **FR-10** | Multilingual Translation | Translate verified English summaries into Hindi and Kannada while preserving numbers. | Medium (P2) |
| **FR-11** | Lab Bench Simulator | Provide interactive scenario sliders with live client preview and real-time SSE event generation. | High (P2) |
| **FR-12** | Observational Outcome Tracking | Record realized field moisture 72h post-irrigation with mandatory non-causal disclaimer. | Medium (P1) |

---

## 4. Non-Functional Requirements (NFR)

| NFR ID | Category | Specification Metric |
|---|---|---|
| **NFR-01** | Performance | Stateless engine calculation response time $\le 50\text{ ms}$; SQLite query latency $\le 10\text{ ms}$. |
| **NFR-02** | Security & Tamper Resistance | Zero unauthorized modifications permitted on decision snapshots; triggers enforced at DB engine. |
| **NFR-03** | Reliability & Graceful Degradation | Offline-first: if Qdrant Cloud times out, seamlessly degrade to deterministic SQL search without failure. |
| **NFR-04** | Verifiability | 100% of decisions must yield a mathematically verifiable SHA-256 cryptographic proof. |
| **NFR-05** | Accessibility & Taste | WCAG 2.1 AA compliant contrast ($\ge 7:1$ for secondary text); responsive across 1440px to 390px. |

---

## 5. External Interface Specifications
- **Hardware / Telemetry:** REST ingestion of calibrated soil moisture (capacitance probes) and ambient temperature.
- **Ollama Engine:** Local daemon at `http://localhost:11434/api/generate` running `qwen2.5:3b`.
- **Google Gemini API:** Cloud model `gemini-2.5-flash` for high-fidelity multilingual translation.
- **Qdrant Vector Database:** Derived cosine similarity index (with local SQL fallback).

---

## 6. Traceability Matrix: Requirements to Test Cases

| Functional Requirement | Test Case ID | Test File | Verification Outcome |
|---|---|---|---|
| **FR-01 (Engine)** | TC-01, TC-02 | `test_engine.py` | PASS |
| **FR-02 (Snapshot)** | TC-03 | `test_triggers_and_invariants.py` | PASS |
| **FR-03 (Immutability)** | TC-04, TC-05 | `test_triggers_and_invariants.py` | PASS |
| **FR-04 (Human Review)** | TC-06, TC-07 | `test_lifecycle_and_integrity.py` | PASS |
| **FR-05 (Hash Chain)** | TC-08, TC-09 | `test_lifecycle_and_integrity.py` | PASS |
| **FR-06 (Replay)** | TC-10 | `test_lifecycle_and_integrity.py` | PASS |
| **FR-07 (Reproduce)** | TC-11 | `test_lifecycle_and_integrity.py` | PASS |
| **FR-08 (Compare & Flips)** | TC-12, TC-13 | `test_comparison_flips.py` | PASS |
| **FR-09 (Validator)** | TC-14, TC-15 | `test_validator.py` | PASS |
| **FR-11 (API & SSE)** | TC-16, TC-17 | `test_api_endpoints.py` | PASS |
