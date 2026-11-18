import pytest
from api.irrigatrace.services.narration import NumberConsistencyValidator


def test_tc22_number_consistency_validator_pass():
    evidence = {
        "factors": [
            {"value": 21.0, "threshold": 25.9},
            {"value": 33.0, "threshold": 30.0},
            {"value": 12.0, "threshold": 60.0},
        ],
        "duration_h": 2.8,
    }
    # Valid narrative containing only numbers from evidence
    text = "Recommend IRRIGATE for 2.8 hours. Soil moisture 21% is below trigger 25.9% with temperature 33C."
    valid, reason = NumberConsistencyValidator.validate(text, evidence, "IRRIGATE")
    assert valid is True


def test_tc22_number_consistency_validator_injected_number():
    evidence = {
        "factors": [
            {"value": 21.0, "threshold": 25.9},
            {"value": 33.0, "threshold": 30.0},
        ],
        "duration_h": 2.8,
    }
    # Injected hallucinated number 45.5% or 99 hours
    text = "Recommend IRRIGATE for 99 hours because moisture is 45.5%."
    valid, reason = NumberConsistencyValidator.validate(text, evidence, "IRRIGATE")
    assert valid is False
    assert "not present in evidence" in reason


def test_tc22_number_consistency_validator_action_contradiction():
    evidence = {
        "factors": [{"value": 21.0, "threshold": 25.9}],
        "duration_h": 2.8,
    }
    text = "Do not irrigate today as conditions might change."
    valid, reason = NumberConsistencyValidator.validate(text, evidence, "IRRIGATE")
    assert valid is False
    assert "Contradicts action" in reason
