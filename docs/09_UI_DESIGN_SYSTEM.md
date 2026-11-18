# 09 — UI Design System (Stitch Glassy Editorial)

> **DESIGN SWAP NOTICE (2026-10-23):**  
> The previous BeanMachine indigo-only nocturne reference and Urbanist typography have been **superseded** by the user's Stitch source of truth project (`14433471932359710161`).  
> - **Light Mode:** Screen `172d95b73fc24a32b28c2b3b0c309116` ("Refined Light Mode Learning Page with Glassy UI")  
> - **Dark Mode:** Screen `d024a0f03bb745898fae7c7dd727cf40` ("Updated Learning Page with Dynamic Reviews")  
> All IrrigaTrace domain invariants, content, numbers, formulas, and screens (S1–S8) remain 100% active.

---

## 1. Dual-Mode Architecture & Theme Engine
- **Both Light and Dark modes are fully supported.**
- Defaults to client OS preference via `(prefers-color-scheme: dark)`.
- Client toggle in the navigation header with `localStorage` persistence (`irrigatrace-theme`).
- Anti-flash script in `app/layout.tsx` guarantees zero theme flicker during initial hydration.

---

## 2. Design Tokens (`web/styles/tokens.css`)

```css
:root {
  /* Canvas & Base */
  --bg-page: #f9f9f9;
  --bg-surface: #ffffff;
  --bg-surface-elevated: #f3f3f4;
  --bg-surface-glass: rgba(255, 255, 255, 0.75);
  --bg-surface-glass-elevated: rgba(255, 255, 255, 0.88);

  /* Lines & Borders */
  --border-subtle: rgba(0, 0, 0, 0.08);
  --border-default: #cfc4c5;
  --border-strong: #7e7576;
  --border-glass: rgba(0, 0, 0, 0.08);

  /* Typography Colors */
  --text-primary: #1a1c1c;
  --text-secondary: #5e5e5e;
  --text-tertiary: #7e7576;
  --text-inverse: #ffffff;

  /* Button CTA */
  --btn-primary-bg: #000000;
  --btn-primary-text: #ffffff;
  --btn-primary-hover: #222222;
  --btn-secondary-border: #cfc4c5;
  --btn-secondary-hover: rgba(0, 0, 0, 0.04);

  /* Status Tokens */
  --status-ok: #15803d;
  --status-ok-bg: rgba(21, 128, 61, 0.10);
  --status-warn: #b45309;
  --status-warn-bg: rgba(180, 83, 9, 0.10);
  --status-bad: #b91c1c;
  --status-bad-bg: rgba(185, 28, 28, 0.10);
  --status-info: #4338ca;
  --status-info-bg: rgba(67, 56, 202, 0.10);

  /* Glass Effects */
  --glass-blur: 18px;
  --glass-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.06), 0 0 1px 1px rgba(255, 255, 255, 0.8) inset;

  /* Typography Scales */
  --font-serif: 'Noto Serif', serif;
  --font-sans: 'Manrope', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Radii */
  --r-sm: 8px;
  --r-md: 12px;
  --r-lg: 20px;
  --r-pill: 9999px;
}

[data-theme="dark"],
.dark {
  /* Canvas & Base */
  --bg-page: #0a0a0a;
  --bg-surface: #121212;
  --bg-surface-elevated: #1a1a1c;
  --bg-surface-glass: rgba(28, 28, 30, 0.82);
  --bg-surface-glass-elevated: rgba(36, 36, 38, 0.90);

  /* Lines & Borders */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-default: #262626;
  --border-strong: #404040;
  --border-glass: rgba(255, 255, 255, 0.10);

  /* Typography Colors */
  --text-primary: #ffffff;
  --text-secondary: #c7c6c6;
  --text-tertiary: #71717a;
  --text-inverse: #1a1c1c;

  /* Button CTA */
  --btn-primary-bg: #ffffff;
  --btn-primary-text: #000000;
  --btn-primary-hover: #e5e5e5;
  --btn-secondary-border: #333333;
  --btn-secondary-hover: rgba(255, 255, 255, 0.06);

  /* Status Tokens */
  --status-ok: #4ade80;
  --status-ok-bg: rgba(74, 222, 128, 0.12);
  --status-warn: #fbbf24;
  --status-warn-bg: rgba(251, 191, 36, 0.12);
  --status-bad: #f87171;
  --status-bad-bg: rgba(248, 113, 113, 0.12);
  --status-info: #818cf8;
  --status-info-bg: rgba(129, 140, 248, 0.12);

  /* Glass Effects */
  --glass-blur: 20px;
  --glass-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.50), 0 0 1px 1px rgba(255, 255, 255, 0.06) inset;
}
```

---

## 3. Typography & Editorial Hierarchies
- **Headlines & Display:** **Noto Serif** (300/400 light, italic accents). High-contrast editorial pacing.
- **Body & Controls:** **Manrope** (400/500/600). Clean geometric legibility with wide tracking on small kickers (`letterSpacing: 0.2em`, uppercase).
- **Technical & Audit:** **JetBrains Mono** for all IDs (`IRR-2026-018`), timestamps, hash signatures, and telemetry readouts.

---

## 4. Glass Effect & Surfaces Specification
- **Light Mode Glass:** Translucent warm white `rgba(255, 255, 255, 0.75)` with `backdrop-filter: blur(18px)` and subtle hairline border `rgba(0, 0, 0, 0.08)`. Solid fallback `#ffffff` (98%).
- **Dark Mode Glass:** Translucent obsidian `rgba(28, 28, 30, 0.82)` with `backdrop-filter: blur(20px)` and hairline border `rgba(255, 255, 255, 0.08)`. Solid fallback `#141416` (98%).
- **WCAG AA Compliance:** Numerically verified across all surfaces (> 5:1 for secondary text, > 15:1 for primary text).

---

## 5. Signature IrrigaTrace Components
1. **AI vs Human Split Number:** Side-by-side display of initial FAO-56 duration vs final approved duration, connected by an agronomist override delta pill.
2. **Orbit Timeline & Scrubber:** Interactive horizontal sequence track that reconstructs historical "State at t" at any point in the lifecycle.
3. **Integrity Seal:** SHA-256 validation seal with interactive live recalculation.
4. **Liquid Orb Indicator:** Stitch signature CSS animation indicating live engine activity.
5. **Dynamic Human Review Stream:** Real-time feed of supervisor approvals, modifications, and reasons from seeded database records.
