# Experiment 8: Software Test Documentation (STD)

**Course:** Object-Oriented Software Engineering (OOSE Lab)  
**Standard:** IEEE Std 829-2008  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Date:** 2026-10-23  
**Course Outcome:** CO4

---

## 1. Test Strategy & Levels
Testing encompasses four rigorous levels:
1. **Unit Testing:** Pure domain calculations (`IrrigationEngine`, FAO-56 thresholds, stage parameters).
2. **Database Trigger Testing:** Direct SQLite constraint verification ensuring append-only triggers reject any UPDATE or DELETE operations.
3. **Integration & Lifecycle Testing:** End-to-end event chains, supervisor reviews, replay reconstruction, and cryptographic hash verification.
4. **AI Output & Grounding Validation:** Regex verification of numbers extracted from LLM text against frozen snapshot domain fields.

---

## 2. Test Case Register & Real Execution Results

| Test ID | Module | Test Function / Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **TC-01** | Domain Engine | `test_engine_low_moisture_triggers_irrigate` | Action = `IRRIGATE`, duration calculated per moisture deficit. | Matches expected FAO-56 duration | **PASS** |
| **TC-02** | Domain Engine | `test_engine_adequate_moisture_skips` | Action = `WAIT`, duration = 0.0 h. | Action = WAIT, duration = 0.0 h | **PASS** |
| **TC-03** | Domain Engine | `test_engine_imminent_rain_suppresses_irrigation` | Rain prob > 70% suppresses duration or forces WAIT. | Suppressed appropriately | **PASS** |
| **TC-04** | Triggers | `test_update_recommendation_fails_trigger` | SQLite trigger `dec_core_immutable` raises `IntegrityError`. | `sqlite3.IntegrityError` raised | **PASS** |
| **TC-05** | Triggers | `test_delete_snapshot_fails_trigger` | SQLite trigger raises error preventing row deletion. | `sqlite3.IntegrityError` raised | **PASS** |
| **TC-06** | Triggers | `test_events_no_update_trigger` | `decision_events` rejects any SQL UPDATE command. | `sqlite3.IntegrityError` raised | **PASS** |
| **TC-07** | Lifecycle | `test_supervisor_modification_lifecycle` | Supervisor override modifies final duration, original AI intact. | Original AI = 2.8, Final = 2.0 | **PASS** |
| **TC-08** | Integrity | `test_hash_chain_genesis_and_verification` | Sequential SHA-256 chain verified with `valid == True`. | `valid: True, broken_seq: None` | **PASS** |
| **TC-09** | Integrity | `test_hash_chain_tamper_detection` | Altered payload in raw DB row is immediately flagged as broken. | `valid: False, broken_seq: 2` | **PASS** |
| **TC-10** | Replay | `test_replay_vs_reproduce` | Replay returns historical facts; reproduce re-executes engine. | Replay = Historical, Diff verified | **PASS** |
| **TC-11** | Compare | `test_flip_analysis` | Identifies single input variables that flip action WAIT -> IRRIGATE. | Identified `soil_moisture_pct` flip | **PASS** |
| **TC-12** | AI Validator | `test_validator_accepts_grounded_numbers` | Validates text containing strictly grounded snapshot numbers. | `valid: True, rejected_numbers: []` | **PASS** |
| **TC-13** | AI Validator | `test_validator_rejects_hallucinated_numbers` | Flags text containing hallucinated numbers (e.g. 99.9%). | `valid: False, rejected: ['99.9']` | **PASS** |
| **TC-14** | REST API | `test_health_endpoint` | `GET /api/health` returns status: "healthy", db: "ok". | HTTP 200 OK | **PASS** |
| **TC-15** | REST API | `test_decision_stream_sse` | `GET /api/decisions/{id}/stream` streams valid SSE events. | Content-Type: `text/event-stream` | **PASS** |

---

## 3. Real Test Execution Summary
```text
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0
rootdir: C:\Study\OOSE\Mini Project
configfile: pytest.ini
collected 24 items

api/tests/test_engine.py ....                                            [ 16%]
api/tests/test_triggers_and_invariants.py .....                          [ 37%]
api/tests/test_lifecycle_and_integrity.py .....                         [ 58%]
api/tests/test_comparison_flips.py ..                                    [ 66%]
api/tests/test_validator.py ....                                         [ 83%]
api/tests/test_api_endpoints.py ....                                     [100%]

============================== 24 passed in 2.14s ==============================
```

---

## 4. Defect Log & Resolutions

| Defect ID | Severity | Description | Resolution | Status |
|---|---|---|---|---|
| **DEF-01** | High | Seeding script attempted to update decision ID, triggering `dec_core_immutable`. | Updated `record_new_decision` to accept explicit `decision_id` at inception. | **Closed** |
| **DEF-02** | High | SQLite autoincrement `seq` is table-wide; hash formula expected `seq_in_chain` per decision. | Updated `IntegrityService` to index and hash using 1-indexed `seq_in_chain`. | **Closed** |
| **DEF-03** | Medium | Outbound IPv4 timeout on Qdrant Cloud connection. | Implemented Invariant 8 graceful fallback to deterministic SQL nearest-neighbor. | **Closed** |
