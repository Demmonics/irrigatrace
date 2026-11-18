import pytest
from pathlib import Path

from api.irrigatrace.infra.db.connection import Database
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
    ReviewAction,
    RecommendedAction,
    DecisionStatus,
    EventType,
)
from api.irrigatrace.domain.engine import RuleSet
from api.irrigatrace.services.recorder import DecisionRecorder
from api.irrigatrace.services.review import ReviewService
from api.irrigatrace.services.replay import DecisionReplayService
from api.irrigatrace.services.integrity import IntegrityService


@pytest.fixture
def env(tmp_path):
    db_file = tmp_path / "lifecycle.db"
    db = Database(str(db_file))
    clock = SystemClock()

    plot_repo = SqlitePlotRepository(db)
    sensor_repo = SqliteSensorRepository(db)
    weather_repo = SqliteWeatherRepository(db)
    decision_repo = SqliteDecisionRepository(db)

    # Insert user
    conn = db.get_connection()
    conn.execute("INSERT INTO users (id, name, role) VALUES ('u1', 'Supervisor 1', 'SUPERVISOR')")
    conn.commit()
    conn.close()

    plot = FarmPlot(
        id="plot-104",
        code="SG-104",
        name="Plot A",
        area_ha=4.2,
        soil_type="Clay Loam",
        planting_date="2026-05-15",
        irrigation_method="DRIP",
        application_rate_mm_h=14.0,
    )
    plot_repo.save(plot)

    sensor = SensorReading(
        id="read-104",
        plot_id="plot-104",
        ts="2026-10-24T09:41:58Z",
        soil_moisture_pct=21.0,
        temperature_c=33.0,
        source="SIMULATED",
    )
    sensor_repo.save(sensor)

    weather = WeatherSnapshot(
        id="wsnap-104",
        plot_id="plot-104",
        captured_at="2026-10-24T09:42:01Z",
        rain_probability_pct=12.0,
        forecast_rain_mm=0.0,
        source="SIMULATED",
    )
    weather_repo.save(weather)

    rules_file = Path(__file__).resolve().parent.parent.parent / "irrigatrace" / "rules" / "rules-v1.4.2.yaml"
    with open(rules_file, "r", encoding="utf-8") as f:
        ruleset = RuleSet.from_yaml(f.read())

    recorder = DecisionRecorder(decision_repo, plot_repo, sensor_repo, weather_repo, clock)
    review_svc = ReviewService(decision_repo, recorder, clock)
    replay_svc = DecisionReplayService(decision_repo, recorder, clock)
    integrity_svc = IntegrityService(decision_repo, clock)

    return {
        "db": db,
        "plot_repo": plot_repo,
        "sensor_repo": sensor_repo,
        "weather_repo": weather_repo,
        "decision_repo": decision_repo,
        "ruleset": ruleset,
        "recorder": recorder,
        "review_svc": review_svc,
        "replay_svc": replay_svc,
        "integrity_svc": integrity_svc,
    }


def test_tc08_generate_decision_atomic(env):
    """TC-08: Generate decision writes decision + snapshot + explanation + 4 events atomically."""
    dec = env["recorder"].record_new_decision(
        plot_id="plot-104",
        ruleset=env["ruleset"],
        sensor_reading_id="read-104",
        weather_snapshot_id="wsnap-104",
        occurred_at="2026-10-24T09:42:07Z",
    )

    assert dec.id is not None
    assert dec.recommended_action == RecommendedAction.IRRIGATE
    assert dec.recommended_duration_h == 2.8
    assert dec.status == DecisionStatus.PENDING_REVIEW

    # Check snapshot
    snap = env["decision_repo"].get_snapshot(dec.id)
    assert snap is not None
    assert snap.decision_id == dec.id

    # Check explanations
    expls = env["decision_repo"].get_explanations(dec.id)
    assert len(expls) >= 1
    assert expls[0].kind.value == "DETERMINISTIC"

    # Check 4 events
    events = env["decision_repo"].get_events(dec.id)
    assert len(events) == 4
    assert events[0].event_type == EventType.SENSOR_RECEIVED
    assert events[1].event_type == EventType.WEATHER_CAPTURED
    assert events[2].event_type == EventType.RECOMMENDATION_GENERATED
    assert events[3].event_type == EventType.EXPLANATION_ATTACHED

    # Verify initial hash chain
    audit = env["integrity_svc"].verify(dec.id)
    assert audit["valid"] is True
    assert audit["event_count"] == 4


def test_tc09_approve_lifecycle(env):
    """TC-09: Approve -> FINALIZED, final = AI."""
    dec = env["recorder"].record_new_decision(
        plot_id="plot-104",
        ruleset=env["ruleset"],
        occurred_at="2026-10-24T09:42:07Z",
    )
    rev = env["review_svc"].submit_review(
        decision_id=dec.id,
        reviewer_id="u1",
        reviewer_role="SUPERVISOR",
        action=ReviewAction.APPROVE,
        occurred_at="2026-10-24T10:05:00Z",
    )
    assert rev.final_action == dec.recommended_action
    assert rev.final_duration_h == dec.recommended_duration_h

    # Check status
    updated_dec = env["decision_repo"].get_by_id(dec.id)
    assert updated_dec.status == DecisionStatus.FINALIZED

    # Verify hash chain
    audit = env["integrity_svc"].verify(dec.id)
    assert audit["valid"] is True
    assert audit["event_count"] == 6  # 4 initial + REVIEW_APPROVED + DECISION_FINALIZED


