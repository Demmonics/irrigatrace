from pathlib import Path
import pytest
from api.irrigatrace.domain.models import EngineInputs, RecommendedAction, CropStage
from api.irrigatrace.domain.engine import RuleSet, IrrigationEngine


@pytest.fixture
def ruleset():
    rule_file = Path(__file__).resolve().parent.parent.parent / "irrigatrace" / "rules" / "rules-v1.4.2.yaml"
    with open(rule_file, "r", encoding="utf-8") as f:
        return RuleSet.from_yaml(f.read())


def test_worked_example_1_irrigate(ruleset):
    """
    Doc 07 Worked Example 1:
    Grand Growth, moisture 21, temp 33, rain 12, rate 14 mm/h ->
    hot_uplift 0.9, trigger 25.9; deficit 13 pp -> 39 mm -> 39/14 = 2.79 -> 2.8 h, IRRIGATE.
    fired [R-TRIGGER-LOW, R-HOT-UPLIFT, R-RAIN-NONE]. Confidence ≈ 0.84.
    """
    inputs = EngineInputs(
        soil_moisture_pct=21.0,
        temperature_c=33.0,
        rain_probability_pct=12.0,
        forecast_rain_mm=0.0,
        crop_stage=CropStage.GRAND_GROWTH,
        days_since_last_irrigation=9,
        application_rate_mm_h=14.0,
        active_root_zone_mm=300,
    )
    rec = IrrigationEngine.recommend(inputs, ruleset)

    assert rec.action == RecommendedAction.IRRIGATE
    assert rec.duration_h == 2.8
    assert abs(rec.confidence - 0.84) <= 0.02
    assert "R-TRIGGER-LOW" in rec.fired_rules
    assert "R-HOT-UPLIFT" in rec.fired_rules
    assert "R-RAIN-NONE" in rec.fired_rules

    # Test explanation factors
    explanation = IrrigationEngine.build_deterministic_explanation(inputs, ruleset, rec)
    assert len(explanation["factors"]) >= 3
    assert "2.8" in explanation["template_narrative"]
    assert "IRRIGATE" in explanation["template_narrative"]


def test_worked_example_2_defer_rain(ruleset):
    """
    Doc 07 Worked Example 2:
    Grand Growth, moisture 29, temp 29, rain 72 -> DEFER_RAIN (R-RAIN-HIGH)
    """
    inputs = EngineInputs(
        soil_moisture_pct=29.0,
        temperature_c=29.0,
        rain_probability_pct=72.0,
        forecast_rain_mm=15.0,
        crop_stage=CropStage.GRAND_GROWTH,
        days_since_last_irrigation=4,
        application_rate_mm_h=14.0,
        active_root_zone_mm=300,
    )
    rec = IrrigationEngine.recommend(inputs, ruleset)

    assert rec.action == RecommendedAction.DEFER_RAIN
    assert rec.duration_h == 0.0
    assert "R-RAIN-HIGH" in rec.fired_rules


def test_wait_when_moisture_sufficient(ruleset):
    """
    Moisture is 28% in Tillering (trigger is 23%), low rain -> WAIT
    """
    inputs = EngineInputs(
        soil_moisture_pct=28.0,
        temperature_c=25.0,
        rain_probability_pct=10.0,
        forecast_rain_mm=0.0,
        crop_stage=CropStage.TILLERING,
        days_since_last_irrigation=3,
        application_rate_mm_h=14.0,
        active_root_zone_mm=250,
    )
    rec = IrrigationEngine.recommend(inputs, ruleset)

    assert rec.action == RecommendedAction.WAIT
    assert rec.duration_h == 0.0
    assert "R-MOISTURE-OK" in rec.fired_rules
