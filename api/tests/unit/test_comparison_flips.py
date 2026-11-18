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
from api.irrigatrace.domain.models import FarmPlot, SensorReading, WeatherSnapshot
from api.irrigatrace.domain.engine import RuleSet
from api.irrigatrace.services.recorder import DecisionRecorder
from api.irrigatrace.services.comparison import ComparisonService


def test_tc20_and_tc21_comparison_flip_analysis(tmp_path):
    """
    TC-20: Compare 29% moisture / 29C / 72% rain (DEFER_RAIN) vs 21% / 33C / 12% rain (IRRIGATE 2.8h).
    Deltas: -8 pp, +4 C, -60 pp.
    Flip analysis: rain alone flips action; moisture alone does not flip.
    """
    db_file = tmp_path / "compare.db"
    db = Database(str(db_file))
    clock = SystemClock()

    plot_repo = SqlitePlotRepository(db)
    sensor_repo = SqliteSensorRepository(db)
    weather_repo = SqliteWeatherRepository(db)
    decision_repo = SqliteDecisionRepository(db)

    plot = FarmPlot(
        id="plot-104",
        code="SG-104",
        name="North Plateau A",
        area_ha=4.2,
        soil_type="Clay Loam",
        planting_date="2026-05-15",
        irrigation_method="DRIP",
        application_rate_mm_h=14.0,
    )
    plot_repo.save(plot)

    # Decision A (IRR-2026-014): 29% moisture, 29C, 72% rain -> DEFER_RAIN
    s_a = SensorReading(id="s-a", plot_id="plot-104", ts="2026-10-18T08:00:00Z", soil_moisture_pct=29.0, temperature_c=29.0, source="SIMULATED")
    sensor_repo.save(s_a)
    w_a = WeatherSnapshot(id="w-a", plot_id="plot-104", captured_at="2026-10-18T08:00:00Z", rain_probability_pct=72.0, forecast_rain_mm=18.0, source="SIMULATED")
    weather_repo.save(w_a)

    # Decision B (IRR-2026-018): 21% moisture, 33C, 12% rain -> IRRIGATE
    s_b = SensorReading(id="s-b", plot_id="plot-104", ts="2026-10-24T09:40:00Z", soil_moisture_pct=21.0, temperature_c=33.0, source="SIMULATED")
    sensor_repo.save(s_b)
    w_b = WeatherSnapshot(id="w-b", plot_id="plot-104", captured_at="2026-10-24T09:40:00Z", rain_probability_pct=12.0, forecast_rain_mm=0.0, source="SIMULATED")
    weather_repo.save(w_b)

    rules_file = Path(__file__).resolve().parent.parent.parent / "irrigatrace" / "rules" / "rules-v1.4.2.yaml"
    with open(rules_file, "r", encoding="utf-8") as f:
        ruleset = RuleSet.from_yaml(f.read())

    recorder = DecisionRecorder(decision_repo, plot_repo, sensor_repo, weather_repo, clock)

    dec_a = recorder.record_new_decision(
        plot_id="plot-104",
        ruleset=ruleset,
        sensor_reading_id="s-a",
        weather_snapshot_id="w-a",
        occurred_at="2026-10-18T08:00:00Z",
        decision_id="IRR-2026-014",
    )
    dec_b = recorder.record_new_decision(
        plot_id="plot-104",
        ruleset=ruleset,
        sensor_reading_id="s-b",
        weather_snapshot_id="w-b",
        occurred_at="2026-10-24T09:42:07Z",
        decision_id="IRR-2026-018",
    )

    comp_svc = ComparisonService(decision_repo)
    comp = comp_svc.compare("IRR-2026-014", "IRR-2026-018")

    # Check input deltas
    deltas = {d["field"]: d["delta"] for d in comp.input_deltas}
    assert deltas["soil_moisture_pct"] == -8.0
    assert deltas["temperature_c"] == 4.0
    assert deltas["rain_probability_pct"] == -60.0

    # Check output deltas
    out_deltas = {d["field"]: d for d in comp.output_deltas}
    assert out_deltas["action"]["a"] == "DEFER_RAIN"
    assert out_deltas["action"]["b"] == "IRRIGATE"
    assert out_deltas["duration_h"]["delta"] == 2.8

    # Flip analysis:
    # On Decision A (DEFER_RAIN because rain=72%):
    # Changing rain to B's 12% (with moisture=29% in Grand Growth, trigger=25%) ->
    # Since moisture 29% >= trigger 25%, changing rain alone from 72% to 12% flips DEFER_RAIN to WAIT!
    # And changing moisture alone to 21% (while rain is still 72%) still stays DEFER_RAIN!
    rain_flip = next(f for f in comp.flips if f["input"] == "rain_probability_pct")
    moist_flip = next(f for f in comp.flips if f["input"] == "soil_moisture_pct")

    assert rain_flip["alone_flips_action"] is True
    assert moist_flip["alone_flips_action"] is False

    assert "alone flips" in comp.summary["text"]
