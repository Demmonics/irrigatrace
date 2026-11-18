# Experiment 8: Software Test Documentation (STD) (Corrected)

**Course:** Object-Oriented Software Engineering (OOSE Lab, Semester 5)  
**Standard:** IEEE Std 829-2008  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Institution:** K. J. Somaiya College of Engineering (KJSCE), Somaiya Vidyavihar University  
**Student:** Yoosha Abbas (Roll No.: 16014224101, Batch: B2)  
**Date:** 2026-10-23  
**Course Outcome:** CO4  

---

## 1. Test Strategy & Verification Levels
Testing encompasses four comprehensive tiers:
1. **Unit Testing:** Pure domain calculations (`IrrigationEngine`, FAO-56 thresholds, stage parameters).
2. **Database Trigger Testing:** Direct SQLite constraint verification ensuring append-only triggers reject any `UPDATE` or `DELETE` operations.
3. **Integration & Lifecycle Testing:** End-to-end event chains, supervisor reviews, replay reconstruction, and cryptographic hash verification.
4. **AI Output & Grounding Validation:** Regex verification of numbers extracted from LLM text against frozen snapshot domain fields.

*(Note: In accordance with faculty review instructions, legacy references to the standalone 49-line prototype script `irrigation_advisor.py` and obsolete test IDs have been completely replaced with the authentic production test suite).*

---

## 2. Authentic Test Execution Output
The entire automated test suite was executed against the production codebase:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python313\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\Study\OOSE\Mini Project
configfile: pytest.ini
plugins: anyio-4.11.0, hypothesis-6.170.8, langsmith-0.11.1, asyncio-1.4.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 24 items

api/tests/integration/test_api_endpoints.py::test_api_health_endpoint PASSED           [  4%]
api/tests/integration/test_api_endpoints.py::test_api_plots_and_preview PASSED         [  8%]
api/tests/integration/test_api_endpoints.py::test_tc16_auditor_permission_forbidden PASSED [ 12%]
api/tests/integration/test_api_endpoints.py::test_case_file_and_reproduce PASSED       [ 16%]
api/tests/integration/test_api_endpoints.py::test_tc24_similar_decisions_fallback PASSED [ 20%]
api/tests/integration/test_api_endpoints.py::test_compare_and_audit PASSED             [ 25%]
api/tests/unit/test_comparison_flips.py::test_tc20_and_tc21_comparison_flip_analysis PASSED [ 29%]
api/tests/unit/test_engine.py::test_worked_example_1_irrigate PASSED                    [ 33%]
api/tests/unit/test_engine.py::test_worked_example_2_defer_rain PASSED                  [ 37%]
api/tests/unit/test_engine.py::test_wait_when_moisture_sufficient PASSED                [ 41%]
api/tests/unit/test_lifecycle_and_integrity.py::test_tc08_generate_decision_atomic PASSED [ 45%]
api/tests/unit/test_lifecycle_and_integrity.py::test_tc09_approve_lifecycle PASSED    [ 50%]
api/tests/unit/test_lifecycle_and_integrity.py::test_tc10_and_tc11_modify_lifecycle PASSED [ 54%]
api/tests/unit/test_lifecycle_and_integrity.py::test_tc12_reject_lifecycle PASSED     [ 58%]
api/tests/unit/test_lifecycle_and_integrity.py::test_tc15_tamper_detection PASSED     [ 62%]
api/tests/unit/test_lifecycle_and_integrity.py::test_tc18_reproduce_check PASSED       [ 66%]
api/tests/unit/test_lifecycle_and_integrity.py::test_tc27_replay_state_at PASSED        [ 70%]
api/tests/unit/test_triggers_and_invariants.py::test_tc13_events_immutable PASSED      [ 75%]
api/tests/unit/test_triggers_and_invariants.py::test_tc13_snapshots_immutable PASSED   [ 79%]
api/tests/unit/test_triggers_and_invariants.py::test_tc13_reviews_immutable PASSED     [ 83%]
api/tests/unit/test_triggers_and_invariants.py::test_tc14_decision_core_immutable PASSED [ 87%]
api/tests/unit/test_validator.py::test_tc22_number_consistency_validator_pass PASSED   [ 91%]
api/tests/unit/test_validator.py::test_tc22_number_consistency_validator_injected_number PASSED [ 95%]
api/tests/unit/test_validator.py::test_tc22_number_consistency_validator_action_contradiction PASSED [100%]

