"""
FastAPI dependency injection and authorization.
Resolves X-Demo-User header to authenticated user and role.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import Header, HTTPException, status, Depends

from api.irrigatrace.infra.db.connection import get_db, Database
from api.irrigatrace.infra.db.repositories import (
    SqlitePlotRepository,
    SqliteSensorRepository,
    SqliteWeatherRepository,
    SqliteDecisionRepository,
    SystemClock,
)
from api.irrigatrace.domain.engine import RuleSet
from api.irrigatrace.services.recorder import DecisionRecorder
from api.irrigatrace.services.review import ReviewService
from api.irrigatrace.services.replay import DecisionReplayService
from api.irrigatrace.services.comparison import ComparisonService
from api.irrigatrace.services.integrity import IntegrityService
from api.irrigatrace.services.outcome import OutcomeService
from api.irrigatrace.services.narration import NarrationService
from api.irrigatrace.services.translation import TranslationService
from api.irrigatrace.services.similarity import SimilaritySearchService
from api.irrigatrace.api.sse import broadcaster

DEMO_USERS = {
    "user-sup-01": {"id": "user-sup-01", "name": "Ramesh Patil", "role": "SUPERVISOR"},
    "user-adm-01": {"id": "user-adm-01", "name": "Anil Deshmukh", "role": "ADMIN"},
    "user-aud-01": {"id": "user-aud-01", "name": "Dr. Sunita Rao", "role": "AUDITOR"},
}


def get_current_user(x_demo_user: Optional[str] = Header(None, alias="X-Demo-User")) -> Dict[str, str]:
    if not x_demo_user:
        # Default demo user if header omitted in development
        if os.environ.get("DEMO_AUTH", "true").lower() == "true":
            return DEMO_USERS["user-sup-01"]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required X-Demo-User authentication header",
        )
    user = DEMO_USERS.get(x_demo_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unknown demo user ID: {x_demo_user}",
        )
    return user


def require_role(*allowed_roles: str):
    def role_checker(user: Dict[str, str] = Depends(get_current_user)) -> Dict[str, str]:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{user['role']}' is not authorized for this operation",
            )
        return user
    return role_checker


# Singleton services provider
class ServicesContainer:
    def __init__(self):
        self.db = get_db()
        self.clock = SystemClock()
        self.plot_repo = SqlitePlotRepository(self.db)
        self.sensor_repo = SqliteSensorRepository(self.db)
        self.weather_repo = SqliteWeatherRepository(self.db)
        self.decision_repo = SqliteDecisionRepository(self.db)

        # Load default ruleset
        rules_path = Path(__file__).resolve().parent.parent / "rules" / "rules-v1.4.2.yaml"
        with open(rules_path, "r", encoding="utf-8") as f:
            self.ruleset = RuleSet.from_yaml(f.read())

        self.recorder = DecisionRecorder(
            decision_repo=self.decision_repo,
            plot_repo=self.plot_repo,
            sensor_repo=self.sensor_repo,
            weather_repo=self.weather_repo,
            clock=self.clock,
            event_publisher=broadcaster,
        )

        self.review_service = ReviewService(
            decision_repo=self.decision_repo,
            recorder=self.recorder,
            clock=self.clock,
        )

        self.replay_service = DecisionReplayService(
            decision_repo=self.decision_repo,
            recorder=self.recorder,
            clock=self.clock,
        )

        self.comparison_service = ComparisonService(
            decision_repo=self.decision_repo,
        )

        self.integrity_service = IntegrityService(
            decision_repo=self.decision_repo,
            clock=self.clock,
        )

        self.outcome_service = OutcomeService(
            decision_repo=self.decision_repo,
            recorder=self.recorder,
            clock=self.clock,
        )

        # AI Services
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        ollama_model = os.environ.get("LLM_MODEL", "qwen2.5:3b")

        self.narration_service = NarrationService(
            decision_repo=self.decision_repo,
            recorder=self.recorder,
            clock=self.clock,
            ollama_host=ollama_host,
            ollama_model=ollama_model,
            gemini_api_key=gemini_key,
        )

        self.translation_service = TranslationService(
            decision_repo=self.decision_repo,
            clock=self.clock,
            gemini_api_key=gemini_key,
        )

        self.similarity_service = SimilaritySearchService(
            decision_repo=self.decision_repo,
            plot_repo=self.plot_repo,
            ollama_host=ollama_host,
        )


_CONTAINER: Optional[ServicesContainer] = None


def get_services() -> ServicesContainer:
    global _CONTAINER
    if _CONTAINER is None:
        _CONTAINER = ServicesContainer()
    return _CONTAINER
