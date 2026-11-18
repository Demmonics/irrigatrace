"""
OutcomeService for recording real-world field actions and subsequent observations.
"""
from __future__ import annotations

import uuid
from typing import Optional, Dict, Any

from api.irrigatrace.domain.models import (
    OutcomeRecord,
    DecisionStatus,
    EventType,
    canonical_json,
)
from api.irrigatrace.domain.ports import DecisionRepository, Clock
from api.irrigatrace.services.recorder import DecisionRecorder


class OutcomeService:
    def __init__(
        self,
        decision_repo: DecisionRepository,
        recorder: DecisionRecorder,
        clock: Clock,
    ):
        self.decision_repo = decision_repo
        self.recorder = recorder
        self.clock = clock

    def record_action(
        self,
        decision_id: str,
        actual_duration_h: float,
        executed_at: str,
        actor_id: str,
        actor_role: str,
    ) -> Dict[str, Any]:
        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        self.recorder.append_event(
            decision_id=decision_id,
            event_type=EventType.ACTION_RECORDED,
            actor_id=actor_id,
            actor_role=actor_role,
            payload={
                "actual_duration_h": actual_duration_h,
                "executed_at": executed_at,
            },
        )
        self.decision_repo.update_status(decision_id, DecisionStatus.ACTION_RECORDED)
        return {
            "decision_id": decision_id,
            "status": DecisionStatus.ACTION_RECORDED.value,
            "actual_duration_h": actual_duration_h,
            "executed_at": executed_at,
        }

    def record_outcome(
        self,
        decision_id: str,
        recorded_by: str,
        actual_duration_h: Optional[float] = None,
        soil_moisture_after_pct: Optional[float] = None,
        actual_rainfall_mm: Optional[float] = None,
        water_stress_observed: Optional[int] = None,
        crop_health_note: Optional[str] = None,
        notes: Optional[str] = None,
        recorded_at: Optional[str] = None,
    ) -> OutcomeRecord:
        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        now = recorded_at or self.clock.now_iso()
        outcome_id = f"OUT-{uuid.uuid4().hex[:8]}"

        outcome = OutcomeRecord(
            id=outcome_id,
            decision_id=decision_id,
            recorded_by=recorded_by,
            recorded_at=now,
            actual_duration_h=actual_duration_h,
            soil_moisture_after_pct=soil_moisture_after_pct,
            actual_rainfall_mm=actual_rainfall_mm,
            water_stress_observed=water_stress_observed,
            crop_health_note=crop_health_note,
            notes=notes,
        )
        self.decision_repo.save_outcome(outcome)

        self.recorder.append_event(
            decision_id=decision_id,
            event_type=EventType.OUTCOME_RECORDED,
            actor_id=recorded_by,
            actor_role="SUPERVISOR",
            payload={
                "outcome_id": outcome_id,
                "soil_moisture_after_pct": soil_moisture_after_pct,
                "actual_rainfall_mm": actual_rainfall_mm,
                "water_stress_observed": water_stress_observed,
                "crop_health_note": crop_health_note,
            },
            occurred_at=now,
        )
        self.decision_repo.update_status(decision_id, DecisionStatus.OUTCOME_RECORDED)
        return outcome
