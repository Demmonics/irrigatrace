#!/usr/bin/env python3
"""
IrrigaTrace - Automated Evaluator Demo Runner
============================================
Designed for hands-free presentation to professors / evaluators ("Ma'am").
This script automatically launches Chromium, drives through every feature
and screen of IrrigaTrace, highlights key components, and displays on-screen
and terminal speech cues so you can present without touching the keyboard or mouse!

Usage:
    python run_demo.py
    python run_demo.py --pace fast       (Quick rehearsal ~2.5 min)
    python run_demo.py --pace normal     (Default, balanced ~5 min)
    python run_demo.py --pace relaxed    (Extended ~7 min)
    python run_demo.py --step-by-step    (Press Enter to advance between sections)
"""

import sys
import os
import time
import argparse
import urllib.request
from typing import Optional

# ANSI colors for beautiful terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

BANNER = f"""{Colors.CYAN}{Colors.BOLD}
================================================================================
   IRRIGATRACE: AUTOMATED HANDS-FREE DEMO FOR EVALUATION
   Forensic Audit Trail & Lifecycle Observatory for AI Irrigation Decisions
   Branch: Stitch Glassy UI · KJS-AGR-01 · OOSE Lab Evaluation
================================================================================{Colors.RESET}
"""

def print_step(step_num: int, total_steps: int, title: str, cue: str):
    print(f"\n{Colors.GREEN}{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD} [STEP {step_num}/{total_steps}] {title.upper()}{Colors.RESET}")
    print(f"{Colors.GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print(f"{Colors.YELLOW}{Colors.BOLD} 🗣️  WHAT TO SAY TO MA'AM NOW:{Colors.RESET}")
    print(f"{Colors.BOLD} \"{cue}\"{Colors.RESET}\n")

def check_server(url: str, timeout: int = 3) -> bool:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'IrrigaTrace-DemoCheck'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 304)
    except Exception:
        return False

# JavaScript injected into pages to show teleprompter overlay and highlight elements
INJECTED_JS = """
window.__showDemoCue = function(stepTitle, speechCue, timeSec) {
    let el = document.getElementById('irrigatrace-demo-banner');
    if (!el) {
        el = document.createElement('div');
        el.id = 'irrigatrace-demo-banner';
        el.style.position = 'fixed';
        el.style.top = '14px';
        el.style.left = '50%';
        el.style.transform = 'translateX(-50%)';
        el.style.zIndex = '999999';
        el.style.maxWidth = '960px';
        el.style.width = '92%';
        el.style.backgroundColor = 'rgba(15, 23, 42, 0.94)';
        el.style.backdropFilter = 'blur(16px)';
        el.style.color = '#f8fafc';
        el.style.padding = '14px 22px';
        el.style.borderRadius = '18px';
        el.style.boxShadow = '0 20px 45px -10px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.18)';
        el.style.fontFamily = 'system-ui, -apple-system, sans-serif';
        el.style.pointerEvents = 'none';
        el.style.transition = 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
        document.body.appendChild(el);
    }
    el.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:6px;">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:#10b981;box-shadow:0 0 10px #10b981;"></span>
                <span style="font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#38bdf8;">${stepTitle}</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:10px;font-family:monospace;background:rgba(56,189,248,0.15);border:1px solid rgba(56,189,248,0.3);padding:2px 8px;border-radius:999px;color:#38bdf8;">🎙️ PRESENTATION AUTO-PILOT</span>
            </div>
        </div>
        <div style="font-size:13px;line-height:1.45;color:#f1f5f9;font-weight:450;">
            <span style="color:#fbbf24;font-weight:700;margin-right:6px;">🗣️ SPEAK:</span> ${speechCue}
        </div>
    `;
};

window.__highlightElement = function(selector) {
    try {
        const el = document.querySelector(selector);
        if (!el) return;
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        const prevTransition = el.style.transition;
        const prevOutline = el.style.outline;
        const prevShadow = el.style.boxShadow;
        el.style.transition = 'all 0.35s ease';
        el.style.outline = '3px solid #38bdf8';
        el.style.boxShadow = '0 0 30px rgba(56, 189, 248, 0.6)';
        setTimeout(() => {
            el.style.outline = prevOutline;
            el.style.boxShadow = prevShadow;
            el.style.transition = prevTransition;
        }, 4000);
    } catch (e) {
        console.error(e);
    }
};

window.__smoothScroll = function(targetY, durationMs) {
    return new Promise((resolve) => {
        const startY = window.scrollY;
        const diff = targetY - startY;
        const startTime = performance.now();
        function step(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / durationMs, 1);
            const ease = 0.5 - Math.cos(progress * Math.PI) / 2;
            window.scrollTo(0, startY + diff * ease);
            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                resolve();
            }
        }
        requestAnimationFrame(step);
    });
};
"""

