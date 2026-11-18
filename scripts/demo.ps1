# demo.ps1 - IrrigaTrace 7-Minute Evaluator Demo Script
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "         IRRIGATRACE: NIGHT FIELD OBSERVATORY DEMO SUITE             " -ForegroundColor Green
Write-Host "         KJS-AGR-01 · OOSE Lab Evaluation · 7-Minute Walkthrough    " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

# Step 1: Run comprehensive pipeline verifier
Write-Host "`n[STEP 1/3] Running Automated 8-Step Scenario Verification..." -ForegroundColor Yellow
python scripts/verify_demo_pipeline.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Demo pipeline verification failed! Check error details above." -ForegroundColor Red
    exit 1
}

Write-Host "`n[STEP 2/3] Verification Passed 100%! Ready to launch dev servers." -ForegroundColor Green
Write-Host "  * Backend API: http://localhost:8000/docs" -ForegroundColor DarkCyan
Write-Host "  * Observatory Web App: http://localhost:3000" -ForegroundColor DarkCyan
Write-Host "  * Hero Scenario: http://localhost:3000/decisions/IRR-2026-018" -ForegroundColor DarkCyan
Write-Host "  * Compare 014 vs 018: http://localhost:3000/compare?a=IRR-2026-014&b=IRR-2026-018" -ForegroundColor DarkCyan
Write-Host "  * Lab Bench: http://localhost:3000/lab" -ForegroundColor DarkCyan

Write-Host "`n[STEP 3/3] 7-Minute Presentation Sequence:" -ForegroundColor Yellow
Write-Host "  Minute 0-1: Landing Page (Observatory theme, 4 pillars, 6 questions)"
Write-Host "  Minute 1-2: Dashboard (Dominant Total KPI, filter 'Overridden only')"
Write-Host "  Minute 2-4: Case File (IRR-2026-018 split number: 2.8h AI vs 2.0h human, factors)"
Write-Host "  Minute 4-5: Replay Tab (Orbit scrubber, state-at-t, reproduce check)"
Write-Host "  Minute 5-6: Compare Tab (014 vs 018, lavender diff glow, flip sensitivity)"
Write-Host "  Minute 6-7: Lab Bench (Sliders, live preview, generate decision with SSE)"
Write-Host "  Minute 7+ : Audit Ledger (SHA-256 chain verification, honest prototype caveat)"

Write-Host "`nAll systems green! To run servers concurrently, execute: make dev" -ForegroundColor Cyan
