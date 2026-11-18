import sqlite3
import pytest
from pathlib import Path

from api.irrigatrace.infra.db.connection import Database
from api.irrigatrace.domain.models import compute_hash, canonical_json
from api.irrigatrace.services.integrity import IntegrityService
from api.irrigatrace.infra.db.repositories import SqliteDecisionRepository, SystemClock


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_triggers.db"
    db = Database(str(db_file))
    conn = db.get_connection()

    # Insert minimal seed
    conn.execute("INSERT INTO users (id, name, role) VALUES ('u1', 'Test', 'SUPERVISOR')")
    conn.execute("INSERT INTO farm_plots (id, code, name, area_ha, soil_type, planting_date, irrigation_method, application_rate_mm_h) VALUES ('p1', 'SG-101', 'P1', 1.0, 'Loam', '2026-01-01', 'DRIP', 10.0)")
    conn.execute("INSERT INTO sensor_readings (id, plot_id, ts, soil_moisture_pct, temperature_c, source) VALUES ('r1', 'p1', '2026-10-01T10:00:00Z', 20.0, 30.0, 'SIMULATED')")
    conn.execute("INSERT INTO weather_snapshots (id, plot_id, captured_at, rain_probability_pct, forecast_rain_mm, source) VALUES ('w1', 'p1', '2026-10-01T10:00:00Z', 10.0, 0.0, 'SIMULATED')")
    conn.execute("INSERT INTO irrigation_decisions (id, plot_id, created_at, ruleset_version, recommended_action, recommended_duration_h, confidence, status) VALUES ('IRR-2026-001', 'p1', '2026-10-01T10:00:00Z', 'rules-v1.4.2', 'IRRIGATE', 2.5, 0.85, 'PENDING_REVIEW')")
    conn.execute("INSERT INTO decision_snapshots (decision_id, sensor_reading_id, weather_snapshot_id, inputs_json, ruleset_json, engine_version, engine_code_sha256, snapshot_sha256) VALUES ('IRR-2026-001', 'r1', 'w1', '{}', '{}', '1.4.2', 'hash', 'snap_hash')")
    conn.execute("INSERT INTO human_reviews (id, decision_id, reviewer_id, action, final_action, final_duration_h, created_at) VALUES ('rev1', 'IRR-2026-001', 'u1', 'APPROVE', 'IRRIGATE', 2.5, '2026-10-01T10:05:00Z')")
    conn.execute("INSERT INTO decision_events (decision_id, event_type, actor_id, actor_role, occurred_at, payload_json, prev_hash, event_hash) VALUES ('IRR-2026-001', 'SENSOR_RECEIVED', 'u1', 'SYSTEM', '2026-10-01T10:00:00Z', '{}', 'prev', 'ev_hash')")
    conn.commit()
    conn.close()
    return db


def test_tc13_events_immutable(temp_db):
    """TC-13: UPDATE/DELETE on decision_events raises DB error via trigger."""
    conn = temp_db.get_connection()
    with pytest.raises(sqlite3.IntegrityError, match="decision_events is append-only"):
        conn.execute("UPDATE decision_events SET actor_id = 'hacker' WHERE decision_id = 'IRR-2026-001'")

    with pytest.raises(sqlite3.IntegrityError, match="decision_events is append-only"):
        conn.execute("DELETE FROM decision_events WHERE decision_id = 'IRR-2026-001'")
    conn.close()


def test_tc13_snapshots_immutable(temp_db):
    """TC-13: UPDATE/DELETE on snapshots raises DB error via trigger."""
    conn = temp_db.get_connection()
    with pytest.raises(sqlite3.IntegrityError, match="snapshots are immutable"):
        conn.execute("UPDATE decision_snapshots SET engine_version = '2.0' WHERE decision_id = 'IRR-2026-001'")

    with pytest.raises(sqlite3.IntegrityError, match="snapshots are immutable"):
        conn.execute("DELETE FROM decision_snapshots WHERE decision_id = 'IRR-2026-001'")
    conn.close()


def test_tc13_reviews_immutable(temp_db):
    """TC-13: UPDATE/DELETE on human_reviews raises DB error via trigger."""
    conn = temp_db.get_connection()
    with pytest.raises(sqlite3.IntegrityError, match="reviews are immutable"):
        conn.execute("UPDATE human_reviews SET final_duration_h = 10.0 WHERE id = 'rev1'")

    with pytest.raises(sqlite3.IntegrityError, match="reviews are immutable"):
        conn.execute("DELETE FROM human_reviews WHERE id = 'rev1'")
    conn.close()


def test_tc14_decision_core_immutable(temp_db):
    """TC-14: UPDATE of original recommendation fields raises DB error."""
    conn = temp_db.get_connection()
    with pytest.raises(sqlite3.IntegrityError, match="original recommendation is immutable"):
        conn.execute("UPDATE irrigation_decisions SET recommended_duration_h = 5.0 WHERE id = 'IRR-2026-001'")

    with pytest.raises(sqlite3.IntegrityError, match="original recommendation is immutable"):
        conn.execute("UPDATE irrigation_decisions SET recommended_action = 'WAIT' WHERE id = 'IRR-2026-001'")

    # But status projection update IS allowed:
    conn.execute("UPDATE irrigation_decisions SET status = 'FINALIZED' WHERE id = 'IRR-2026-001'")
    conn.commit()
    conn.close()
