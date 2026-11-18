"""
Health router: GET /health.
Reports status for db, ollama, qdrant, gemini, and models.
"""
from __future__ import annotations

import os
import json
import urllib.request
from fastapi import APIRouter, Depends

from api.irrigatrace.api.deps import get_services, ServicesContainer

router = APIRouter(prefix="", tags=["Health"])


@router.get("/health")
def get_health(services: ServicesContainer = Depends(get_services)):
    # 1. DB check
    db_status = "up"
    try:
        conn = services.db.get_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
    except Exception:
        db_status = "down"

    # 2. Ollama & Models check
    ollama_status = "down"
    models_status = {"llm": False, "embed": False}
    try:
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        with urllib.request.urlopen(f"{ollama_host}/api/tags", timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            installed = {m.get("name") for m in data.get("models", [])}
            ollama_status = "up"
            models_status["llm"] = any("qwen" in m for m in installed)
            models_status["embed"] = any("nomic-embed" in m for m in installed)
    except Exception:
        ollama_status = "degraded"

    # 3. Gemini check
    gemini_status = "down"
    if os.environ.get("GEMINI_API_KEY"):
        gemini_status = "up"

    # 4. Qdrant check
    qdrant_status = "degraded"  # using local/memory/sql fallback
    if os.environ.get("QDRANT_URL"):
        qdrant_status = "degraded"

    overall_status = "up" if db_status == "up" else "degraded"

    return {
        "status": overall_status,
        "db": db_status,
        "ollama": ollama_status,
        "qdrant": qdrant_status,
        "gemini": gemini_status,
        "models": models_status,
    }


@router.get("/users")
def list_users():
    from api.irrigatrace.api.deps import DEMO_USERS
    return list(DEMO_USERS.values())
