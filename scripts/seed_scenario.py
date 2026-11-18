"""
Idempotent seed data script for IrrigaTrace.
Populates demo users, farm plots near Sameerwadi, Karnataka,
the exact Hero scenario (IRR-2026-018 and IRR-2026-014),
and realistic bulk decisions across 6 weeks with real hash-chained events.
"""
from __future__ import annotations

import os
import sys
import json
import uuid
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.irrigatrace.infra.db.connection import get_db
from api.irrigatrace.infra.db.repositories import (
    SqlitePlotRepository,
    SqliteSensorRepository,
    SqliteWeatherRepository,
    SqliteDecisionRepository,
    SystemClock,
)
from api.irrigatrace.domain.models import (
    FarmPlot,
    SensorReading,
    WeatherSnapshot,
    IrrigationDecision,
    DecisionSnapshot,
    DecisionExplanation,
    DecisionEvent,
    HumanReview,
    OutcomeRecord,
    ReviewAction,
    RecommendedAction,
    DecisionStatus,
    EventType,
    ExplanationKind,
    compute_hash,
    canonical_json,
)
from api.irrigatrace.domain.engine import RuleSet, IrrigationEngine
from api.irrigatrace.services.recorder import DecisionRecorder


class StaticClock:
    def __init__(self, current_time: str):
        self.current_time = current_time

    def now_iso(self) -> str:
        return self.current_time