============================= 24 passed in 30.27s =============================
```

---

## 3. Test Case Specification Register (24 Test Cases)

| TC ID | Test Function Name | Req ID | UC ID | Class / Method | Inputs & Scenarios | Expected Result | Actual Result Observed | Status |
|---|---|---|---|---|---|---|---|---|
| **TC-01** | `test_worked_example_1_irrigate` | FR-01 | UC-02 | `IrrigationEngine.recommend` | Moisture 21%, temp 33°C, rain 12%, rate 14 mm/h. | Action `IRRIGATE`, duration `2.8h`, confidence ≈ 0.84. | Matches expected FAO-56 duration | **PASS** |
| **TC-02** | `test_worked_example_2_defer_rain` | FR-01 | UC-02 | `IrrigationEngine.recommend` | Moisture 29%, temp 29°C, rain prob 72%. | Action `DEFER_RAIN`, duration `0.0h`. | Action `DEFER_RAIN`, duration 0.0h | **PASS** |
| **TC-03** | `test_wait_when_moisture_sufficient` | FR-01 | UC-02 | `IrrigationEngine.recommend` | Moisture 28% in Tillering (trigger 23%), rain 10%. | Action `WAIT`, duration `0.0h`. | Action `WAIT`, duration 0.0h | **PASS** |
| **TC-04** | `test_tc13_events_immutable` | FR-05 | UC-09 | Trigger `events_no_update` | Execute SQL `UPDATE` / `DELETE` on `decision_events`. | SQLite raises `IntegrityError: decision_events is append-only`. | `sqlite3.IntegrityError` raised | **PASS** |
| **TC-05** | `test_tc13_snapshots_immutable` | FR-02 | UC-03 | Trigger `snap_no_update` | Execute SQL `UPDATE` / `DELETE` on `decision_snapshots`. | SQLite raises `IntegrityError: snapshots are immutable`. | `sqlite3.IntegrityError` raised | **PASS** |
| **TC-06** | `test_tc13_reviews_immutable` | FR-04 | UC-04 | Trigger `rev_no_update` | Execute SQL `UPDATE` / `DELETE` on `human_reviews`. | SQLite raises `IntegrityError: reviews are immutable`. | `sqlite3.IntegrityError` raised | **PASS** |
| **TC-07** | `test_tc14_decision_core_immutable` | FR-03 | UC-03 | Trigger `dec_core_immutable` | Execute SQL `UPDATE` on original recommendation duration. | SQLite raises `IntegrityError: original recommendation is immutable`. | `sqlite3.IntegrityError` raised | **PASS** |
| **TC-08** | `test_tc08_generate_decision_atomic` | FR-01 | UC-01 | `DecisionRecorder.record_decision` | Valid telemetry inputs for plot SG-104. | Atomic commit of decision, snapshot, and event blocks. | Atomic transaction committed | **PASS** |
| **TC-09** | `test_tc09_approve_lifecycle` | FR-04 | UC-04 | `ReviewService.submit_review` | Decision in `PENDING_REVIEW`, action `APPROVE`. | Status transitions to `FINALIZED`; final duration equals original AI duration. | Status `FINALIZED`, AI duration kept | **PASS** |
| **TC-10** | `test_tc10_and_tc11_modify_lifecycle` | FR-04 | UC-04 | `ReviewService.submit_review` | Action `MODIFY`, duration `2.0h`, reason `R-POWER`. | Status becomes `MODIFIED`; original AI recommendation intact. | Original AI 2.8h vs Final 2.0h | **PASS** |
| **TC-11** | `test_tc12_reject_lifecycle` | FR-04 | UC-04 | `ReviewService.submit_review` | Action `REJECT`, duration `0.0h`, reason `R-WEATHER`. | Status becomes `REJECTED`; final duration = `0.0h`. | Status `REJECTED`, duration 0.0h | **PASS** |
| **TC-12** | `test_tc15_tamper_detection` | FR-05 | UC-09 | `IntegrityService.verify_chain` | Corrupt raw payload byte in event sequence 2 in database. | Verification routine flags `valid: False, broken_seq: 2`. | `valid: False, broken_seq: 2` reported | **PASS** |
| **TC-13** | `test_tc18_reproduce_check` | FR-07 | UC-06 | `DecisionReplayService.reproduce` | Snapshot inputs re-evaluated against identical ruleset. | Re-execution yields exact match (`match: True`). | `match: True` confirmed | **PASS** |
| **TC-14** | `test_tc27_replay_state_at` | FR-06 | UC-05 | `DecisionReplayService.state_at` | Request state at historical timestamp $t$ prior to override. | Reconstructs state with status `PENDING_REVIEW`. | Historical state matched | **PASS** |
| **TC-15** | `test_tc20_and_tc21_comparison_flip_analysis` | FR-08 | UC-07 | `ComparisonService.compare` | Compare decision A (`WAIT`) vs B (`IRRIGATE`). | Identifies `soil_moisture_pct` as the single flip variable. | Single-variable flip detected | **PASS** |
| **TC-16** | `test_tc22_number_consistency_validator_pass` | FR-09 | UC-11 | `NumberConsistencyValidator` | Narration text contains only grounded numbers: `21.0%`, `33.0°C`. | Validator returns `valid: True, rejected_numbers: []`. | `valid: True` | **PASS** |
| **TC-17** | `test_tc22_number_consistency_validator_injected_number` | FR-09 | UC-11 | `NumberConsistencyValidator` | Text contains hallucinated number: `"Irrigate 99.9 hours"`. | Validator flags `valid: False, rejected: ['99.9']`. | `valid: False, rejected: ['99.9']` | **PASS** |
| **TC-18** | `test_tc22_number_consistency_validator_action_contradiction` | FR-09 | UC-11 | `NumberConsistencyValidator` | Action is `WAIT`, text contains `"Irrigate now"`. | Validator flags `ACTION_CONTRADICTION`. | `valid: False, contradiction flagged` | **PASS** |
| **TC-19** | `test_api_health_endpoint` | NFR-01 | All | `FastAPI Router (/api/health)` | API running with active database pool. | Returns HTTP 200 with `status: healthy, db: ok`. | HTTP 200 OK | **PASS** |
| **TC-20** | `test_api_plots_and_preview` | FR-11 | UC-08 | `FastAPI Router (/api/engine/preview)` | Stateless preview request with environmental slider inputs. | Returns HTTP 200 with computed factors; zero database writes. | HTTP 200 OK, zero DB mutations | **PASS** |
| **TC-21** | `test_tc16_auditor_permission_forbidden` | NFR-02 | UC-04 | FastAPI Auth Dependency | Auditor role attempts `POST /api/decisions/{id}/review`. | Returns HTTP 403 Forbidden with permission error. | HTTP 403 Forbidden | **PASS** |
| **TC-22** | `test_case_file_and_reproduce` | FR-06 | UC-05 | `FastAPI Router (/decisions/{id})` | Query case file and execute reproduce verification. | Returns HTTP 200 with complete 4-tab case-file data. | HTTP 200 OK | **PASS** |
| **TC-23** | `test_tc24_similar_decisions_fallback` | NFR-03 | UC-07 | `SimilaritySearchService` | Simulate network timeout on external Qdrant Cloud. | Gracefully degrades to deterministic SQLite query without error. | HTTP 200 OK via SQLite fallback | **PASS** |
| **TC-24** | `test_compare_and_audit` | FR-08 | UC-07 | `FastAPI Router (/compare & /audit)` | Query decision diff and verify full ledger cryptographic proof. | Returns HTTP 200 with verified hash chains and parameter diffs. | HTTP 200 OK | **PASS** |

---

## 4. Defect Log & Resolutions

| Defect ID | Severity | Description | Resolution | Status |
|---|---|---|---|---|
| **DEF-01** | High | Seeding script attempted to update decision ID, triggering `dec_core_immutable`. | Updated `record_decision` to accept explicit `decision_id` at inception. | **Closed** |
| **DEF-02** | High | SQLite autoincrement `seq` is table-wide; hash formula expected local `seq_in_chain`. | Updated `IntegrityService` to index and hash using 1-indexed `seq_in_chain` per decision. | **Closed** |
| **DEF-03** | Medium | Outbound IPv4 timeout on Qdrant Cloud connection. | Implemented Invariant 8 graceful fallback to deterministic SQL nearest-neighbor. | **Closed** |
