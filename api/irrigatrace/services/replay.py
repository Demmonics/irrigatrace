"""
DecisionReplayService.
Implements:
1. Ordered historical timeline.
2. Temporal state reconstruction at time t (state_at).
3. Reproduce verification (re-running pinned engine on immutable snapshot).
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from api.irrigatrace.domain.models import (
    EventType,
    RecommendedAction,
    DecisionStatus,
    EngineInputs,
    CropStage,
    canonical_json,
)
from api.irrigatrace.domain.engine import RuleSet, IrrigationEngine
from api.irrigatrace.domain.ports import DecisionRepository, Clock
from api.irrigatrace.services.recorder import DecisionRecorder


class DecisionReplayService:
    def __init__(
        self,
        decision_repo: DecisionRepository,
        recorder: DecisionRecorder,
        clock: Clock,
    ):
        self.decision_repo = decision_repo
        self.recorder = recorder
        self.clock = clock

    def timeline(self, decision_id: str) -> List[Dict[str, Any]]:
        events = self.decision_repo.get_events(decision_id)
        result = []
        for ev in events:
            result.append({
                "seq": ev.seq,
                "event_type": ev.event_type.value,
                "actor_id": ev.actor_id,
                "actor_role": ev.actor_role,
                "occurred_at": ev.occurred_at,
                "payload": json.loads(ev.payload_json),
                "event_hash": ev.event_hash,
                "prev_hash": ev.prev_hash,
            })
        return result

    def state_at(self, decision_id: str, t_iso: str) -> Dict[str, Any]:
        """
        Folds events up to time t into a temporal view-model.
        """
        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        events = self.decision_repo.get_events(decision_id)
        t_target = datetime.fromisoformat(t_iso.replace("Z", "+00:00"))

        inputs_known = None
        recommendation_known = None
        review_known = None
        current_status = DecisionStatus.GENERATED.value

        events_applied = []
        future_events = []

        for ev in events:
            ev_time = datetime.fromisoformat(ev.occurred_at.replace("Z", "+00:00"))
            payload = json.loads(ev.payload_json)
            if ev_time <= t_target:
                events_applied.append(ev.event_type.value)
                if ev.event_type == EventType.SENSOR_RECEIVED:
                    if not inputs_known:
                        inputs_known = {}
                    inputs_known.update(payload)
                elif ev.event_type == EventType.WEATHER_CAPTURED:
                    if not inputs_known:
                        inputs_known = {}
                    inputs_known.update(payload)
                elif ev.event_type == EventType.RECOMMENDATION_GENERATED:
                    recommendation_known = payload
                    current_status = DecisionStatus.PENDING_REVIEW.value
                elif ev.event_type in (EventType.REVIEW_APPROVED, EventType.REVIEW_MODIFIED, EventType.REVIEW_REJECTED):
                    review_known = payload
                elif ev.event_type == EventType.DECISION_FINALIZED:
                    current_status = DecisionStatus.FINALIZED.value
                elif ev.event_type == EventType.ACTION_RECORDED:
                    current_status = DecisionStatus.ACTION_RECORDED.value
                elif ev.event_type == EventType.OUTCOME_RECORDED:
                    current_status = DecisionStatus.OUTCOME_RECORDED.value
            else:
                future_events.append({
                    "event_type": ev.event_type.value,
                    "occurred_at": ev.occurred_at,
                    "label": "Not yet happened at scrubber time t"
                })

        return {
            "decision_id": decision_id,
            "target_time": t_iso,
            "status_at_t": current_status,
            "inputs": inputs_known,
            "recommendation": recommendation_known,
            "review": review_known,
            "events_applied": events_applied,
            "future_events": future_events,
        }

    def reproduce(self, decision_id: str) -> Dict[str, Any]:
        """
        Invariant 4: Replay != reproduce.
        Re-executes the pinned engine with the snapshot's inputs and ruleset.
        """
        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        snapshot = self.decision_repo.get_snapshot(decision_id)
        if not snapshot:
            raise ValueError(f"Snapshot not found for decision {decision_id}")

        inputs_data = json.loads(snapshot.inputs_json)
        ruleset = RuleSet.from_json(snapshot.ruleset_json)

        inputs = EngineInputs(
            soil_moisture_pct=inputs_data["soil_moisture_pct"],
            temperature_c=inputs_data["temperature_c"],
            rain_probability_pct=inputs_data["rain_probability_pct"],
            forecast_rain_mm=inputs_data["forecast_rain_mm"],
            crop_stage=CropStage(inputs_data["crop_stage"]),
            days_since_last_irrigation=inputs_data["days_since_last_irrigation"],
            application_rate_mm_h=inputs_data["application_rate_mm_h"],
            active_root_zone_mm=inputs_data["active_root_zone_mm"],
        )

        reproduced = IrrigationEngine.recommend(inputs, ruleset)

        recorded = {
            "action": decision.recommended_action.value,
            "duration_h": decision.recommended_duration_h,
            "confidence": decision.confidence,
        }
        reproduced_dict = {
            "action": reproduced.action.value,
            "duration_h": reproduced.duration_h,
            "confidence": reproduced.confidence,
            "fired_rules": reproduced.fired_rules,
        }

        diffs = []
        if recorded["action"] != reproduced_dict["action"]:
            diffs.append(f"action: recorded={recorded['action']} vs reproduced={reproduced_dict['action']}")
        if abs(recorded["duration_h"] - reproduced_dict["duration_h"]) > 0.01:
            diffs.append(f"duration_h: recorded={recorded['duration_h']} vs reproduced={reproduced_dict['duration_h']}")
        if abs(recorded["confidence"] - reproduced_dict["confidence"]) > 0.05:
            diffs.append(f"confidence: recorded={recorded['confidence']} vs reproduced={reproduced_dict['confidence']}")

        current_engine_code_hash = IrrigationEngine.engine_code_sha256()
        code_hash_matched = (current_engine_code_hash == snapshot.engine_code_sha256)

        match = len(diffs) == 0

        # Append REPRODUCTION_CHECKED event to hash chain
        self.recorder.append_event(
            decision_id=decision_id,
            event_type=EventType.REPRODUCTION_CHECKED,
            actor_id="AUDIT_RUNNER",
            actor_role="SYSTEM",
            payload={
                "match": match,
                "recorded": recorded,
                "reproduced": reproduced_dict,
                "diffs": diffs,
                "engine_code_matched": code_hash_matched,
            },
        )

        status_msg = "EXACT_MATCH" if match else "MISMATCH"
        if match and not code_hash_matched:
            status_msg = "MATCH_ENGINE_CODE_CHANGED"

        return {
            "decision_id": decision_id,
            "match": match,
            "status": status_msg,
            "recorded": recorded,
            "reproduced": reproduced_dict,
            "diffs": diffs,
            "engine_code_matched": code_hash_matched,
            "snapshot_sha256": snapshot.snapshot_sha256,
        }
