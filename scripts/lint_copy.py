import sys
import os
import re

# Banned vocabulary terms that violate IrrigaTrace's honest governance invariants:
# E.g. claiming mathematical causality on observational outcomes, claiming real farm data,
# claiming the LLM made the irrigation decision, or generic marketing slop.
BANNED_PATTERNS = [
    (r"\bAI predicted yield\b", "Never claim the AI predicted or caused farm yield."),
    (r"\bguaranteed crop yield\b", "Never guarantee crop yields."),
    (r"\bactual farm data\b", "All data is prototype simulated; must be labeled illustrative."),
    (r"\bproven causality\b", "Observations only; never claim mathematical causality."),
    (r"\bthe LLM decided\b", "LLM is narration only; deterministic engine decides."),
    (r"\bthe LLM recommended\b", "The deterministic FAO-56 engine recommends, LLM narrates."),
    (r"\blorem ipsum\b", "No placeholder text."),
]

WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web", "app")

def check_files():
    violations = 0
    for root, _, files in os.walk(WEB_DIR):
        for f in files:
            if f.endswith((".tsx", ".ts", ".jsx", ".js")):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                    for pattern, msg in BANNED_PATTERNS:
                        matches = re.findall(pattern, content, flags=re.IGNORECASE)
                        if matches:
                            print(f"[ERROR] Banned vocabulary in {f}: '{matches[0]}' — {msg}")
                            violations += 1
    if violations == 0:
        print("[OK] lint-copy passed: Zero banned vocabulary occurrences detected across all UI files.")
        return 0
    else:
        print(f"[FAIL] {violations} banned vocabulary violations found.")
        return 1

if __name__ == "__main__":
    sys.exit(check_files())
