import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGES = [
    {
        "name": "s2_dashboard",
        "url": "http://localhost:3000/dashboard",
        "desc": "Decision Monitoring Dashboard with KPIs, filters, and pending review queue",
    },
    {
        "name": "s3_case_file",
        "url": "http://localhost:3000/decisions/IRR-2026-018",
        "desc": "Comprehensive Case File for Decision IRR-2026-018 with AI-vs-Human split hero",
    },
    {
        "name": "s4_compare_flips",
        "url": "http://localhost:3000/compare?a=IRR-2026-014&b=IRR-2026-018",
        "desc": "Decision Diff and Single-Variable Flip Sensitivity Analysis",
    },
    {
        "name": "s5_lab_bench",
        "url": "http://localhost:3000/lab",
        "desc": "Interactive Lab Bench Simulator with environmental sliders and live preview",
    },
    {
        "name": "s6_plots_telemetry",
        "url": "http://localhost:3000/plots",
        "desc": "Farm Plots and Soil Telemetry Management across SG-104 to SG-125",
    },
    {
        "name": "s7_analytics",
        "url": "http://localhost:3000/analytics",
        "desc": "Operational Analytics with override rates and reason-code distributions",
    },
    {
        "name": "s8_audit_ledger",
        "url": "http://localhost:3000/audit",
        "action": "click_verify",
        "desc": "Cryptographic Audit Ledger with SHA-256 chain verification",
    },
]

def capture_all():
    out_dirs = [
        Path(r"c:\Study\OOSE\Mini Project\report\screenshots"),
        Path(r"c:\Study\OOSE\report\screenshots"),
    ]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
            color_scheme="dark",
        )
        page = context.new_page()

        for item in PAGES:
            name = item["name"]
            url = item["url"]
            print(f"Navigating to {url}...")
            
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                time.sleep(2)  # Allow client hydration and animations to settle

                # Special action for audit page to trigger verification
                if item.get("action") == "click_verify":
                    try:
                        verify_btn = page.query_selector("button:has-text('Verify')")
                        if verify_btn:
                            verify_btn.click()
                            time.sleep(2)
                    except Exception as e:
                        print(f"  Note: Action verify error: {e}")

                # Wait for any spinners to disappear
                time.sleep(1)

                for out_dir in out_dirs:
                    png_path = out_dir / f"{name}.png"
                    # Capture viewport screenshot
                    page.screenshot(path=str(png_path), full_page=False)
                    print(f"  [OK] Saved {png_path} ({os.path.getsize(png_path)} bytes)")

            except Exception as e:
                print(f"  [FAIL] Error capturing {name}: {e}")

        browser.close()

if __name__ == "__main__":
    capture_all()