def run_demo(pace: str = 'normal', step_by_step: bool = False):
    print(BANNER)
    
    # Scale sleep multipliers based on chosen pace
    multipliers = {
        'fast': 0.5,
        'normal': 1.0,
        'relaxed': 1.5
    }
    m = multipliers.get(pace, 1.0)

    def pause(seconds: float):
        time.sleep(seconds * m)

    def gate(prompt: str = "Press Enter to continue to next step..."):
        if step_by_step:
            print(f"{Colors.DIM}>>> {prompt}{Colors.RESET}")
            try:
                input()
            except (KeyboardInterrupt, EOFError):
                sys.exit(0)

    # 1. Health check
    print(f"{Colors.CYAN}[1/2] Checking services...{Colors.RESET}")
    web_ok = check_server("http://localhost:3000")
    api_ok = check_server("http://localhost:8000/api/health")

    if not web_ok or not api_ok:
        print(f"\n{Colors.RED}[WARNING] Dev servers are not currently running!{Colors.RESET}")
        if not web_ok:
            print(f"  ❌ Web app: http://localhost:3000 is not responding")
        if not api_ok:
            print(f"  ❌ Backend API: http://localhost:8000/api/health is not responding")
        print(f"\n{Colors.YELLOW}Please start them using in another terminal:{Colors.RESET}")
        print(f"  Backend: python -m uvicorn api.irrigatrace.main:app --port 8000")
        print(f"  Frontend: cd web && npm run dev")
        print(f"\nAttempting to continue anyway in case they are still booting up...")
    else:
        print(f"{Colors.GREEN}  ✓ Web Observatory (port 3000) is ONLINE{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ FastAPI Backend (port 8000) is ONLINE{Colors.RESET}")

    # 2. Launch Playwright
    print(f"\n{Colors.CYAN}[2/2] Launching Chromium in Presentation Mode...{Colors.RESET}")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(f"{Colors.RED}Playwright is not installed. Run: python -m pip install playwright && playwright install chromium{Colors.RESET}")
        sys.exit(1)

    with sync_playwright() as p:
        # Launch visible browser with full window
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--no-default-browser-check'
            ]
        )
        context = browser.new_context(viewport=None)
        page = context.new_page()

        def set_cue(title: str, cue: str, duration: float = 6.0):
            try:
                page.evaluate(f"window.__showDemoCue({repr(title)}, {repr(cue)}, {duration})")
            except Exception:
                pass

        def highlight(selector: str):
            try:
                page.evaluate(f"window.__highlightElement({repr(selector)})")
            except Exception:
                pass

        def scroll_to(y: int, duration_ms: int = 1200):
            try:
                page.evaluate(f"window.__smoothScroll({y}, {duration_ms})")
                pause(duration_ms / 1000.0)
            except Exception:
                pass

        TOTAL_STEPS = 7

        # -------------------------------------------------------------
        # STEP 1: LANDING PAGE & EDITORIAL OBSERVATORY
        # -------------------------------------------------------------
        cue_1 = "Good morning Ma'am. This is IrrigaTrace — an immutable forensic audit observatory for AI irrigation decisions. When an autonomous system decides whether to release thousands of liters of water, farmers need absolute accountability. Our system records every decision, frozen sensor snapshot, and agronomist modification into a tamper-evident audit ledger."
        print_step(1, TOTAL_STEPS, "Landing Page & System Architecture", cue_1)
        
        page.goto("http://localhost:3000/", wait_until="networkidle")
        page.evaluate(INJECTED_JS)
        set_cue("1/7 — Observatory Landing", cue_1)
        pause(4)

        # Smooth exploration of landing page
        highlight("h1")
        pause(3)

        # Scroll to 6 questions
        scroll_to(650, 1000)
        pause(3)

        # Scroll to 4 Pillars
        scroll_to(1300, 1000)
        pause(3)

        # Scroll to Dynamic Reviews
        scroll_to(2000, 1000)
        pause(3)

        # Scroll back to top
        scroll_to(0, 1000)
        pause(2)

        # Click Launch Dashboard
        gate("Ready to launch Dashboard? Press Enter...")
        highlight("a[href='/dashboard']")
        pause(1.5)
        page.click("a[href='/dashboard']")
        page.wait_for_load_state("networkidle")
        page.evaluate(INJECTED_JS)

        # -------------------------------------------------------------
        # STEP 2: DASHBOARD & IMMUTABLE KPI MONITORING
        # -------------------------------------------------------------
        cue_2 = "Here on the Monitoring Dashboard, we track all decisions across 6 sugarcane plots in Karnataka. Notice our primary KPI card showing 125+ decisions with cryptographic genesis hashes. Unlike standard dashboards that overwrite records, IrrigaTrace explicitly exposes human-in-the-loop overrides. Watch as I filter exclusively for overridden decisions."
        print_step(2, TOTAL_STEPS, "Decision Monitoring Dashboard & KPIs", cue_2)
        set_cue("2/7 — Monitoring Dashboard & KPIs", cue_2)
        pause(3)

        # Highlight Dominant KPI Card
        highlight("div.glass-card")
        pause(3)

        # Click "Overridden Only" filter
        highlight("button:has-text('Overridden Only')")
        pause(1.5)
        page.click("button:has-text('Overridden Only')")
        pause(3)

        # Point to Hero Decision IRR-2026-018
        highlight("a[href='/decisions/IRR-2026-018']")
        pause(2.5)

        gate("Ready to inspect hero case IRR-2026-018? Press Enter...")
        page.click("a[href='/decisions/IRR-2026-018']")
        page.wait_for_load_state("networkidle")
        page.evaluate(INJECTED_JS)

        # -------------------------------------------------------------
        # STEP 3: CASE FILE & AI VS HUMAN SPLIT
        # -------------------------------------------------------------
        cue_3 = "This is our Hero Case File: IRR-2026-018. The central visual shows our signature Split Decision: the AI engine calculated 2.8 hours, but Field Supervisor Anita R. reduced it to 2.0 hours due to local furrow conditions. The original AI recommendation is NEVER erased or overwritten. All sensor inputs — 21% soil moisture, 33°C ambient temperature — are cryptographically frozen at decision time."
        print_step(3, TOTAL_STEPS, "Case File & AI vs Human Split Decision", cue_3)
        set_cue("3/7 — Hero Case IRR-2026-018 Split Analysis", cue_3)
        pause(4)

        # Highlight Split Number
        highlight("div.glass-card")
        pause(4)

        # Scroll down to frozen inputs
        scroll_to(450, 1000)
        pause(3)

        # Highlight authoritative FAO-56 factors
        scroll_to(800, 1000)
        pause(3)

        # Demonstrate multilingual local briefing translation
        cue_3_trans = "For field accessibility, our system generates plain-language briefings via local LLM while mathematically guaranteeing that numeric values can never be hallucinated. Notice how we support local regional languages like Hindi and Kannada for field supervisors."
        set_cue("3/7 — Regional Field Accessibility", cue_3_trans)
        print(f"{Colors.YELLOW}🗣️  {cue_3_trans}{Colors.RESET}\n")
        
        try:
            page.click("button:has-text('हिन्दी')")
            pause(2.5)
            page.click("button:has-text('ಕನ್ನಡ')")
            pause(2.5)
            page.click("button:has-text('EN')")
            pause(1.5)
        except Exception:
            pass

        # Scroll back to top
        scroll_to(0, 800)
        pause(1.5)

        # -------------------------------------------------------------
        # STEP 4: ORBIT REPLAY SCRUBBER & REPRODUCE CHECK
        # -------------------------------------------------------------
        cue_4 = "Now let's switch to the Replay tab. This is our Orbit Timeline. In traditional systems, you only see the final state. Here, you can scrub backwards through time to see the exact state at 09:41 when sensors fired, at 09:42 when weather arrived, and at 10:05 when the supervisor signed off. Above it is our 'Reproduce Check' button, which re-runs the pure deterministic FAO-56 engine to verify that historical inputs reproduce the exact 2.8-hour recommendation."
        print_step(4, TOTAL_STEPS, "Orbit Replay Scrubber & Reproduce Check", cue_4)
        
        # Click Replay Tab
        page.click("button:has-text('replay')")
        pause(2)
        set_cue("4/7 — Orbit Timeline & Deterministic Reproducibility", cue_4)

        # Scrub through the timeline events
        timeline_buttons = page.query_selector_all("div.relative button.group")
        if timeline_buttons:
            for i, btn in enumerate(timeline_buttons[:5]):
                try:
                    btn.click()
                    pause(1.2)
                except Exception:
                    pass
        else:
            pause(3)

        # Scroll up and click Reproduce Check
        scroll_to(0, 800)
        pause(1.5)
        highlight("button:has-text('Reproduce Check')")
        pause(1.5)
        page.click("button:has-text('Reproduce Check')")
        pause(3)

        # -------------------------------------------------------------
        # STEP 5: DIFFERENTIAL ATTRIBUTION (COMPARE 014 VS 018)
        # -------------------------------------------------------------
        cue_5 = "A major challenge in agronomy is: 'Why did the AI say DEFER yesterday, but IRRIGATE today?' In our Differential Attribution view, we compare yesterday's IRR-014 against today's IRR-018. The delta matrix immediately shows that rain probability dropped from 72% down to 12%, and our single-variable counterfactual test proves rain alone flipped the decision."
        print_step(5, TOTAL_STEPS, "Differential Attribution & Flip Sensitivity", cue_5)
        
        gate("Ready to view Compare analysis? Press Enter...")
        page.goto("http://localhost:3000/compare?a=IRR-2026-014&b=IRR-2026-018", wait_until="networkidle")
        page.evaluate(INJECTED_JS)
        set_cue("5/7 — Differential Attribution & Counterfactual Flip", cue_5)
        pause(4)

        # Highlight comparison header cards
        highlight("div.grid")
        pause(3)

        # Scroll to delta matrix
        scroll_to(550, 1000)
        pause(3)

        # Scroll to single-variable flip sensitivity
        scroll_to(1100, 1000)
        pause(4)

        # -------------------------------------------------------------
        # STEP 6: LAB BENCH LIVE SIMULATION & REAL DECISION GENERATION
        # -------------------------------------------------------------
        cue_6 = "Next is the Lab Bench simulator. Here agronomists can stress-test the FAO-56 rules under extreme climate conditions. When I click the 'Dry & Hot' preset, the sliders immediately adjust to 17.5% moisture and 34°C, and the stateless preview shows an instant 2.8h recommendation. When we click 'Generate Real Decision', server-sent events stream each lifecycle block live into the hash chain."
        print_step(6, TOTAL_STEPS, "Lab Bench Simulator & Live Stream", cue_6)

        gate("Ready to open Lab Bench? Press Enter...")
        page.goto("http://localhost:3000/lab", wait_until="networkidle")
        page.evaluate(INJECTED_JS)
        set_cue("6/7 — Lab Bench Simulator & Event Streaming", cue_6)
        pause(3)

        # Click Preset "Dry & Hot"
        highlight("button:has-text('Dry & Hot')")
        pause(1.5)
        page.click("button:has-text('Dry & Hot')")
        pause(2.5)

        # Highlight live stateless preview
        highlight("div.liquid-orb")
        pause(2.5)

        # Click Generate Real Decision
        highlight("button:has-text('Generate Real Decision')")
        pause(1.5)
        page.click("button:has-text('Generate Real Decision')")
        pause(4)

        # -------------------------------------------------------------
        # STEP 7: CRYPTOGRAPHIC AUDIT LEDGER
        # -------------------------------------------------------------
        cue_7 = "Finally, we arrive at the Cryptographic Audit & Ledger. Every single event is bound by a SHA-256 sequential hash formula: H(i) = SHA-256(decision_id || seq || payload || H(i-1)). When I trigger 'Verify All Chains', the auditor checks every mathematical link. If anyone tampers with a historical sensor or timestamp in the database, the chain breaks immediately."
        print_step(7, TOTAL_STEPS, "Cryptographic Audit Ledger & Chain Verification", cue_7)

        gate("Ready to inspect Audit Ledger? Press Enter...")
        page.goto("http://localhost:3000/audit", wait_until="networkidle")
        page.evaluate(INJECTED_JS)
        set_cue("7/7 — Cryptographic SHA-256 Audit Verification", cue_7)
        pause(3)

        # Highlight Formula Card
        highlight("code")
        pause(3)

        # Click Verify All Chains
        highlight("button:has-text('Verify All Chains')")
        pause(1.5)
        page.click("button:has-text('Verify All Chains')")
        pause(4)

        # -------------------------------------------------------------
        # CONCLUSION / WRAP-UP
        # -------------------------------------------------------------
        cue_final = "To conclude: IrrigaTrace does not try to be a black-box AI — it provides a trustworthy, auditable, and human-governed lifecycle around any agricultural decision. Thank you Ma'am, we are now ready for your questions."
        print(f"\n{Colors.GREEN}{Colors.BOLD}================================================================================{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD} DEMO COMPLETE! WRAP-UP CUE:{Colors.RESET}")
        print(f"{Colors.YELLOW}{Colors.BOLD} 🗣️  \"{cue_final}\"{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}================================================================================{Colors.RESET}\n")

        set_cue("DEMO COMPLETE — CONCLUSION", cue_final)
        
        # Smoothly return to Dashboard
        pause(5)
        page.goto("http://localhost:3000/dashboard", wait_until="networkidle")
        page.evaluate(INJECTED_JS)
        set_cue("IrrigaTrace Evaluation Complete", cue_final)

        print(f"{Colors.CYAN}The browser will remain open so you can answer questions or navigate anywhere.{Colors.RESET}")
        print(f"{Colors.DIM}Press Enter in this terminal window whenever you want to close the browser...{Colors.RESET}")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            pass
        browser.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="IrrigaTrace Automated Demo Runner")
    parser.add_argument('--pace', choices=['fast', 'normal', 'relaxed'], default='normal',
                        help="Pacing speed: fast (~2.5 min), normal (~5 min), relaxed (~7 min)")
    parser.add_argument('--step-by-step', action='store_true',
                        help="Wait for Enter key before advancing to each major screen")
    args = parser.parse_args()

    run_demo(pace=args.pace, step_by_step=args.step_by_step)
