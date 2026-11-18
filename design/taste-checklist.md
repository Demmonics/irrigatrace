# Taste & Anti-Slop Checklist (IrrigaTrace)

Distilled from `taste-skill v2` (`design-taste-frontend`) and `docs/09_UI_DESIGN_SYSTEM.md`.
Direction: **"Night Field Observatory"** (adapted from `design/reference/beanmachine-reference.png`).

---

## 1. Anti-Slop Prohibitions (Hard "No")
- [ ] **No stock AI gradients**: No purple-to-pink or rainbow AI gradients; palette is disciplined deep indigo night (`--night-950`, `--night-900`) with soft atmospheric lavender glow and pale-mint accent.
- [ ] **No unstyled shadcn defaults**: Every Radix primitive must be explicitly styled to the design system tokens.
- [ ] **No generic 3-card / 6-card feature grids**: Use varied structural hierarchy (prominent observatory cards, orbit timeline, side-by-side split comparison, data tables).
- [ ] **No emoji icons**: Lucide icons (stroke 1.5) or custom crisp SVGs exclusively.
- [ ] **No monospace everywhere**: Monospace (JetBrains Mono) strictly reserved for decision IDs, cryptographic hash chains, timestamps, and numeric telemetry readouts. Display/UI typography is **Urbanist**.
- [ ] **No placeholder grey rectangles or lorem ipsum**: Real, specific agronomy scenario data (KJS-AGR-01 sugarcane, plot SG-104), actual rule thresholds, and genuine narrative copy.
- [ ] **No resting heavy box-shadows**: Visual depth is achieved through layered surfaces (`--night-800`, `--night-700`), 1px borders (`--line`), and soft indigo/lavender ambient glow (`--glow-soft`).

---

## 2. Invariants & Required Details
- [ ] **Mandatory honest label**: Every data-bearing screen carries the quiet notice: *"Illustrative prototype data"*.
- [ ] **Dual recommendation preservation**: Never hide or overwrite AI recommendation. The AI recommendation (e.g. `2.8 h`) and Human Final decision (e.g. `2.0 h`) must both be displayed side by side.
- [ ] **Provenance tag on all AI text**: Model narratives clearly badge model source (`qwen2.5:3b` / `qwen3:4b` / `gemini` / `template`), validation status, and note that deterministic factors govern decisions.
- [ ] **Status chips with icon + text**: Approved (✓), Modified (✎), Rejected (✕), Pending (◔), Finalized (●).
- [ ] **Floating pill navigation**: 56px height, rounded-full pill (`--r-pill`), centered brand, role selector, status dots indicator, and mint primary action CTA.
- [ ] **Orbit timeline**: Curved or sequenced event stars with scrubbable temporal states (*State at t*).
- [ ] **Reduced motion support**: Full `@media (prefers-reduced-motion)` fallbacks disabling parallax and bouncy springs.
