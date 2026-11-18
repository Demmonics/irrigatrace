"""
DecisionRecorder facade service.
Handles atomic creation of decisions, snapshots, explanations, and hash-chained events.
"""
from __future__ import annotations

import json
import uuid
from typing import Optional, List, Dict, Any, Tuple

from api.irrigatrace.domain.models import (
    FarmPlot,
    SensorReading,
    WeatherSnapshot,
    IrrigationDecision,
    DecisionSnapshot,
    DecisionExplanation,
    DecisionEvent,
    EngineInputs,
    Recommendation,
    RecommendedAction,
    DecisionStatus,
    EventType,
    ExplanationKind,
    compute_hash,
    canonical_json,
)
from api.irrigatrace.domain.engine import RuleSet, IrrigationEngine
from api.irrigatrace.domain.ports import (
    Clock,
    DecisionRepository,
    SensorRepository,
    WeatherRepository,
    PlotRepository,
    EventPublisher,
)


class DecisionRecorder:
    def __init__(
        self,
        decision_repo: DecisionRepository,
        plot_repo: PlotRepository,
        sensor_repo: SensorRepository,
        weather_repo: WeatherRepository,
        clock: Clock,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.decision_repo = decision_repo
        self.plot_repo = plot_repo
        self.sensor_repo = sensor_repo
        self.weather_repo = weather_repo
        self.clock = clock
        self.event_publisher = event_publisher

    def record_new_decision(
        self,
        plot_id: str,
        ruleset: RuleSet,
        sensor_reading_id: Optional[str] = None,
        weather_snapshot_id: Optional[str] = None,
        actor_id: str = "SYSTEM",
        actor_role: str = "SYSTEM",
        occurred_at: Optional[str] = None,
        decision_id: Optional[str] = None,
    ) -> IrrigationDecision:
        plot = self.plot_repo.get_by_id(plot_id)
        if not plot:
            raise ValueError(f"Plot not found: {plot_id}")

        reading = (
            self.sensor_repo.get_by_id(sensor_reading_id)
            if sensor_reading_id
            else self.sensor_repo.get_latest_for_plot(plot_id)
        )
        if not reading:
            raise ValueError(f"No sensor reading found for plot {plot_id}")

        weather = (
            self.weather_repo.get_by_id(weather_snapshot_id)
            if weather_snapshot_id
            else self.weather_repo.get_latest_for_plot(plot_id)
        )
        if not weather:
            raise ValueError(f"No weather snapshot found for plot {plot_id}")

        now = occurred_at or self.clock.now_iso()
        target_date = reading.ts[:10]
        from datetime import datetime
        crop_stage = plot.crop_stage_on(datetime.strptime(target_date, "%Y-%m-%d").date())
        stage_params = ruleset.stage_params[crop_stage.value]

        # Calculate days since last irrigation
        prev_dec = self.decision_repo.get_latest_for_plot(plot_id, before_date=now)
        days_since_last = 7  # default fallback
        if prev_dec and prev_dec.created_at:
            t_prev = datetime.fromisoformat(prev_dec.created_at.replace("Z", "+00:00"))
            t_curr = datetime.fromisoformat(now.replace("Z", "+00:00"))
            days_since_last = max(0, (t_curr - t_prev).days)

        inputs = EngineInputs(
            soil_moisture_pct=reading.soil_moisture_pct,
            temperature_c=reading.temperature_c,
            rain_probability_pct=weather.rain_probability_pct,
            forecast_rain_mm=weather.forecast_rain_mm,
            crop_stage=crop_stage,
            days_since_last_irrigation=days_since_last,
            application_rate_mm_h=plot.application_rate_mm_h,
            active_root_zone_mm=stage_params.active_root_zone_mm,
            sensor_reading_ts=reading.ts,
        )

        rec = IrrigationEngine.recommend(inputs, ruleset)
        year = int(now[:4])
        decision_id = decision_id or self.decision_repo.next_decision_id(year)

        # 1. Create Decision Entity
        decision = IrrigationDecision(
            id=decision_id,
            plot_id=plot_id,
            created_at=now,
            ruleset_version=ruleset.version,
            recommended_action=rec.action,
            recommended_duration_h=rec.duration_h,
            confidence=rec.confidence,
            status=DecisionStatus.PENDING_REVIEW,
        )
        self.decision_repo.save_decision(decision)

        # 2. Create Immutable Snapshot
        snapshot = DecisionSnapshot(
            decision_id=decision_id,
            sensor_reading_id=reading.id,
            weather_snapshot_id=weather.id,
            inputs_json=canonical_json(inputs.to_dict()),
            ruleset_json=ruleset.to_json(),
            engine_version=IrrigationEngine.VERSION,
            engine_code_sha256=IrrigationEngine.engine_code_sha256(),
        )
        self.decision_repo.save_snapshot(snapshot)
        decision.snapshot = snapshot

        # 3. Create Deterministic Explanation
        expl_data = IrrigationEngine.build_deterministic_explanation(inputs, ruleset, rec)
        expl_id = f"EXP-{uuid.uuid4().hex[:8]}"
        explanation = DecisionExplanation(
            id=expl_id,
            decision_id=decision_id,
            kind=ExplanationKind.DETERMINISTIC,
            content_json=canonical_json(expl_data),
            provenance_json=canonical_json({
                "source": "deterministic_engine",
                "ruleset_version": ruleset.version,
                "engine_version": IrrigationEngine.VERSION,
            }),
            created_at=now,
        )
        self.decision_repo.save_explanation(explanation)
        decision.explanation = explanation

        # 4. Hash Chain Events
        # GENESIS = sha256("GENESIS:" + decision_id)
        genesis_hash = compute_hash(f"GENESIS:{decision_id}")
        current_prev_hash = genesis_hash

        events_to_create = [
            (
                EventType.SENSOR_RECEIVED,
                actor_id,
                actor_role,
                now,
                {
                    "reading_id": reading.id,
                    "soil_moisture_pct": reading.soil_moisture_pct,
                    "temperature_c": reading.temperature_c,
                    "source": reading.source,
                    "quality_flag": reading.quality_flag,
                },
            ),
            (
                EventType.WEATHER_CAPTURED,
                actor_id,
                actor_role,
                now,
                {
                    "snapshot_id": weather.id,
                    "rain_probability_pct": weather.rain_probability_pct,
                    "forecast_rain_mm": weather.forecast_rain_mm,
                    "horizon_h": weather.horizon_h,
                    "source": weather.source,
                },
            ),
            (
                EventType.RECOMMENDATION_GENERATED,
                "ENGINE",
                "SYSTEM",
                now,
                {
                    "action": rec.action.value,
                    "duration_h": rec.duration_h,
                    "confidence": rec.confidence,
                    "fired_rules": rec.fired_rules,
                    "ruleset_version": ruleset.version,
                    "engine_version": IrrigationEngine.VERSION,
                },
            ),
            (
                EventType.EXPLANATION_ATTACHED,
                "ENGINE",
                "SYSTEM",
                now,
                {
                    "explanation_id": expl_id,
                    "kind": "DETERMINISTIC",
                },
            ),
        ]

        seq = 1
        for ev_type, ev_actor, ev_role, ev_time, payload in events_to_create:
            p_json = canonical_json(payload)
            ev_hash = DecisionEvent.calculate_hash(
                decision_id=decision_id,
                seq=seq,
                event_type=ev_type.value,
                actor_id=ev_actor,
                actor_role=ev_role,
                occurred_at=ev_time,
                payload_json=p_json,
                prev_hash=current_prev_hash,
            )
            event = DecisionEvent(
                seq=seq,
                decision_id=decision_id,
                event_type=ev_type,
                actor_id=ev_actor,
                actor_role=ev_role,
                occurred_at=ev_time,
                payload_json=p_json,
                prev_hash=current_prev_hash,
                event_hash=ev_hash,
            )
            self.decision_repo.save_event(event)
            decision.events.append(event)
            if self.event_publisher:
                self.event_publisher.publish(event)
            current_prev_hash = ev_hash
            seq += 1

        return decision

    def append_event(
        self,
        decision_id: str,
        event_type: EventType,
        actor_id: str,
        actor_role: str,
        payload: Dict[str, Any],
        occurred_at: Optional[str] = None,
    ) -> DecisionEvent:
        events = self.decision_repo.get_events(decision_id)
        if not events:
            prev_hash = compute_hash(f"GENESIS:{decision_id}")
            seq = 1
        else:
            prev_hash = events[-1].event_hash
            seq = len(events) + 1

        now = occurred_at or self.clock.now_iso()
        p_json = canonical_json(payload)
        ev_hash = DecisionEvent.calculate_hash(
            decision_id=decision_id,
            seq=seq,
            event_type=event_type.value,
            actor_id=actor_id,
            actor_role=actor_role,
            occurred_at=now,
            payload_json=p_json,
            prev_hash=prev_hash,
        )
        event = DecisionEvent(
            seq=seq,
            decision_id=decision_id,
            event_type=event_type,
            actor_id=actor_id,
            actor_role=actor_role,
            occurred_at=now,
            payload_json=p_json,
            prev_hash=prev_hash,
            event_hash=ev_hash,
        )
        self.decision_repo.save_event(event)
        if self.event_publisher:
            self.event_publisher.publish(event)
        return event