def run_seed():
    db_file = Path("irrigatrace.db")
    if db_file.exists():
        try:
            db_file.unlink()
        except Exception:
            pass

    from api.irrigatrace.infra.db.connection import Database
    db = Database("irrigatrace.db")
    conn = db.get_connection()

    # 1. Insert Users
    users_data = [
        ("user-sup-01", "Ramesh Patil (Supervisor)", "SUPERVISOR"),
        ("user-sup-02", "Anita R. (Supervisor)", "SUPERVISOR"),
        ("user-adm-01", "Anil Deshmukh (Admin)", "ADMIN"),
        ("user-aud-01", "Dr. Sunita Rao (Auditor)", "AUDITOR"),
    ]
    for uid, name, role in users_data:
        conn.execute("INSERT INTO users (id, name, role) VALUES (?, ?, ?)", (uid, name, role))
    conn.commit()

    plot_repo = SqlitePlotRepository(db)
    sensor_repo = SqliteSensorRepository(db)
    weather_repo = SqliteWeatherRepository(db)
    decision_repo = SqliteDecisionRepository(db)

    # 2. Insert Farm Plots (Near Sameerwadi, Karnataka)
    # Planting dates: 2026-05-15 (Grand Growth), 2026-08-01 (Tillering), 2026-01-10 (Maturity)
    plots_data = [
        ("plot-104", "SG-104", "North Plateau A", 4.2, "Clay Loam", "2026-05-15", 14.0),
        ("plot-107", "SG-107", "North Plateau B", 3.8, "Sandy Clay", "2026-05-20", 12.5),
        ("plot-112", "SG-112", "Canal Reach East", 5.5, "Medium Black", "2026-08-01", 15.0),
        ("plot-118", "SG-118", "Canal Reach West", 4.0, "Deep Black Clay", "2026-08-05", 14.0),
        ("plot-121", "SG-121", "Terrace Basin 1", 2.9, "Red Loam", "2026-01-10", 11.0),
        ("plot-125", "SG-125", "Terrace Basin 2", 3.4, "Alluvial Silt", "2026-07-15", 13.5),
    ]
    for pid, code, name, area, soil, pdate, rate in plots_data:
        plot_repo.save(FarmPlot(
            id=pid,
            code=code,
            name=name,
            area_ha=area,
            soil_type=soil,
            crop="sugarcane",
            variety="Co 86032",
            planting_date=pdate,
            irrigation_method="DRIP",
            application_rate_mm_h=rate,
            geojson=json.dumps({"type": "Polygon", "coordinates": [[[75.1, 16.2], [75.12, 16.2], [75.12, 16.22], [75.1, 16.22], [75.1, 16.2]]]}),
        ))

    # Load ruleset
    rules_path = Path(__file__).resolve().parent.parent / "api" / "irrigatrace" / "rules" / "rules-v1.4.2.yaml"
    with open(rules_path, "r", encoding="utf-8") as f:
        ruleset = RuleSet.from_yaml(f.read())

    # 3. Create Hero Decisions (Doc 14)
    # Decision IRR-2026-014 (Previous on SG-104: moisture 29%, temp 29C, rain 72% -> DEFER_RAIN)
    clock14 = StaticClock("2026-10-18T08:30:00Z")
    rec14 = DecisionRecorder(decision_repo, plot_repo, sensor_repo, weather_repo, clock14)

    s14 = SensorReading(id="read-hero-014", plot_id="plot-104", ts="2026-10-18T08:28:00Z", soil_moisture_pct=29.0, temperature_c=29.0, source="SIMULATED")
    sensor_repo.save(s14)
    w14 = WeatherSnapshot(id="wsnap-hero-014", plot_id="plot-104", captured_at="2026-10-18T08:29:00Z", rain_probability_pct=72.0, forecast_rain_mm=18.0, horizon_h=48, source="SIMULATED")
    weather_repo.save(w14)

    dec14 = rec14.record_new_decision(
        plot_id="plot-104",
        ruleset=ruleset,
        sensor_reading_id=s14.id,
        weather_snapshot_id=w14.id,
        actor_id="SYSTEM",
        actor_role="SYSTEM",
        occurred_at="2026-10-18T08:30:00Z",
        decision_id="IRR-2026-014",
    )

    # Hero Scenario: Decision IRR-2026-018
    # 09:41:58 sensor (21%, 33C) · 09:42:01 weather (12%) · 09:42:07 recommendation IRRIGATE 2.8h · 10:03:21 review opened · 10:05:47 MODIFIED -> 2.0h
    s18 = SensorReading(id="read-hero-018", plot_id="plot-104", ts="2026-10-24T09:41:58Z", soil_moisture_pct=21.0, temperature_c=33.0, source="SIMULATED")
    sensor_repo.save(s18)
    w18 = WeatherSnapshot(id="wsnap-hero-018", plot_id="plot-104", captured_at="2026-10-24T09:42:01Z", rain_probability_pct=12.0, forecast_rain_mm=0.0, horizon_h=48, source="SIMULATED")
    weather_repo.save(w18)

    clock18 = StaticClock("2026-10-24T09:42:07Z")
    rec18 = DecisionRecorder(decision_repo, plot_repo, sensor_repo, weather_repo, clock18)
    dec18 = rec18.record_new_decision(
        plot_id="plot-104",
        ruleset=ruleset,
        sensor_reading_id=s18.id,
        weather_snapshot_id=w18.id,
        actor_id="SYSTEM",
        actor_role="SYSTEM",
        occurred_at="2026-10-24T09:42:07Z",
        decision_id="IRR-2026-018",
    )

    # Re-chain events for IRR-2026-018
    # 1. Review opened at 10:03:21
    rec18.append_event(
        decision_id="IRR-2026-018",
        event_type=EventType.REVIEW_OPENED,
        actor_id="user-sup-01",
        actor_role="SUPERVISOR",
        payload={"reviewer_id": "user-sup-01", "reviewer_name": "Ramesh Patil"},
        occurred_at="2026-10-24T10:03:21Z",
    )

    # 2. Review modified at 10:05:47
    rev18 = HumanReview(
        id="rev-hero-018",
        decision_id="IRR-2026-018",
        reviewer_id="user-sup-01",
        action=ReviewAction.MODIFY,
        final_action=RecommendedAction.IRRIGATE,
        final_duration_h=2.0,
        reason_code="LOCAL_FIELD_CONDITIONS",
        reason_text="Local field conditions suggested a shorter irrigation duration.",
        created_at="2026-10-24T10:05:47Z",
    )
    decision_repo.save_review(rev18)

    rec18.append_event(
        decision_id="IRR-2026-018",
        event_type=EventType.REVIEW_MODIFIED,
        actor_id="user-sup-01",
        actor_role="SUPERVISOR",
        payload={
            "review_id": rev18.id,
            "action": "MODIFY",
            "reason_code": "LOCAL_FIELD_CONDITIONS",
            "reason_text": rev18.reason_text,
            "final_action": "IRRIGATE",
            "final_duration_h": 2.0,
        },
        occurred_at="2026-10-24T10:05:47Z",
    )

    # 3. Finalized at 10:06:00
    rec18.append_event(
        decision_id="IRR-2026-018",
        event_type=EventType.DECISION_FINALIZED,
        actor_id="user-sup-01",
        actor_role="SUPERVISOR",
        payload={"final_action": "IRRIGATE", "final_duration_h": 2.0, "source": "HUMAN_OVERRIDDEN"},
        occurred_at="2026-10-24T10:06:00Z",
    )
    decision_repo.update_status("IRR-2026-018", DecisionStatus.FINALIZED)

    # 4. Action recorded next day
    rec18.append_event(
        decision_id="IRR-2026-018",
        event_type=EventType.ACTION_RECORDED,
        actor_id="user-sup-01",
        actor_role="SUPERVISOR",
        payload={"actual_duration_h": 2.0, "executed_at": "2026-10-25T06:00:00Z"},
        occurred_at="2026-10-25T06:15:00Z",
    )
    decision_repo.update_status("IRR-2026-018", DecisionStatus.ACTION_RECORDED)

    # 5. Outcome recorded
    out18 = OutcomeRecord(
        id="out-hero-018",
        decision_id="IRR-2026-018",
        recorded_by="user-sup-01",
        recorded_at="2026-10-26T08:00:00Z",
        actual_duration_h=2.0,
        soil_moisture_after_pct=31.5,
        actual_rainfall_mm=0.0,
        water_stress_observed=0,
        crop_health_note="Good cane vigor, no waterlogging.",
        notes="Soil moisture replenished to 31.5% target band.",
    )
    decision_repo.save_outcome(out18)

    rec18.append_event(
        decision_id="IRR-2026-018",
        event_type=EventType.OUTCOME_RECORDED,
        actor_id="user-sup-01",
        actor_role="SUPERVISOR",
        payload={
            "outcome_id": out18.id,
            "soil_moisture_after_pct": 31.5,
            "water_stress_observed": 0,
        },
        occurred_at="2026-10-26T08:00:00Z",
    )
    decision_repo.update_status("IRR-2026-018", DecisionStatus.OUTCOME_RECORDED)

    # Attach LLM narrative for IRR-2026-018
    expl_narr = DecisionExplanation(
        id="exp-narr-018",
        decision_id="IRR-2026-018",
        kind=ExplanationKind.LLM_NARRATIVE,
        content_json=canonical_json({
            "narrative": "Recommend IRRIGATE for 2.8 hours. Soil moisture 21% is below the Grand Growth trigger of 25.9% with ambient temperature at 33C and rain probability at 12%.",
            "key_points": [
                "Soil moisture 21% is below trigger threshold 25.9%",
                "Temperature 33C adds +0.9pp heat uplift",
                "Rain probability 12% is well below deferral threshold"
            ]
        }),
        provenance_json=canonical_json({
            "source": "ollama",
            "model": "qwen2.5:3b",
            "validated": True,
            "latency_ms": 1420,
        }),
        created_at="2026-10-24T09:42:15Z",
    )
    decision_repo.save_explanation(expl_narr)

    # 4. Generate Bulk Decisions (~125 decisions across 6 weeks)
    random.seed(42)
    start_date = datetime(2026, 9, 10, 8, 0, 0, tzinfo=timezone.utc)
    all_plots = plot_repo.list_all()

    reason_choices = [
        "LOCAL_FIELD_CONDITIONS",
        "RECENT_RAIN_OBSERVED",
        "PUMP_OR_POWER_CONSTRAINT",
        "WATER_AVAILABILITY",
        "SENSOR_DOUBT",
        "CROP_OBSERVATION",
    ]

    for i in range(1, 126):
        plot = random.choice(all_plots)
        time_offset = timedelta(days=random.uniform(0, 42), hours=random.uniform(0, 10))
        dec_time = (start_date + time_offset).isoformat()

        # Randomize realistic sensor conditions
        moist = round(random.uniform(17.0, 32.0), 1)
        temp = round(random.uniform(24.0, 36.0), 1)
        rain_prob = round(random.uniform(5.0, 75.0), 1)
        rain_mm = round(random.uniform(0.0, 25.0), 1) if rain_prob > 50 else 0.0

        sr = SensorReading(
            id=f"read-bulk-{i:03d}",
            plot_id=plot.id,
            ts=dec_time,
            soil_moisture_pct=moist,
            temperature_c=temp,
            source="SIMULATED",
        )
        sensor_repo.save(sr)

        ws = WeatherSnapshot(
            id=f"wsnap-bulk-{i:03d}",
            plot_id=plot.id,
            captured_at=dec_time,
            rain_probability_pct=rain_prob,
            forecast_rain_mm=rain_mm,
            horizon_h=48,
            source="SIMULATED",
        )
        weather_repo.save(ws)

        clk = StaticClock(dec_time)
        recorder = DecisionRecorder(decision_repo, plot_repo, sensor_repo, weather_repo, clk)
        dec = recorder.record_new_decision(
            plot_id=plot.id,
            ruleset=ruleset,
            sensor_reading_id=sr.id,
            weather_snapshot_id=ws.id,
            actor_id="SYSTEM",
            actor_role="SYSTEM",
            occurred_at=dec_time,
        )

        # Decide review action (~20% modified, ~5% rejected, ~65% approved, ~10% pending)
        roll = random.random()
        if roll < 0.10:
            # Leave pending
            continue
        elif roll < 0.75:
            # Approved
            rev_time = (datetime.fromisoformat(dec_time) + timedelta(minutes=random.randint(5, 45))).isoformat()
            rev = HumanReview(
                id=f"rev-bulk-{i:03d}",
                decision_id=dec.id,
                reviewer_id="user-sup-01",
                action=ReviewAction.APPROVE,
                final_action=dec.recommended_action,
                final_duration_h=dec.recommended_duration_h,
                created_at=rev_time,
            )
            decision_repo.save_review(rev)
            recorder.append_event(
                decision_id=dec.id,
                event_type=EventType.REVIEW_APPROVED,
                actor_id="user-sup-01",
                actor_role="SUPERVISOR",
                payload={"action": "APPROVE", "final_action": dec.recommended_action.value},
                occurred_at=rev_time,
            )
            recorder.append_event(
                decision_id=dec.id,
                event_type=EventType.DECISION_FINALIZED,
                actor_id="user-sup-01",
                actor_role="SUPERVISOR",
                payload={"final_action": dec.recommended_action.value, "source": "HUMAN_APPROVED"},
                occurred_at=rev_time,
            )
            decision_repo.update_status(dec.id, DecisionStatus.FINALIZED)
        elif roll < 0.95:
            # Modified
            rev_time = (datetime.fromisoformat(dec_time) + timedelta(minutes=random.randint(5, 45))).isoformat()
            mod_dur = max(0.5, round(dec.recommended_duration_h + random.choice([-0.8, -0.5, 0.5, 0.8]), 1))
            code = random.choice(reason_choices)
            rev = HumanReview(
                id=f"rev-bulk-{i:03d}",
                decision_id=dec.id,
                reviewer_id="user-sup-02",
                action=ReviewAction.MODIFY,
                final_action=RecommendedAction.IRRIGATE,
                final_duration_h=mod_dur,
                reason_code=code,
                reason_text=f"Modified duration to {mod_dur}h due to {code.lower().replace('_', ' ')}.",
                created_at=rev_time,
            )
            decision_repo.save_review(rev)
            recorder.append_event(
                decision_id=dec.id,
                event_type=EventType.REVIEW_MODIFIED,
                actor_id="user-sup-02",
                actor_role="SUPERVISOR",
                payload={"action": "MODIFY", "final_action": "IRRIGATE", "final_duration_h": mod_dur, "reason_code": code},
                occurred_at=rev_time,
            )
            recorder.append_event(
                decision_id=dec.id,
                event_type=EventType.DECISION_FINALIZED,
                actor_id="user-sup-02",
                actor_role="SUPERVISOR",
                payload={"final_action": "IRRIGATE", "final_duration_h": mod_dur, "source": "HUMAN_OVERRIDDEN"},
                occurred_at=rev_time,
            )
            decision_repo.update_status(dec.id, DecisionStatus.FINALIZED)
        else:
            # Rejected
            rev_time = (datetime.fromisoformat(dec_time) + timedelta(minutes=random.randint(5, 45))).isoformat()
            code = random.choice(["SENSOR_DOUBT", "RECENT_RAIN_OBSERVED"])
            rev = HumanReview(
                id=f"rev-bulk-{i:03d}",
                decision_id=dec.id,
                reviewer_id="user-sup-01",
                action=ReviewAction.REJECT,
                final_action=RecommendedAction.WAIT,
                final_duration_h=0.0,
                reason_code=code,
                reason_text=f"Rejected recommendation: {code.lower().replace('_', ' ')}.",
                created_at=rev_time,
            )
            decision_repo.save_review(rev)
            recorder.append_event(
                decision_id=dec.id,
                event_type=EventType.REVIEW_REJECTED,
                actor_id="user-sup-01",
                actor_role="SUPERVISOR",
                payload={"action": "REJECT", "final_action": "WAIT", "reason_code": code},
                occurred_at=rev_time,
            )
            recorder.append_event(
                decision_id=dec.id,
                event_type=EventType.DECISION_FINALIZED,
                actor_id="user-sup-01",
                actor_role="SUPERVISOR",
                payload={"final_action": "WAIT", "source": "HUMAN_OVERRIDDEN"},
                occurred_at=rev_time,
            )
            decision_repo.update_status(dec.id, DecisionStatus.FINALIZED)

        # Record action & outcome for older finalized decisions (~70% of finalized)
        if random.random() < 0.70:
            act_time = (datetime.fromisoformat(dec_time) + timedelta(hours=14)).isoformat()
            recorder.append_event(
                decision_id=dec.id,
                event_type=EventType.ACTION_RECORDED,
                actor_id="user-sup-01",
                actor_role="SUPERVISOR",
                payload={"actual_duration_h": dec.recommended_duration_h, "executed_at": act_time},
                occurred_at=act_time,
            )
            decision_repo.update_status(dec.id, DecisionStatus.ACTION_RECORDED)

            out_time = (datetime.fromisoformat(dec_time) + timedelta(days=2)).isoformat()
            out = OutcomeRecord(
                id=f"out-bulk-{i:03d}",
                decision_id=dec.id,
                recorded_by="user-sup-01",
                recorded_at=out_time,
                actual_duration_h=dec.recommended_duration_h,
                soil_moisture_after_pct=round(moist + random.uniform(6.0, 12.0), 1) if dec.recommended_action == RecommendedAction.IRRIGATE else moist,
                water_stress_observed=0,
                crop_health_note="Normal vigor observed",
            )
            decision_repo.save_outcome(out)
            recorder.append_event(
                decision_id=dec.id,
                event_type=EventType.OUTCOME_RECORDED,
                actor_id="user-sup-01",
                actor_role="SUPERVISOR",
                payload={"outcome_id": out.id, "water_stress_observed": 0},
                occurred_at=out_time,
            )
            decision_repo.update_status(dec.id, DecisionStatus.OUTCOME_RECORDED)

    conn.close()
    print("Seed complete: populated users, plots, hero scenario IRR-2026-018 & IRR-2026-014, and bulk decisions.")


if __name__ == "__main__":
    run_seed()
