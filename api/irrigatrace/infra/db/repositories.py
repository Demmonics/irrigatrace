"""
SQLite implementations of domain repositories.
Strictly respects DDL schema and invariants.
"""
from __future__ import annotations

import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from api.irrigatrace.domain.models import (
    FarmPlot,
    SensorReading,
    WeatherSnapshot,
    IrrigationDecision,
    DecisionSnapshot,
    DecisionExplanation,
    HumanReview,
    DecisionEvent,
    OutcomeRecord,
    DecisionStatus,
    RecommendedAction,
    ReviewAction,
    EventType,
    ExplanationKind,
)
from api.irrigatrace.domain.ports import (
    Clock,
    PlotRepository,
    SensorRepository,
    WeatherRepository,
    DecisionRepository,
)
from api.irrigatrace.infra.db.connection import Database


class SystemClock(Clock):
    def now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()


class SqlitePlotRepository(PlotRepository):
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, plot_id: str) -> Optional[FarmPlot]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM farm_plots WHERE id = ?", (plot_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_plot(row)
        finally:
            conn.close()

    def get_by_code(self, code: str) -> Optional[FarmPlot]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM farm_plots WHERE code = ?", (code,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_plot(row)
        finally:
            conn.close()

    def list_all(self) -> List[FarmPlot]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM farm_plots ORDER BY code ASC")
            return [self._row_to_plot(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def save(self, plot: FarmPlot) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO farm_plots (id, code, name, area_ha, soil_type, crop, variety, planting_date, irrigation_method, application_rate_mm_h, geojson)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name, area_ha=excluded.area_ha, soil_type=excluded.soil_type,
                    crop=excluded.crop, variety=excluded.variety, planting_date=excluded.planting_date,
                    irrigation_method=excluded.irrigation_method, application_rate_mm_h=excluded.application_rate_mm_h,
                    geojson=excluded.geojson
                """,
                (
                    plot.id, plot.code, plot.name, plot.area_ha, plot.soil_type, plot.crop,
                    plot.variety, plot.planting_date, plot.irrigation_method, plot.application_rate_mm_h,
                    plot.geojson,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _row_to_plot(self, r: sqlite3.Row) -> FarmPlot:
        return FarmPlot(
            id=r["id"],
            code=r["code"],
            name=r["name"],
            area_ha=float(r["area_ha"]),
            soil_type=r["soil_type"],
            crop=r["crop"],
            variety=r["variety"],
            planting_date=r["planting_date"],
            irrigation_method=r["irrigation_method"],
            application_rate_mm_h=float(r["application_rate_mm_h"]),
            geojson=r["geojson"],
        )


class SqliteSensorRepository(SensorRepository):
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, reading_id: str) -> Optional[SensorReading]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM sensor_readings WHERE id = ?", (reading_id,))
            row = cursor.fetchone()
            return self._row_to_reading(row) if row else None
        finally:
            conn.close()

    def get_latest_for_plot(self, plot_id: str) -> Optional[SensorReading]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM sensor_readings WHERE plot_id = ? ORDER BY ts DESC LIMIT 1",
                (plot_id,),
            )
            row = cursor.fetchone()
            return self._row_to_reading(row) if row else None
        finally:
            conn.close()

    def save(self, reading: SensorReading) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO sensor_readings (id, plot_id, ts, soil_moisture_pct, temperature_c, source, quality_flag)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (
                    reading.id, reading.plot_id, reading.ts, reading.soil_moisture_pct,
                    reading.temperature_c, reading.source, reading.quality_flag,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _row_to_reading(self, r: sqlite3.Row) -> SensorReading:
        return SensorReading(
            id=r["id"],
            plot_id=r["plot_id"],
            ts=r["ts"],
            soil_moisture_pct=float(r["soil_moisture_pct"]),
            temperature_c=float(r["temperature_c"]),
            source=r["source"],
            quality_flag=r["quality_flag"],
        )


class SqliteWeatherRepository(WeatherRepository):
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, snapshot_id: str) -> Optional[WeatherSnapshot]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM weather_snapshots WHERE id = ?", (snapshot_id,))
            row = cursor.fetchone()
            return self._row_to_snapshot(row) if row else None
        finally:
            conn.close()

    def get_latest_for_plot(self, plot_id: str) -> Optional[WeatherSnapshot]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM weather_snapshots WHERE plot_id = ? ORDER BY captured_at DESC LIMIT 1",
                (plot_id,),
            )
            row = cursor.fetchone()
            return self._row_to_snapshot(row) if row else None
        finally:
            conn.close()

    def save(self, snapshot: WeatherSnapshot) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO weather_snapshots (id, plot_id, captured_at, rain_probability_pct, forecast_rain_mm, horizon_h, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (
                    snapshot.id, snapshot.plot_id, snapshot.captured_at, snapshot.rain_probability_pct,
                    snapshot.forecast_rain_mm, snapshot.horizon_h, snapshot.source,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _row_to_snapshot(self, r: sqlite3.Row) -> WeatherSnapshot:
        return WeatherSnapshot(
            id=r["id"],
            plot_id=r["plot_id"],
            captured_at=r["captured_at"],
            rain_probability_pct=float(r["rain_probability_pct"]),
            forecast_rain_mm=float(r["forecast_rain_mm"]),
            horizon_h=int(r["horizon_h"]),
            source=r["source"],
        )


class SqliteDecisionRepository(DecisionRepository):
    def __init__(self, db: Database):
        self.db = db

    def next_decision_id(self, year: int) -> str:
        conn = self.db.get_connection()
        try:
            prefix = f"IRR-{year}-"
            cursor = conn.execute(
                "SELECT id FROM irrigation_decisions WHERE id LIKE ? ORDER BY id DESC LIMIT 1",
                (prefix + "%",),
            )
            row = cursor.fetchone()
            if not row:
                return f"IRR-{year}-001"
            last_seq = int(row["id"].split("-")[-1])
            return f"IRR-{year}-{last_seq + 1:03d}"
        finally:
            conn.close()

    def get_by_id(self, decision_id: str) -> Optional[IrrigationDecision]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM irrigation_decisions WHERE id = ?", (decision_id,))
            row = cursor.fetchone()
            if not row:
                return None
            dec = self._row_to_decision(row)
            dec.snapshot = self.get_snapshot(decision_id)
            explanations = self.get_explanations(decision_id)
            dec.explanation = explanations[0] if explanations else None
            dec.reviews = self.get_reviews(decision_id)
            dec.events = self.get_events(decision_id)
            return dec
        finally:
            conn.close()

    def get_snapshot(self, decision_id: str) -> Optional[DecisionSnapshot]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM decision_snapshots WHERE decision_id = ?", (decision_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return DecisionSnapshot(
                decision_id=row["decision_id"],
                sensor_reading_id=row["sensor_reading_id"],
                weather_snapshot_id=row["weather_snapshot_id"],
                inputs_json=row["inputs_json"],
                ruleset_json=row["ruleset_json"],
                engine_version=row["engine_version"],
                engine_code_sha256=row["engine_code_sha256"],
                snapshot_sha256=row["snapshot_sha256"],
            )
        finally:
            conn.close()

    def get_explanations(self, decision_id: str) -> List[DecisionExplanation]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM decision_explanations WHERE decision_id = ? ORDER BY created_at ASC", (decision_id,))
            return [
                DecisionExplanation(
                    id=r["id"],
                    decision_id=r["decision_id"],
                    kind=ExplanationKind(r["kind"]),
                    language=r["language"],
                    content_json=r["content_json"],
                    provenance_json=r["provenance_json"],
                    created_at=r["created_at"],
                )
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_reviews(self, decision_id: str) -> List[HumanReview]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM human_reviews WHERE decision_id = ? ORDER BY created_at ASC", (decision_id,))
            return [
                HumanReview(
                    id=r["id"],
                    decision_id=r["decision_id"],
                    reviewer_id=r["reviewer_id"],
                    action=ReviewAction(r["action"]),
                    final_action=RecommendedAction(r["final_action"]),
                    final_duration_h=float(r["final_duration_h"]),
                    created_at=r["created_at"],
                    reason_code=r["reason_code"],
                    reason_text=r["reason_text"],
                )
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_events(self, decision_id: str) -> List[DecisionEvent]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM decision_events WHERE decision_id = ? ORDER BY seq ASC", (decision_id,))
            return [
                DecisionEvent(
                    seq=r["seq"],
                    decision_id=r["decision_id"],
                    event_type=EventType(r["event_type"]),
                    actor_id=r["actor_id"],
                    actor_role=r["actor_role"],
                    occurred_at=r["occurred_at"],
                    payload_json=r["payload_json"],
                    prev_hash=r["prev_hash"],
                    event_hash=r["event_hash"],
                )
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_outcome(self, decision_id: str) -> Optional[OutcomeRecord]:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM outcome_records WHERE decision_id = ? ORDER BY recorded_at DESC LIMIT 1", (decision_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return OutcomeRecord(
                id=row["id"],
                decision_id=row["decision_id"],
                recorded_by=row["recorded_by"],
                recorded_at=row["recorded_at"],
                actual_duration_h=float(row["actual_duration_h"]) if row["actual_duration_h"] is not None else None,
                soil_moisture_after_pct=float(row["soil_moisture_after_pct"]) if row["soil_moisture_after_pct"] is not None else None,
                actual_rainfall_mm=float(row["actual_rainfall_mm"]) if row["actual_rainfall_mm"] is not None else None,
                water_stress_observed=row["water_stress_observed"],
                crop_health_note=row["crop_health_note"],
                notes=row["notes"],
            )
        finally:
            conn.close()

    def get_latest_for_plot(self, plot_id: str, before_date: Optional[str] = None) -> Optional[IrrigationDecision]:
        conn = self.db.get_connection()
        try:
            if before_date:
                cursor = conn.execute(
                    "SELECT * FROM irrigation_decisions WHERE plot_id = ? AND created_at < ? ORDER BY created_at DESC LIMIT 1",
                    (plot_id, before_date),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM irrigation_decisions WHERE plot_id = ? ORDER BY created_at DESC LIMIT 1",
                    (plot_id,),
                )
            row = cursor.fetchone()
            return self.get_by_id(row["id"]) if row else None
        finally:
            conn.close()

    def list_decisions(
        self,
        plot_code: Optional[str] = None,
        status: Optional[List[str]] = None,
        overridden: Optional[bool] = None,
        ruleset_version: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        action: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[IrrigationDecision]:
        conn = self.db.get_connection()
        try:
            query = """
                SELECT d.* FROM irrigation_decisions d
                JOIN farm_plots p ON d.plot_id = p.id
                WHERE 1=1
            """
            params: List[Any] = []
            if plot_code:
                query += " AND p.code = ?"
                params.append(plot_code)
            if status:
                placeholders = ",".join("?" for _ in status)
                query += f" AND d.status IN ({placeholders})"
                params.extend(status)
            if ruleset_version:
                query += " AND d.ruleset_version = ?"
                params.append(ruleset_version)
            if date_from:
                query += " AND d.created_at >= ?"
                params.append(date_from)
            if date_to:
                query += " AND d.created_at <= ?"
                params.append(date_to)
            if action:
                placeholders = ",".join("?" for _ in action)
                query += f" AND d.recommended_action IN ({placeholders})"
                params.extend(action)
            if overridden is True:
                query += " AND d.id IN (SELECT decision_id FROM human_reviews WHERE action != 'APPROVE')"
            elif overridden is False:
                query += " AND d.id NOT IN (SELECT decision_id FROM human_reviews WHERE action != 'APPROVE')"

            query += " ORDER BY d.created_at DESC LIMIT ? OFFSET ?"
            offset = (page - 1) * page_size
            params.extend([page_size, offset])

            cursor = conn.execute(query, params)
            decisions = []
            for r in cursor.fetchall():
                dec = self._row_to_decision(r)
                dec.reviews = self.get_reviews(dec.id)
                decisions.append(dec)
            return decisions
        finally:
            conn.close()

    def count_decisions(
        self,
        plot_code: Optional[str] = None,
        status: Optional[List[str]] = None,
        overridden: Optional[bool] = None,
    ) -> int:
        conn = self.db.get_connection()
        try:
            query = "SELECT count(*) as total FROM irrigation_decisions d JOIN farm_plots p ON d.plot_id = p.id WHERE 1=1"
            params: List[Any] = []
            if plot_code:
                query += " AND p.code = ?"
                params.append(plot_code)
            if status:
                placeholders = ",".join("?" for _ in status)
                query += f" AND d.status IN ({placeholders})"
                params.extend(status)
            if overridden is True:
                query += " AND d.id IN (SELECT decision_id FROM human_reviews WHERE action != 'APPROVE')"
            elif overridden is False:
                query += " AND d.id NOT IN (SELECT decision_id FROM human_reviews WHERE action != 'APPROVE')"
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return row["total"] if row else 0
        finally:
            conn.close()

    def save_decision(self, decision: IrrigationDecision) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO irrigation_decisions (id, plot_id, created_at, ruleset_version, recommended_action, recommended_duration_h, confidence, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.id, decision.plot_id, decision.created_at, decision.ruleset_version,
                    decision.recommended_action.value, decision.recommended_duration_h, decision.confidence,
                    decision.status.value,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def update_status(self, decision_id: str, status: DecisionStatus) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                "UPDATE irrigation_decisions SET status = ? WHERE id = ?",
                (status.value, decision_id),
            )
            conn.commit()
        finally:
            conn.close()

    def save_snapshot(self, snapshot: DecisionSnapshot) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO decision_snapshots (decision_id, sensor_reading_id, weather_snapshot_id, inputs_json, ruleset_json, engine_version, engine_code_sha256, snapshot_sha256)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.decision_id, snapshot.sensor_reading_id, snapshot.weather_snapshot_id,
                    snapshot.inputs_json, snapshot.ruleset_json, snapshot.engine_version,
                    snapshot.engine_code_sha256, snapshot.snapshot_sha256,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def save_explanation(self, explanation: DecisionExplanation) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO decision_explanations (id, decision_id, kind, language, content_json, provenance_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    explanation.id, explanation.decision_id, explanation.kind.value,
                    explanation.language, explanation.content_json, explanation.provenance_json,
                    explanation.created_at,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def save_review(self, review: HumanReview) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO human_reviews (id, decision_id, reviewer_id, action, reason_code, reason_text, final_action, final_duration_h, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review.id, review.decision_id, review.reviewer_id, review.action.value,
                    review.reason_code, review.reason_text, review.final_action.value,
                    review.final_duration_h, review.created_at,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def save_event(self, event: DecisionEvent) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO decision_events (decision_id, event_type, actor_id, actor_role, occurred_at, payload_json, prev_hash, event_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.decision_id, event.event_type.value, event.actor_id, event.actor_role,
                    event.occurred_at, event.payload_json, event.prev_hash, event.event_hash,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def save_outcome(self, outcome: OutcomeRecord) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO outcome_records (id, decision_id, recorded_by, recorded_at, actual_duration_h, soil_moisture_after_pct, actual_rainfall_mm, water_stress_observed, crop_health_note, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    outcome.id, outcome.decision_id, outcome.recorded_by, outcome.recorded_at,
                    outcome.actual_duration_h, outcome.soil_moisture_after_pct, outcome.actual_rainfall_mm,
                    outcome.water_stress_observed, outcome.crop_health_note, outcome.notes,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _row_to_decision(self, r: sqlite3.Row) -> IrrigationDecision:
        return IrrigationDecision(
            id=r["id"],
            plot_id=r["plot_id"],
            created_at=r["created_at"],
            ruleset_version=r["ruleset_version"],
            recommended_action=RecommendedAction(r["recommended_action"]),
            recommended_duration_h=float(r["recommended_duration_h"]),
            confidence=float(r["confidence"]),
            status=DecisionStatus(r["status"]),
        )
