# Design Language Extraction: Stitch Source of Truth

Extracted from:
- Project: **"Remix of H612 Saas Landing Page"** (ID `14433471932359710161`)
- Light mode screen: **"Refined Light Mode Learning Page with Glassy UI"** (ID `172d95b73fc24a32b28c2b3b0c309116`)
- Dark mode screen: **"Updated Learning Page with Dynamic Reviews"** (ID `d024a0f03bb745898fae7c7dd727cf40`)

---

## 1. Color Palette (Exact Hex Values)

| Role | Light Mode | Dark Mode | Notes & Contrast |
| :--- | :--- | :--- | :--- |
| **Canvas / Background** | `#f9f9f9` (subtle off-white) | `#0a0a0a` / `#141313` | Deep obsidian night in dark; pristine crisp warm canvas in light |
| **Surface (Container)** | `#eeeeee` / `#f3f3f4` | `#121212` / `#1c1c1e` | Card bases |
| **Surface Glass** | `rgba(255, 255, 255, 0.70)` | `rgba(28, 28, 30, 0.95)` / `rgba(18, 18, 18, 0.85)` | Frosted glass cards |
| **Glass Border / Hairline** | `rgba(0, 0, 0, 0.08)` / `#cfc4c5` | `rgba(255, 255, 255, 0.12)` / `#262626` / `#333333` | Hairline crisp separation |
| **Text Primary** | `#1a1c1c` (near black, `#000000` headers) | `#ffffff` / `#e5e2e1` | Contrast ratio > 15:1 in both modes |
| **Text Secondary** | `#5e5e5e` / `#4c4546` | `#c7c6c6` / `#a1a1aa` | WCAG AA compliant (> 4.8:1) |
| **Text Tertiary / Muted** | `#7e7576` | `#636565` / `#71717a` | Captions and tracking labels |
| **Primary Button Fill** | `#000000` (pill, text `#ffffff`) | `#ffffff` (pill, text `#000000` / `#1a1c1c`) | Inverted high-contrast pills |
| **Secondary Button** | Border `#cfc4c5`, bg `rgba(255,255,255,0.4)` | Border `#262626`, bg `rgba(255,255,255,0.05)` | Subtle translucent hover |
| **Accent / Indicator** | Liquid rainbow orb (`#2196f3`, `#e91e63`, `#ffeb3b`, `#4caf50`, `#9c27b0`) & Indigo/Purple gradient (`#6366f1` to `#a855f7`) | Indigo/Purple gradient (`#6366f1` to `#a855f7`) | Subdued glowing indicator dots |
| **Success / Verified** | `#2e7d32` / `#4caf50` | `#4ade80` | Integrity seal, approved events |
| **Warning / Modified** | `#d97706` | `#f59e0b` | Human review overrides |
| **Error / Alert** | `#ba1a1a` (light) / `#ffdad6` cont | `#ffb4ab` (dark) / `#93000a` cont | Rejections, sensor faults |

---

## 2. Typography

Primary Serif Font: **Noto Serif** (Headings, titles, editorial callouts)  
Primary Sans Font: **Manrope** (Body, labels, navigation, interactive controls)  
Mono Font (Technical/IDs): **JetBrains Mono** / system monospace (for trigger IDs, telemetry, hash signatures)

| Level | Font Family | Size | Weight | Line Height | Tracking | Transform |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Display XL** | Noto Serif | 48px – 72px (`4.5rem`) | 300 / 400 (Light) | 1.1 – 1.2 | `-0.02em` | Normal |
| **Headline LG** | Noto Serif | 36px – 42px (`2.5rem`) | 400 / 500 | 1.2 – 1.3 | `-0.01em` | Normal |
| **Headline MD** | Noto Serif | 24px – 32px (`2rem`) | 500 / 600 | 1.3 – 1.4 | `-0.01em` | Normal |
| **Body LG** | Manrope | 18px (`1.125rem`) | 400 | 1.6 | `0.01em` | Normal |
| **Body MD** | Manrope | 16px (`1.0rem`) | 400 | 1.6 | Normal | Normal |
| **Body SM** | Manrope | 14px (`0.875rem`) | 400 | 1.5 | Normal | Normal |
| **Label SM / Kicker**| Manrope | 12px – 13px (`0.75rem`)| 600 | 1.2 – 1.4 | `0.15em` – `0.2em` | UPPERCASE |
| **Mono Code/Audit** | JetBrains Mono | 12px – 13px | 500 | 1.4 | `0.05em` | Normal / UPPERCASE |

