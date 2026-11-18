# 09 — UI Design System

**Reference:** `design/reference/beanmachine-reference.png` — deep indigo night sky, soft painterly illustration (ringed planet, pale lavender mountains, tiny towers and ships), centered airy hero, pale-mint pill CTA, thin floating nav pill, small line icons in rounded indigo tiles, lots of empty space.

**IrrigaTrace concept — "Night Field Observatory":** the same indigo night world, retold for agriculture. Hero art: a moonlit sugarcane plateau with terraced rows, a slim irrigation tower and pump house, a ringed planet low on the horizon, a few tiny survey drones. Decisions are "stars"; a decision's life is an **orbit trail** (timeline). Calm, precise, trustworthy — an audit tool that feels like an observatory.

Mood words: nocturnal, quiet, precise, painterly, spacious. **Not** neon cyber, not glassy-gradient SaaS, not dashboard-grey.

## Tokens (`web/styles/tokens.css`) — dark theme is the only theme
```css
:root {
  /* surfaces */
  --night-950: #06052A;   /* page deep */
  --night-900: #0B0A3F;   /* page base (matches reference top) */
  --night-800: #14116B;   /* raised surface */
  --night-700: #1E1A94;   /* card hover / borders strong */
  --indigo-600: #2B22C2;  /* reference mid-field indigo */
  --indigo-500: #4B40E6;  /* primary accent fills, icon tiles */
  --lavender-400: #8F86F5;/* secondary accent, links, mountains */
  --lavender-200: #C9C4FF;/* soft text accent, glows */
  --mist-50: #F3F1FF;     /* primary text */
  --mist-300: #B2AEEA;    /* secondary text (AA on night-900) */
  --mist-500: #7C78C4;    /* tertiary text / hints (large text only) */
  --mint-300: #C8F5C9;    /* primary CTA bg (reference button) */
  --mint-900: #0C2A1A;    /* text on mint */
  /* status */
  --ok: #7CE7A0;  --warn: #FFC76B;  --bad: #FF7A90;  --info: #8F86F5;
  /* lines & glow */
  --line: rgba(201,196,255,0.14); --line-strong: rgba(201,196,255,0.28);
  --glow-soft: 0 0 80px rgba(75,64,230,0.35);
  --glow-focus: 0 0 0 3px rgba(143,134,245,0.55);
  /* radii & space */
  --r-sm: 10px; --r-md: 16px; --r-lg: 24px; --r-pill: 999px;
  --space: 4px;   /* scale: 4 8 12 16 24 32 48 64 96 */
}
```
Status chips pair color with an icon + text (never color alone): Approved ✓ `--ok`, Modified ✎ `--warn`, Rejected ✕ `--bad`, Pending ◔ `--info`, Finalized ● `--lavender-200`. (Use Lucide icons, not these glyphs.)

## Typography
- Display/UI: **Urbanist** (400/500/600). H1 clamp(40px, 5vw, 64px)/1.05, weight 500, letter-spacing −0.02em. H2 32/1.15. H3 20/1.3 weight 600. Body 16/1.6 (`--mist-300` for secondary). Small 13/1.5.
- Mono: **JetBrains Mono** 13–14px for decision IDs, hashes, timestamps, numeric readouts. Hero numbers (KPIs, durations) use Urbanist 600 at 56–72px with tabular figures.
- Max line length 68ch. Sentence case everywhere.

## Layout & shape
- 12-col grid, 1200px content max, 24px gutters; marketing sections 96px vertical rhythm; app pages 32px.
- Cards: `--night-800` at 60% over a faint noise texture, 1px `--line` border, radius 24, no heavy drop shadows — depth from glow and layering.
- Floating pill nav (like the reference): 56px tall, radius 999, `--night-800/80` with backdrop blur 12px, centered logo, left nav links, right: role switcher + status dots + primary "Launch dashboard" (mint). Collapses to a sheet on mobile.
- Illustration is a **layered parallax scene** (sky/stars, planet, far mountains, plateau, foreground towers) as separate transparent WebP layers; subtle 8–24px parallax on scroll, slow star twinkle. Disable under `prefers-reduced-motion`.
- Subtle painterly noise overlay (3% opacity) on page background to avoid flat gradient banding.

## Components (restyle shadcn/Radix; each needs hover, focus, disabled, loading, empty, error states)
Button (primary mint pill / secondary outline lavender / ghost), Chip (status), KPI card (big number + label + tiny sparkline), DecisionRow, FilterBar (segmented controls + popover pickers), Tabs (underline-glow), Timeline (orbit trail, see below), Scrubber, DiffTable (changed rows glow lavender; delta pills), FactorList, ProvenanceBadge, ReviewPanel (segmented Approve/Modify/Reject, duration stepper 0.1 h, reason select + textarea), IntegrityBadge, Toast, CommandPalette (⌘K), EmptyState (small illustration), Skeletons (night shimmer).

### Signature elements
1. **Orbit timeline**: a thin curved path with event "stars" — size by importance, ring when human-initiated, mint when finalized. Hover shows exact timestamp (mono) and payload summary; click pins a detail card. Below: a **scrubber** that sets time `t`; the right panel shows "State at t" (what inputs/recommendation/review existed then; later items dimmed and labeled "not yet happened").
2. **AI vs Human split number**: two large numerals side by side: "AI recommended 2.8 h" and "Final 2.0 h", connected by a small arc labelled "−0.8 h · modified by Supervisor". Both always visible.
3. **Integrity seal**: small circular badge with chain-link motif; mint when valid; click opens the verification detail with recomputed hash short IDs.
4. **Diff glow**: in Compare, changed input rows pulse once on load; unchanged rows stay quiet.

## Motion
Durations 200–400ms, easing `cubic-bezier(.2,.8,.2,1)`. Page transitions fade+8px rise. List items stagger 30ms (max 8). Timeline events animate in sequence during live generation (SSE). Respect `prefers-reduced-motion` (replace with fades only).

## Content rules
- Real, specific copy (use the spec's scenario). No lorem ipsum. Honest labels ("Illustrative prototype data").
- Numbers: units adjacent, mono/tabular. Dates `24 Oct 2026, 10:05`.
- Empty states explain what will appear and offer one action.

## Accessibility
Contrast AA (`--mist-300` on `--night-900` ≥ 7:1). Visible focus ring `--glow-focus`. All interactive elements keyboard reachable; timeline stars are buttons with aria-labels; charts have a data-table toggle; touch targets ≥ 44px.

## Anti-patterns (hard no)
Default shadcn look, stock purple→pink gradients, glassmorphism everywhere, emoji as icons, centered-everything page bodies, 6 identical stat cards in a row with no hierarchy, gray placeholder rectangles, fake logos/testimonials, inconsistent radii, text over busy art without a scrim.

## Responsive
Design for 1440 first, verify 1024, 768, 390. On mobile: the timeline becomes vertical; compare becomes stacked cards; tables become cards.
