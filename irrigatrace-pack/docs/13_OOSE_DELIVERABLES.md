# 13 — OOSE deliverables (generated from the code, in `docs/oose/`)

Mini-project rubric (Demo on AI use case, 15 marks): **Understanding 5** (defend all viva questions) · **Demo 5** (working, all steps) · **Punctuality 5** (on the given date; each week late costs marks). Plan to have the demo ready **right after Experiment 4**; the written documents can trail but should be drafted from the same source.

| Exp | Deliverable | CO | What the agent produces (Markdown first; user pastes into the college Word templates in `context/oose-lab-templates.zip`) |
|---|---|---|---|
| 1 | Mini project | 1 | Problem statement, chosen process model (**Incremental/Agile**, justify: P0→P3 tiers), scope, README |
| 2 | SPMP | 2 | WBS from the task board, schedule (Gantt in Mermaid), effort estimate (simple FP or COCOMO-basic with stated assumptions), risk register (doc 00 list + more), team roles, tools, quality plan |
| 3 | SRS | 3 | Intro, overall description, FR/NFR tables (doc 01 IDs), external interfaces (Ollama, Qdrant, Gemini), use-case descriptions, constraints, traceability matrix FR→TC |
| 4 | Tools: JIRA, Trello | 1 | Board setup guide: epics = Tracks A–E, stories = task-board items with FR IDs, sprint plan, screenshot checklist. (Agent can't create the user's JIRA/Trello account; it writes the exact CSV/import and card text) |
| 5 | Behavioral UML | 3 | **Use case** (3 actors), **sequence** (Generate, Review, Replay, Compare), **activity** (review workflow with decision nodes), **state** (lifecycle, doc 02), **collaboration/communication** diagram if template asks |
| 6 | Structural UML | 3 | **Class diagram** (the 14 domain classes, with attributes/methods/relations: composition `IrrigationDecision◆—DecisionSnapshot`, aggregation, dependency on `IrrigationEngine`), **object diagram** (IRR-2026-018 instance), **component** & **deployment** diagrams (web, API, SQLite, Ollama, Qdrant Cloud, Gemini) |
| 7 | SDD | 3 | Architecture (doc 02), data design (doc 05 ERD in Mermaid), interface design (doc 06), UI design (docs 09–10 + screenshots), design patterns used (Strategy, Repository, State, Factory, Observer, Value Object, Facade) with class references |
| 8 | STD | 4 | Test plan, strategy, test case register (doc 12), traceability, execution results from real runs, defect log |
| 9 | Reverse engineering on existing project | 4 | Run the same pipeline on **another existing repo the user names**: recover class diagram, dependency graph, sequence of one key flow, list code smells. (Ask the user which repo when Phase 3 starts; don't guess.) |

## Generation rules
- Diagrams are Mermaid source in `docs/oose/diagrams/*.mmd` + rendered PNG (`mmdc`), consistent palette (white background for print-friendly docs).
- **Class diagram must be generated from or checked against the real code** (script lists classes/attributes via `inspect`/AST and fails if a documented class is missing).
- Every document has a version/date header and the course/project identifiers (KJS-AGR-01; student roll numbers filled by the user).
- Use real run output and real screenshots only. Never fabricate test results.

## Viva prep (`docs/oose/VIVA.md`) — agent writes 25 Q&As; must include
1. Why isn't the engine an ML model? (scope, determinism, reproducibility; the lifecycle is the novelty)
2. Replay vs reproduce — difference and why both exist.
3. How do you guarantee the original recommendation is never overwritten? (triggers + no mutation path + hash chain + tests TC-11/13/15)
4. What does the hash chain prove and not prove? (tamper-evidence in-app; not protection from someone who can rewrite the whole DB)
5. Why is Qdrant a derived index? What if it's down?
6. How do you stop the LLM from inventing facts? (validator, provenance, template fallback)
7. What is flip analysis; what are its limits? (single-variable, interactions)
8. Which design patterns and where? Show class diagram.
9. Process model choice and justification.
10. Which requirements trace to which tests?
11. Outcomes vs. correctness — why you don't claim causality.
12. How would this scale to 25,000 farms? (Postgres, partitioned event table, queue for narration, per-tenant keys)
…plus 13 more from SRS/SDD content.
