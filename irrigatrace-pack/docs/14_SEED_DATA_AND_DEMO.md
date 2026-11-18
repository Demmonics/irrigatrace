# 14 — Seed data & 7-minute demo script

## Seed (idempotent `make seed`; all marked SIMULATED)
- Users: `u-sup1` Supervisor "Anita R.", `u-sup2` "Mahesh K.", `u-admin` Admin "Demo Admin", `u-aud` Auditor "Farm Manager" (display names are fictional).
- Plots (synthetic polygons near Sameerwadi, Karnataka; label "synthetic"): SG-104, SG-107, SG-112, SG-118, SG-121, SG-125 (mixed soils, planting dates producing different stages; SG-104 in Grand Growth, rate 14 mm/h).
- **Hero scenario** reproduced exactly (via recorder with injected clock, 24 Oct 2026):
  - 09:41:58 sensor (moisture 21%, temp 33°C) · 09:42:01 weather (rain 12%) · 09:42:07 recommendation IRRIGATE 2.8 h, rules-v1.4.2, confidence ≈ 0.84 · 10:03:21 review opened · 10:05:47 MODIFIED → 2.0 h, reason `LOCAL_FIELD_CONDITIONS`, text "Local field conditions suggested a shorter irrigation duration." · 10:06 finalized · next day action recorded (actual 2.0 h) · outcome recorded.
  - Decision id `IRR-2026-018`. Its previous decision for SG-104 (`IRR-2026-014`): moisture 29%, temp 29°C, rain 72%, Grand Growth → DEFER_RAIN.
- Bulk: ≈ 125 more decisions over 6 weeks across plots (target dashboard feel: ~128 total, ~12 pending, ~27 modified, ~83 outcomes) with varied reasons, a few rejections, realistic time gaps. Numbers are whatever the generator produces — **dashboard KPIs must be computed from data, not hard-coded**.
- Rebuild Qdrant after seeding (`scripts/reindex_qdrant.py`).

## Demo script (≈7 min, rehearse; the Playwright e2e mirrors it)
1. **Landing (30 s)** — read H1; click Launch dashboard.
2. **Dashboard (45 s)** — KPIs, filter "Overridden only", point to IRR-2026-018.
3. **Case file (90 s)** — AI 2.8 h vs final 2 h; inputs; factor list; local-model summary + provenance; supervisor reason. "The original is never overwritten."
4. **Replay (90 s)** — scrub through 09:41 → 10:05; show "state at 10:00" (no review yet). Click **Reproduce check** → match. Explain replay ≠ reproduce.
5. **Compare (60 s)** — IRR-2026-014 vs 018: deltas, flip analysis (rain alone flips; moisture alone doesn't).
6. **Lab bench live (90 s)** — SG-107, drag sliders to "dry & hot", Generate → events arrive live → review as Supervisor → Modify with reason.
7. **Audit & outcome (45 s)** — Audit tab hash chain, Verify all → all valid; record an outcome; read the caveat.
8. **Close (15 s)** — "Not a better irrigation algorithm — a trustworthy lifecycle around any AI decision."

## Fallback plan (demo day)
Pre-run `make demo` 10 min before; `/api/health` should show DB up. If Ollama is slow, narrative shows template (already labeled) — keep going. If internet is down, Qdrant uses SQL fallback; translation button hidden. Keep screenshots + a 2-min screen recording in `docs/oose/demo-backup/`.
