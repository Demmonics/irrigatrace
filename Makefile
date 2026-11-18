.PHONY: setup dev test e2e seed demo llm-eval lint format check-models

PYTHON ?= python
UVICORN ?= uvicorn
NPM ?= npm

setup:
	$(PYTHON) -m pip install -r api/requirements.txt
	cd web && $(NPM) install

dev:
	powershell -ExecutionPolicy Bypass -Command "Start-Process python -ArgumentList '-m uvicorn api.irrigatrace.main:app --reload --port 8000' ; cd web ; npm run dev"

test:
	pytest api/tests -v

llm-eval:
	$(PYTHON) scripts/eval_llm.py

seed:
	$(PYTHON) scripts/seed_scenario.py

demo:
	powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1

check-models:
	$(PYTHON) scripts/check_models.py

lint:
	ruff check api
	cd web && $(NPM) run lint

format:
	ruff format api