---

## 3. Radii, Spacing & Grid System

- **Border Radii:**
  - Standard cards: `rounded-2xl` (`16px` to `20px` / `rounded-[20px]`)
  - Bento cards: `rounded-xl` (`12px`)
  - Buttons & Badges: `rounded-full` (`100px` capsule)
  - Small pills & tags: `rounded-full` (`9999px`)
- **Spacing Scale:**
  - Base unit: `8px`
  - Gutter: `32px`
  - Container Max Width: `1200px` (`max-w-[1200px]` / `max-w-container-max`)
  - Section Padding: `80px` – `120px` desktop, `40px` mobile
- **Bento Grid Layout:**
  - 12-column grid (`grid-cols-1 md:grid-cols-12 gap-8`)
  - Hero splits: `md:col-span-8` primary card with image/action + `md:col-span-4` metric/status cards.

---

## 4. Glass Effect & Surfaces Specification

- **Light Mode Glass:**
  - `background`: `rgba(255, 255, 255, 0.70)` to `rgba(255, 255, 255, 0.85)`
  - `backdrop-filter`: `blur(16px)` to `blur(24px)`
  - `border`: `1px solid rgba(0, 0, 0, 0.08)` (or `#cfc4c5`)
  - `box-shadow`: `0 20px 40px -15px rgba(0, 0, 0, 0.05), 0 0 1px 1px rgba(255, 255, 255, 0.8) inset`
- **Dark Mode Glass:**
  - `background`: `rgba(28, 28, 30, 0.85)` to `rgba(18, 18, 18, 0.90)`
  - `backdrop-filter`: `blur(20px)`
  - `border`: `1px solid rgba(255, 255, 255, 0.10)` (or `#262626` / `#333333`)
  - `box-shadow`: `0 25px 50px -12px rgba(0, 0, 0, 0.50), 0 0 1px 1px rgba(255, 255, 255, 0.05) inset`
- **Solid-ish Fallback (when backdrop-filter not supported):**
  - Light: `#ffffff` with 98% opacity
  - Dark: `#161618` with 98% opacity

---

## 5. Navigation, Button & Component Micro-Styles

- **Navigation Bar:**
  - Fixed / sticky top navigation with subtle bottom hairline border (`border-b border-black/10` in light, `border-[#262626]/40` in dark).
  - Floating container (`max-w-[1200px]`) with glass backdrop (`backdrop-blur-md`).
  - Active links have understated bottom indicator or subtle opacity boost.
  - Theme toggle switch visible on the right next to system status badge.
- **Buttons:**
  - **Primary CTA:** Capsule pill (`rounded-full py-2.5 px-6 font-medium text-xs md:text-sm`). Black in light mode, crisp white in dark mode. Smooth hover scale/brightness.
  - **Secondary CTA:** Border capsule (`border border-black/15 dark:border-white/20 hover:bg-black/5 dark:hover:bg-white/5`).
- **Interactive Reveal Items (The 3-Step Rhythm):**
  - Accordion / progressive disclosure list with a top hairline border and an animated horizontal indicator line that stretches on hover:
    - `group-hover:w-full transition-all duration-500`
    - Inactive: `w-0` or `w-1/3`, color muted. Active: color primary.
- **Dynamic Human Review Feed (replacing Stitch review placeholder):**
  - Glass card container displaying human-in-the-loop audit actions from seeded telemetry.
  - Role badge (Agronomist, Lead Reviewer), Decision badge (`Approved`, `Modified`, `Rejected`), timestamp, and AI Duration vs Final Duration telemetry split.

---

## 6. Differences Between Light & Dark Beyond Inversion

1. **Atmosphere / Underlay:**
   - Dark mode features deep twilight / celestial photography with dark vignette scrims (`bg-gradient-to-t from-[#0a0a0a] via-transparent`).
   - Light mode features soft high-key architectural photography, crisp mountain daylight, and soft paper-like warmth (`#f9f9f9`).
2. **Hairline Weighting:**
   - Hairlines in light mode use subtle soft grey (`rgba(0,0,0,0.08)`).
   - In dark mode, borders are defined by `#262626` to `#333333` with subtle interior specular highlights (`inset 0 1px 0 rgba(255,255,255,0.05)`).
3. **Typography Contrast Balance:**
   - Light mode leverages Noto Serif in bold/light contrast with dark ink tones (`#1a1c1c`).
   - Dark mode softens pure white body text to `#e5e2e1` and `#a1a1aa` to eliminate eye strain and halation.
