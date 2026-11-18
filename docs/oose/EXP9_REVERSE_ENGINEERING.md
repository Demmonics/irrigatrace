# Experiment 9: Reverse Engineering Methodology & Pipeline

**Course:** Object-Oriented Software Engineering (OOSE Lab)  
**Project Code:** KJS-AGR-01  
**Project Title:** IrrigaTrace: Audit, Replay, and Traceability Framework for AI Irrigation Decisions  
**Date:** 2026-10-23  
**Course Outcome:** CO4

---

## 1. Purpose & Methodology
Experiment 9 establishes a repeatable automated pipeline to reverse engineer architectural models, dependency graphs, and class structures from an existing software codebase without manual charting:
1. **Abstract Syntax Tree (AST) Parsing:** Extract class declarations, member attributes, methods, and type annotations directly from source files using Python's `ast` module.
2. **Dynamic Inspection:** Use Python `inspect` to recover runtime signature objects, docstrings, and module hierarchies.
3. **UML Model Synthesis:** Transform extracted class structures into standardized Mermaid `.mmd` class diagrams.
4. **Code Smells & Anti-Pattern Analysis:** Identify coupling bottlenecks, god classes, circular dependencies, and missing abstractions.

---

## 2. Reverse Engineering Execution Pipeline
The automated script developed for this pipeline is `scripts/generate_oose_class_diagram.py`.

### 2.1 Execution Against IrrigaTrace Domain Modules
Running the AST parser on `api/irrigatrace`:
- **Discovered Classes:** 22 total classes across domain and services.
- **Identified Core Domain Classes:** `FarmPlot`, `SensorReading`, `WeatherSnapshot`, `Recommendation`, `EngineInputs`, `DecisionSnapshot`, `DecisionExplanation`, `HumanReview`, `DecisionEvent`, `IrrigationDecision`, `OutcomeRecord`, `DecisionComparison`, `StageParam`, `RuleSet`.
- **Relationship Recovery:**
  - Extracted composition: `IrrigationDecision *-- DecisionSnapshot`.
  - Extracted aggregation: `IrrigationDecision o-- HumanReview`.
  - Extracted event stream: `IrrigationDecision *-- DecisionEvent (1..*)`.

### 2.2 Template for User-Nominated External Codebase
When evaluating an external codebase (e.g., a student lab partner's project or open-source repository):
1. Specify target directory: `python scripts/reverse_engineer.py --target <path_to_repo>`.
2. Pipeline outputs:
   - Recovered Class Diagram: `docs/oose/diagrams/reverse_class_diagram.mmd`
   - Module Dependency Graph: `docs/oose/diagrams/dependency_graph.mmd`
   - Code Smell Report: Identifying classes with $> 15$ methods (God Object) or $> 300$ LOC functions.
