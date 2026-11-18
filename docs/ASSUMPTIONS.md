# Assumptions & Decisions Log

Log of all architectural choices, hardware tier determinations, and non-blocking decisions made during the IrrigaTrace build.

---

### [2026-10-23] Hardware & Model Selection (Phase 0)
- **Hardware Profile Detected**:
  - CPU: Intel Core i7-13650HX (14 cores, 20 logical threads)
  - RAM: 24 GB Physical Memory (25.48 GB total)
  - GPU: NVIDIA GeForce RTX 4060 Laptop GPU (8 GB VRAM)
- **Tier Assigned**:
  - High tier (≥ 16 GB RAM, ≥ 8 GB VRAM).
- **Model Decisions**:
  - **Local LLM**: Detected pre-installed `qwen2.5:3b` in Ollama, capable of low-latency structured narration (< 3s). Also initiated background pull of `qwen3:4b`. The `NarrationService` will support `qwen2.5:3b` immediately while `qwen3:4b` downloads.
  - **Embeddings**: `nomic-embed-text` (768 dimensions), started in background via Ollama.
  - **Cloud LLM (Gemini)**: Smoke test confirmed 50 models accessible with the user's `GEMINI_API_KEY`. Selected `gemini-2.5-flash` for multilingual translation (Hindi/Kannada) and `imagen-3.0-generate-002` for build-time hero artwork generation.
  - **Qdrant Vector DB**: Qdrant Cloud connection encountered a network URL timeout during smoke testing (due to external IPv4 routing on local Wi-Fi); per Doc 08 specifications, the system implements an in-memory test runner (`QdrantClient(":memory:")`) and a deterministic SQL nearest-neighbor fallback (`source: "sql-fallback"`) for zero-dependency reliability.

---

### [2026-10-23] Taste-Skill & UI Guidelines (Phase 0)
- **Design Archetype**: "Night Field Observatory" derived from `design/reference/beanmachine-reference.png` and `docs/09_UI_DESIGN_SYSTEM.md`.
- **Taste-Skill Location**: Installed at `.agent/skills/taste-skill` and `.agent/skills/design-taste-frontend`.
- **Anti-Slop Distillation**: Saved to `design/taste-checklist.md`.

---

### [2026-10-23] Design Swap Execution (Stitch Source of Truth)
- **Source of Truth Adopted**:
  - Light mode: Screen `172d95b73fc24a32b28c2b3b0c309116` ("Refined Light Mode Learning Page with Glassy UI").
  - Dark mode: Screen `d024a0f03bb745898fae7c7dd727cf40` ("Updated Learning Page with Dynamic Reviews").
- **Superseded Decisions**:
  - The BeanMachine dark-only archetype and indigo-night palette are superseded by the Stitch glassy editorial language.
  - Typography is updated to `Noto Serif` for display/headlines, `Manrope` for body/labels/controls, and `JetBrains Mono` for technical metrics and IDs.
  - The application now fully supports dual-mode (Light and Dark) with default `prefers-color-scheme`, client toggle in nav, localStorage persistence, and flash-free `data-theme` initialization.
- **Content & Behavioral Invariants**:
  - All IrrigaTrace facts, models, formulas (FAO-56 Dual Kc), seed numbers, and invariants remain 100% intact.
  - Hero case IRR-2026-018 (AI 2.8 h → human override 2.0 h, sensor calibration drift, append-only triggers, cryptographic hash seals) preserved with zero modification.
  - "Reviews" layout component in Stitch converted into a live feed of human-in-the-loop audit review events from seeded database records.

