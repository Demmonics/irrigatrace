# Experiment 4: Project Management Tools (JIRA & Trello Setup)

**Course:** Object-Oriented Software Engineering (OOSE Lab)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Date:** 2026-10-23  
**Course Outcome:** CO1

---

## 1. Board Structure & Architecture
The project utilizes an Agile Kanban/Scrum hybrid board with 5 Epics corresponding to project tracks:
- **EPIC-1: Track A — Backend & Core Invariants**
- **EPIC-2: Track B — AI Services & Validation**
- **EPIC-3: Track C — Stitch Design & Observatory Theme**
- **EPIC-4: Track D — Frontend Web Application**
- **EPIC-5: Track E — OOSE Academic Deliverables**

Board Workflow Columns:
`Backlog` $\to$ `Ready for Sprint` $\to$ `In Progress` $\to$ `Review / Verification` $\to$ `Done (Signed Off)`

---

## 2. Sprint Cadence & Allocation
- **Sprint 1 (Foundations & Invariants):** DB triggers, pure engine, repository layer, hardware profiling.
- **Sprint 2 (Audit Services & Intelligence):** Hash chain, Replay/Reproduce, Ollama narration strategy, number validator.
- **Sprint 3 (Observatory UI & Simulator):** Stitch screens, Next.js frontend, orbit timeline, Lab Bench simulator.
- **Sprint 4 (Integration & Demo):** 7-minute demo script, OOSE lab documentation, Viva defense.

---

## 3. JIRA / Trello CSV Import Template
The following structured CSV data can be imported directly into JIRA or Trello boards:

```csv
Issue Key,Issue Type,Summary,Epic Link,Priority,Story Points,Status
IRR-101,Story,Implement pure FAO-56 irrigation recommendation engine,EPIC-1,Highest,5,Done
IRR-102,Story,Enforce SQLite WAL mode and append-only database triggers,EPIC-1,Highest,8,Done
IRR-103,Story,Implement atomic DecisionRecorder and hash chain genesis,EPIC-1,Highest,5,Done
IRR-104,Story,Develop ReviewService with immutable AI recommendation preservation,EPIC-1,High,5,Done
IRR-105,Story,Build ReplayService (state_at) and Reproduce check,EPIC-1,High,5,Done
IRR-106,Story,Implement ComparisonService with single-variable flip analysis,EPIC-1,Medium,5,Done
IRR-107,Story,Configure Ollama local LLM narration with fallback strategy,EPIC-2,High,5,Done
IRR-108,Story,Implement NumberConsistencyValidator regex grounding engine,EPIC-2,Highest,8,Done
IRR-109,Story,Setup Qdrant vector index with graceful SQL fallback,EPIC-2,Medium,5,Done
IRR-110,Story,Create Stitch design system and self-approve 8 screens per rubric,EPIC-3,Highest,8,Done
IRR-111,Story,Scaffold Next.js App Router and tokens.css design system,EPIC-4,High,5,Done
IRR-112,Story,Build Case File (S3) with AI-vs-Human split number and orbit scrubber,EPIC-4,Highest,8,Done
IRR-113,Story,Build Lab Bench (S5) simulator with live SSE event animation,EPIC-4,High,5,Done
IRR-114,Story,Generate complete OOSE documentation and Viva defense guide,EPIC-5,High,5,Done
```

---

## 4. Trello Card Checklist Structure
For each user story card in Trello, the following Quality Assurance checklist is enforced:
1. **Definition of Ready (DoR):** SRS Functional Requirement ID linked; acceptance criteria defined; input/output schema verified.
2. **Implementation:** Code committed to git; typed Pydantic models; docstrings preserved.
3. **Verification:** Automated unit test written; Pytest passes with 0 failures; invariant triggers checked.
4. **Definition of Done (DoD):** Task board ticked in `docs/15_TASK_BOARD.md` with verifiable evidence.
