# 10 — Screens

Global: floating pill nav, role switcher (Supervisor/Admin/Auditor), tiny service-status dots, footer note "Illustrative prototype data — not actual farm data."

## S1 `/` — Landing ("Observatory")
- Hero (full-bleed illustrated scene): H1 **"Every irrigation decision, remembered."** Sub: "IrrigaTrace records, explains and replays how an AI irrigation recommendation was made — who reviewed it, what changed, and what happened next." CTA mint **Launch dashboard**, secondary **Watch a replay** (opens IRR-2026-018 replay).
- Section "The question it answers": the 6 questions a farm manager asks three days later, as a quiet list over a faint plateau illustration.
- Section "What we keep": four icon tiles (like reference's "What we build"): **Inputs snapshot · Original AI output · Human review · Outcome** each with one line.
- Section "The five-step lifecycle" as the orbit timeline drawn statically (Collect → Recommend → Record → Review → Replay & evaluate).
- Section "Built honestly": three statements (replay ≠ reproduce; observations ≠ proof; simulated data).
- Footer: course/project credit line (K J Somaiya School of Engineering · OOSE mini project · KJS-AGR-01).

## S2 `/dashboard` — Decision monitoring
- Header: title + "Demo environment" chip.
- KPI row (4): Total decisions · Awaiting review · Modified by humans · Outcomes recorded (each w/ sparkline; hierarchy: first card larger).
- Filter bar: plot, date range, status, ruleset version, "Overridden only" toggle, search (semantic when text).
- Decision table/list: ID (mono), plot, recommendation ("2.8-hour recommendation"), status chip, AI vs final mini-pair, time. Row click → S3. Pagination.
- Right rail: "Needs review" queue (pending first) + mini plot map (P2).

## S3 `/decisions/[id]` — Case file (tabs: Overview · Replay · Audit · Outcome)
**Overview**: header (ID mono, plot, date, status, integrity seal). AI-vs-Human split numbers. "Inputs at decision time" 4 readouts (moisture, temperature, rain probability, crop stage) + secondary (days since irrigation, forecast mm, sensor age). Explanation: left = deterministic factor list (authoritative), right = plain-English summary with provenance badge; Translate button (EN/HI/KN) for P2. Human intervention card (who, when, reason code + text) — or the Review Panel if pending and role allows. "Similar past decisions" strip (Qdrant). Actions: **Compare with previous decision**, **Reproduce check**.
**Replay**: orbit timeline + scrubber + "State at t" panel; Replay-vs-Reproduce explainer tooltip; Reproduce result card (match/mismatch, diffs).
**Audit**: append-only event table (seq, time, type, actor/role, payload summary, short hash prev→this), integrity result, "Copy full chain" button.
**Outcome**: form (actual duration, moisture after, rainfall, water stress yes/no, crop-health note) → timeline of outcomes; always followed by caveat text: "Observations only — weather, execution and field conditions also affect results."

## S4 `/compare?a=&b=` — Why did it change?
Two decision header cards (A previous, B current, swap button). DiffTable of inputs with delta pills (e.g., −8 pp). Output row (Wait → Irrigate). Fired-rule diff chips. **Flip analysis** card: per changed input, "alone flips action? yes/no" with the engine result. Summary paragraph (template or local model, provenance badge) and warning chip if rulesets differ.

## S5 `/lab` — Lab bench (simulator; Admin/Supervisor)
Left: plot picker + scenario sliders (soil moisture, temperature, rain probability, stage override) with presets ("Dry & hot", "Rain incoming", "Just irrigated"). Right: live preview of engine factors as sliders move (client calls a stateless `POST /engine/preview` — add this endpoint; it writes nothing). Button **Generate decision** → creates a real decision and animates the timeline events arriving via SSE, ending with the review panel. This is the star of the live demo.

## S6 `/plots` and `/plots/[id]`
List with status of latest decision; detail with map polygon (P2), latest readings, decision history sparkline (AI vs final durations), jump to compare for last two decisions.

## S7 `/analytics`
Override rate over time, reason-code breakdown, followed vs modified vs rejected, outcomes observed (water stress yes/no after approved vs modified — with a persistent caveat that this is observational), recommendation distribution by stage. Each chart has a "view data" toggle.

## S8 `/audit` — Integrity
"Verify all chains" → progress → table of decisions with ✓/✗, reason if broken. Explanation card of how the hash chain works (3 short lines + tiny diagram).

## Command palette (⌘K)
Navigate, search decisions (semantic), NL filters ("overridden decisions for SG-104 this week") → shows parsed filter chips before applying.

## States every screen must handle
Loading skeleton · empty · error with retry · degraded service banner (subtle) · read-only (Auditor) with disabled controls and tooltip explaining why.
