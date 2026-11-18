# 11 — Stitch + Taste-skill design workflow (self-approving)

## Setup (Phase 0, before Track C)
1. Confirm the **Stitch MCP** tools are available; list them and note names/params in `design/STITCH_TOOLS.md`. Use whatever the server exposes (create project, generate screen, edit screen, fetch HTML/screenshot). Do not guess tool names.
2. Install **taste-skill** into `.agent/skills/taste-skill/` (the user provides the repo URL/path; if missing, ask once, otherwise continue other tracks). Read its `SKILL.md` fully and write a ≤ 40-line distilled `design/taste-checklist.md`.
3. Place the reference image at `design/reference/beanmachine-reference.png` (already there). Describe it in words in `design/reference/NOTES.md` so the design can be re-created from text if the image is unavailable.

## Precedence when rules conflict
1. User's reference image + `09_UI_DESIGN_SYSTEM.md` → palette, mood, illustration style, shape language.
2. taste-skill → typography details, spacing, hierarchy, motion, anti-"AI-slop" rules.
3. shadcn/Radix defaults → behavior only, never look.

## Generation loop (per screen S1…S8, in this order: S1, S2, S3, S4, S5, then S6–S8)
```
for screen in screens:
  1. Build the Stitch prompt from: design tokens (hex), type, layout from 10_SCREENS.md, real copy (no lorem), mood words, reference image attached, and the anti-pattern list.
  2. Generate in Stitch. Export HTML/Tailwind + screenshot → design/stitch-exports/<screen>/vN/
  3. SELF-REVIEW using the rubric below. Score every criterion 0-10. Write the scores and 3 concrete defects to design/approved/approvals.md.
  4. If total < 85/100 or any criterion < 7 → edit the screen in Stitch with a targeted fix list (max 3 fixes per iteration). Max 3 iterations per screen.
  5. If still < 85 after 3 iterations → pick the best version, record "approved with known gaps", list the gaps as polish tasks, and MOVE ON. Never loop forever.
  6. On approval copy final export to design/approved/<screen>/ and add the screenshot.
```
After all screens: run a **consistency pass** (nav, spacing scale, radii, status chips, button hierarchy identical across screens) and extract the shared tokens into `web/styles/tokens.css` exactly as in doc 09.

## Self-review rubric (100 pts)
| Criterion | Pts | Pass looks like |
|---|---|---|
| Fidelity to reference mood (indigo night, painterly, airy) | 15 | A viewer would say "same world" as the reference |
| Hierarchy & focus (one clear primary per screen) | 15 | Squint test: the AI-vs-final numbers / main KPI dominate |
| Typography (Urbanist/Mono pairing, scale, tabular numbers) | 10 | No default-font feel, consistent scale |
| Color & contrast (tokens only, AA) | 10 | No off-palette colors; status never by color alone |
| Spacing & layout rhythm | 10 | Consistent 4/8 scale, no cramped clusters |
| Content realism & honesty labels | 10 | Real scenario copy, "illustrative data" label present |
| Signature elements present (orbit timeline, split numbers, seal, diff glow) where relevant | 10 | Implemented, not just mentioned |
| Component states & responsiveness (390/768/1440) | 10 | Hover/focus/empty/loading covered |
| Anti-pattern absence (doc 09 list + taste-skill) | 10 | Zero violations |

## Stitch prompt skeleton (fill per screen)
```
Design a {screen name} for "IrrigaTrace", an audit-and-replay tool for AI irrigation recommendations.
Style: deep indigo night world, painterly layered illustration (ringed planet low on horizon, pale lavender mountains, moonlit sugarcane plateau, slim towers), airy generous spacing, floating pill navigation, pale-mint pill primary buttons. Reference attached.
Palette (use exactly): #06052A #0B0A3F #14116B #1E1A94 #2B22C2 #4B40E6 #8F86F5 #C9C4FF #F3F1FF #B2AEEA #C8F5C9 and status #7CE7A0 #FFC76B #FF7A90.
Type: Urbanist for UI/headlines, JetBrains Mono for IDs, hashes, timestamps; large tabular numerals for key figures.
Layout & content: {paste the screen section from 10_SCREENS.md, including the exact copy and numbers}.
Must include: {signature elements}. Must avoid: stock gradients, emoji icons, default component-library look, lorem ipsum, gray placeholder boxes.
Desktop 1440 first; also produce a 390px mobile variant.
```

## Illustration assets (Gemini image model, build-time)
Generate transparent-background layers, 2400×1400 landscape, flat painterly gouache texture, limited indigo/lavender palette, no text, no people, no logos:
1. `sky-stars` — deep indigo gradient sky with sparse tiny stars and soft dust clouds.
2. `planet` — large ringed planet, dark navy sphere with lighter blotches, thin ring arcs.
3. `far-mountains` — pale lavender snow-capped ridge with soft haze.
4. `plateau` — mid-ground terraced sugarcane rows in indigo tones, a slim irrigation tower, small pump house.
5. `foreground-towers` — crystalline pale towers and tiny survey drones on a floating rock shelf (right-bottom, like the reference).
Convert to WebP, ≤ 250 KB each; store prompts + model + date in `design/approved/art-manifest.md`. If generation fails or looks off-style after 3 tries, fall back to hand-built layered SVG with the same palette — never ship stock photos.

## Converting Stitch output to the real app
Treat Stitch HTML as a *visual spec*, not code to paste. Rebuild with React components + Tailwind tokens, matching pixel intent. Use Playwright to screenshot each built page at 1440 and compare against the approved screenshot; log differences in `design/approved/parity.md`; fix anything glaring.