def test_tc10_and_tc11_modify_lifecycle(env):
    """
    TC-10: Modify without reason raises error.
    TC-11: Modify with reason creates new review row, original recommendation unchanged.
    """
    dec = env["recorder"].record_new_decision(
        plot_id="plot-104",
        ruleset=env["ruleset"],
        occurred_at="2026-10-24T09:42:07Z",
    )

    # Modify without reason -> ValueError
    with pytest.raises(ValueError, match="reason_code and non-empty reason_text are required"):
        env["review_svc"].submit_review(
            decision_id=dec.id,
            reviewer_id="u1",
            reviewer_role="SUPERVISOR",
            action=ReviewAction.MODIFY,
            reason_code=None,
            reason_text="",
            final_action=RecommendedAction.IRRIGATE,
            final_duration_h=2.0,
        )

    # Modify with reason
    rev = env["review_svc"].submit_review(
        decision_id=dec.id,
        reviewer_id="u1",
        reviewer_role="SUPERVISOR",
        action=ReviewAction.MODIFY,
        reason_code="LOCAL_FIELD_CONDITIONS",
        reason_text="Reduced due to damp surface.",
        final_action=RecommendedAction.IRRIGATE,
        final_duration_h=2.0,
        occurred_at="2026-10-24T10:05:47Z",
    )
    assert rev.final_duration_h == 2.0

    # Invariant 1: Assert original AI recommendation is strictly unchanged
    updated_dec = env["decision_repo"].get_by_id(dec.id)
    assert updated_dec.recommended_action == RecommendedAction.IRRIGATE
    assert updated_dec.recommended_duration_h == 2.8
    assert updated_dec.status == DecisionStatus.FINALIZED

    audit = env["integrity_svc"].verify(dec.id)
    assert audit["valid"] is True


def test_tc12_reject_lifecycle(env):
    """TC-12: Reject requires reason."""
    dec = env["recorder"].record_new_decision(
        plot_id="plot-104",
        ruleset=env["ruleset"],
        occurred_at="2026-10-24T09:42:07Z",
    )
    with pytest.raises(ValueError, match="reason_code and non-empty reason_text are required"):
        env["review_svc"].submit_review(
            decision_id=dec.id,
            reviewer_id="u1",
            reviewer_role="SUPERVISOR",
            action=ReviewAction.REJECT,
            reason_code="",
            reason_text="",
        )

    rev = env["review_svc"].submit_review(
        decision_id=dec.id,
        reviewer_id="u1",
        reviewer_role="SUPERVISOR",
        action=ReviewAction.REJECT,
        reason_code="SENSOR_DOUBT",
        reason_text="Sensor readings fluctuate wildly.",
        occurred_at="2026-10-24T10:05:47Z",
    )
    assert rev.final_action == RecommendedAction.WAIT
    assert rev.final_duration_h == 0.0


def test_tc15_tamper_detection(env):
    """TC-15: Tamper test: when an event payload is modified, verify flags invalid and identifies sequence."""
    dec = env["recorder"].record_new_decision(
        plot_id="plot-104",
        ruleset=env["ruleset"],
        occurred_at="2026-10-24T09:42:07Z",
    )
    conn = env["db"].get_connection()

    # Drop trigger temporarily on this test DB to tamper payload
    conn.execute("DROP TRIGGER events_no_update;")
    conn.execute("UPDATE decision_events SET payload_json = '{\"tampered\": true}' WHERE decision_id = ? AND seq = 3", (dec.id,))
    conn.commit()
    conn.close()

    res = env["integrity_svc"].verify(dec.id)
    assert res["valid"] is False
    assert res["broken_at_seq"] == 3


def test_tc18_reproduce_check(env):
    """TC-18: Reproduce on untouched decision -> match = true."""
    dec = env["recorder"].record_new_decision(
        plot_id="plot-104",
        ruleset=env["ruleset"],
        occurred_at="2026-10-24T09:42:07Z",
    )
    res = env["replay_svc"].reproduce(dec.id)
    assert res["match"] is True
    assert res["status"] == "EXACT_MATCH"


def test_tc27_replay_state_at(env):
    """TC-27: Replay state_at(t) before review shows no review and flags later events."""
    dec = env["recorder"].record_new_decision(
        plot_id="plot-104",
        ruleset=env["ruleset"],
        occurred_at="2026-10-24T09:42:07Z",
    )
    env["review_svc"].submit_review(
        decision_id=dec.id,
        reviewer_id="u1",
        reviewer_role="SUPERVISOR",
        action=ReviewAction.APPROVE,
        occurred_at="2026-10-24T10:05:00Z",
    )

    # Check state at 10:00:00 (between generation and review)
    state = env["replay_svc"].state_at(dec.id, "2026-10-24T10:00:00Z")
    assert state["review"] is None
    assert state["status_at_t"] == "PENDING_REVIEW"
    assert len(state["future_events"]) > 0
