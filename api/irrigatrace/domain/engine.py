"""
RuleSet and IrrigationEngine implementations.
Strictly deterministic, pure functional recommendation logic.
Worked examples from doc 07 are verified.
"""
from __future__ import annotations

import math
import yaml
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional

from api.irrigatrace.domain.models import (
    EngineInputs,
    Recommendation,
    RecommendedAction,
    CropStage,
    canonical_json,
    compute_hash,
)


@dataclass
class StageParam:
    trigger_vwc: float
    target_vwc: float
    active_root_zone_mm: int


@dataclass
class RuleSet:
    """Versioned thresholds and rules."""
    version: str
    stage_params: Dict[str, StageParam]
    temperature: Dict[str, float]
    rain: Dict[str, float]
    duration: Dict[str, float]
    confidence: Dict[str, Any]
    raw_yaml: str = ""

    @classmethod
    def from_yaml(cls, yaml_content: str) -> RuleSet:
        data = yaml.safe_load(yaml_content)
        stage_params = {}
        for stage_name, sp in data.get("stage_params", {}).items():
            stage_params[stage_name] = StageParam(
                trigger_vwc=float(sp["trigger_vwc"]),
                target_vwc=float(sp["target_vwc"]),
                active_root_zone_mm=int(sp["active_root_zone_mm"]),
            )
        return cls(
            version=data["version"],
            stage_params=stage_params,
            temperature=data.get("temperature", {}),
            rain=data.get("rain", {}),
            duration=data.get("duration", {}),
            confidence=data.get("confidence", {}),
            raw_yaml=yaml_content,
        )

    @classmethod
    def from_json(cls, json_str: str) -> RuleSet:
        data = json.loads(json_str)
        stage_params = {
            k: StageParam(
                trigger_vwc=float(v["trigger_vwc"]),
                target_vwc=float(v["target_vwc"]),
                active_root_zone_mm=int(v["active_root_zone_mm"]),
            )
            for k, v in data.get("stage_params", {}).items()
        }
        return cls(
            version=data["version"],
            stage_params=stage_params,
            temperature=data.get("temperature", {}),
            rain=data.get("rain", {}),
            duration=data.get("duration", {}),
            confidence=data.get("confidence", {}),
        )

    @classmethod
    def default(cls) -> RuleSet:
        import os
        from pathlib import Path
        p = Path(__file__).resolve().parent.parent / "rules" / "rules-v1.4.2.yaml"
        if not p.exists():
            p = Path("api/irrigatrace/rules/rules-v1.4.2.yaml")
        with open(p, "r", encoding="utf-8") as f:
            return cls.from_yaml(f.read())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "stage_params": {
                k: {
                    "trigger_vwc": v.trigger_vwc,
                    "target_vwc": v.target_vwc,
                    "active_root_zone_mm": v.active_root_zone_mm,
                }
                for k, v in self.stage_params.items()
            },
            "temperature": self.temperature,
            "rain": self.rain,
            "duration": self.duration,
            "confidence": self.confidence,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    def sha256(self) -> str:
        return compute_hash(self.to_json())


class IrrigationEngine:
    """Pure deterministic irrigation rule engine."""

    VERSION = "1.4.2"

    @classmethod
    def engine_code_sha256(cls) -> str:
        """Hash of the engine implementation logic."""
        import inspect
        code = inspect.getsource(cls.recommend)
        return compute_hash(code)

    @classmethod
    def recommend(cls, inputs: EngineInputs, ruleset: RuleSet) -> Recommendation:
        """
        Pure function: inputs + ruleset -> Recommendation
        """
        stage_key = inputs.crop_stage.value
        stage = ruleset.stage_params.get(stage_key)
        if not stage:
            raise ValueError(f"Unknown crop stage: {stage_key}")

        # 1. Temperature uplift
        hot_above_c = ruleset.temperature.get("hot_above_c", 30.0)
        uplift_per_c = ruleset.temperature.get("trigger_uplift_pp_per_c", 0.3)
        max_uplift = ruleset.temperature.get("max_uplift_pp", 2.0)

        hot_diff = max(0.0, inputs.temperature_c - hot_above_c)
        hot_uplift = min(max_uplift, hot_diff * uplift_per_c)
        trigger = stage.trigger_vwc + hot_uplift

        # 2. Rain rules
        defer_prob = ruleset.rain.get("defer_if_prob_ge", 60.0)
        partial_prob = ruleset.rain.get("partial_if_prob_ge", 30.0)
        discount = ruleset.rain.get("partial_discount_per_10pct", 0.05)

        fired_rules: List[str] = []

        if inputs.rain_probability_pct >= defer_prob:
            action = RecommendedAction.DEFER_RAIN
            duration_h = 0.0
            fired_rules.append("R-RAIN-HIGH")
        elif inputs.soil_moisture_pct >= trigger:
            action = RecommendedAction.WAIT
            duration_h = 0.0
            fired_rules.append("R-MOISTURE-OK")
            if inputs.rain_probability_pct >= partial_prob:
                fired_rules.append("R-RAIN-PARTIAL")
            else:
                fired_rules.append("R-RAIN-NONE")
        else:
            action = RecommendedAction.IRRIGATE
            fired_rules.append("R-TRIGGER-LOW")
            if hot_uplift > 0:
                fired_rules.append("R-HOT-UPLIFT")

            deficit_pp = stage.target_vwc - inputs.soil_moisture_pct
            root_zone_mm = inputs.active_root_zone_mm or stage.active_root_zone_mm
            deficit_mm = (deficit_pp / 100.0) * root_zone_mm
            raw_h = deficit_mm / inputs.application_rate_mm_h

            if inputs.rain_probability_pct >= partial_prob:
                steps = math.floor((inputs.rain_probability_pct - 30.0) / 10.0) + 1
                factor = max(0.0, 1.0 - (steps * discount))
                raw_h *= factor
                fired_rules.append("R-RAIN-PARTIAL")
            else:
                fired_rules.append("R-RAIN-NONE")

            min_h = ruleset.duration.get("min_h", 0.5)
            max_h = ruleset.duration.get("max_h", 6.0)
            duration_h = max(min_h, min(max_h, round(raw_h, 1)))

        # 3. Confidence calculation
        conf_cfg = ruleset.confidence
        base_conf = conf_cfg.get("base", 0.55)
        margin_weight = conf_cfg.get("margin_weight", 0.35)

        if action == RecommendedAction.IRRIGATE:
            margin = max(0.0, (trigger - inputs.soil_moisture_pct) / 6.0)
            conf = base_conf + margin_weight * min(1.0, margin)
        else:
            margin = max(0.0, (inputs.soil_moisture_pct - trigger) / 6.0)
            conf = base_conf + margin_weight * min(1.0, margin)

        rain_band = conf_cfg.get("rain_uncertain_band", [30, 70])
        if rain_band[0] <= inputs.rain_probability_pct <= rain_band[1]:
            conf -= conf_cfg.get("rain_uncertain_penalty", 0.15)

        min_conf = conf_cfg.get("min", 0.05)
        max_conf = conf_cfg.get("max", 0.98)
        confidence = max(min_conf, min(max_conf, round(conf, 2)))

        return Recommendation(
            action=action,
            duration_h=duration_h,
            confidence=confidence,
            fired_rules=fired_rules,
        )

    @classmethod
    def build_deterministic_explanation(cls, inputs: EngineInputs, ruleset: RuleSet, rec: Recommendation) -> Dict[str, Any]:
        """
        Builds factors[] and plain-text explanation exactly per doc 07.
        """
        stage = ruleset.stage_params[inputs.crop_stage.value]
        hot_above_c = ruleset.temperature.get("hot_above_c", 30.0)
        uplift_per_c = ruleset.temperature.get("trigger_uplift_pp_per_c", 0.3)
        max_uplift = ruleset.temperature.get("max_uplift_pp", 2.0)
        hot_diff = max(0.0, inputs.temperature_c - hot_above_c)
        hot_uplift = min(max_uplift, hot_diff * uplift_per_c)
        trigger = stage.trigger_vwc + hot_uplift

        factors = []
        # F1: Soil moisture
        if inputs.soil_moisture_pct < trigger:
            comp = "below"
            eff = "supports_irrigation"
            text_f1 = f"Soil moisture {inputs.soil_moisture_pct}% is below the {inputs.crop_stage.value} trigger of {trigger:.1f}% ({stage.trigger_vwc}% + {hot_uplift:.1f} hot-weather uplift)."
        else:
            comp = "above_or_equal"
            eff = "supports_waiting"
            text_f1 = f"Soil moisture {inputs.soil_moisture_pct}% is at or above the {inputs.crop_stage.value} trigger of {trigger:.1f}%."

        factors.append({
            "id": "F1",
            "input": "soil_moisture_pct",
            "value": inputs.soil_moisture_pct,
            "unit": "%",
            "comparison": comp,
            "threshold": round(trigger, 1),
            "effect": eff,
            "text": text_f1
        })

        # F2: Temperature
        if hot_uplift > 0:
            factors.append({
                "id": "F2",
                "input": "temperature_c",
                "value": inputs.temperature_c,
                "unit": "C",
                "comparison": "above",
                "threshold": hot_above_c,
                "effect": "raises_moisture_trigger",
                "text": f"Ambient temperature {inputs.temperature_c}C is above {hot_above_c}C threshold, adding +{hot_uplift:.1f}pp moisture threshold uplift."
            })

        # F3: Rain
        defer_prob = ruleset.rain.get("defer_if_prob_ge", 60.0)
        if inputs.rain_probability_pct >= defer_prob:
            factors.append({
                "id": "F3",
                "input": "rain_probability_pct",
                "value": inputs.rain_probability_pct,
                "unit": "%",
                "comparison": "above_or_equal",
                "threshold": defer_prob,
                "effect": "defers_irrigation",
                "text": f"Rain probability {inputs.rain_probability_pct}% meets or exceeds defer threshold ({defer_prob}%)."
            })
        else:
            factors.append({
                "id": "F3",
                "input": "rain_probability_pct",
                "value": inputs.rain_probability_pct,
                "unit": "%",
                "comparison": "below",
                "threshold": defer_prob,
                "effect": "negligible_or_partial_rain",
                "text": f"Rain probability {inputs.rain_probability_pct}% is below defer threshold ({defer_prob}%)."
            })

        # F4: Duration derivation
        if rec.action == RecommendedAction.IRRIGATE:
            deficit_pp = stage.target_vwc - inputs.soil_moisture_pct
            root_zone_mm = inputs.active_root_zone_mm or stage.active_root_zone_mm
            deficit_mm = (deficit_pp / 100.0) * root_zone_mm
            factors.append({
                "id": "F4",
                "input": "duration_derivation",
                "value": rec.duration_h,
                "unit": "hours",
                "comparison": "calculated",
                "threshold": stage.target_vwc,
                "effect": "sets_irrigation_duration",
                "text": f"Target deficit {deficit_pp:.1f}pp ({deficit_mm:.1f} mm over {root_zone_mm} mm root zone) at {inputs.application_rate_mm_h} mm/h application rate yields {rec.duration_h} hours."
            })

        # Assemble template fallback sentence
        if rec.action == RecommendedAction.IRRIGATE:
            template = f"Recommend IRRIGATE for {rec.duration_h} hours. Soil moisture {inputs.soil_moisture_pct}% is below trigger {trigger:.1f}% for {inputs.crop_stage.value} with {inputs.rain_probability_pct}% rain probability."
        elif rec.action == RecommendedAction.DEFER_RAIN:
            template = f"Recommend DEFER_RAIN (Wait). Rain probability {inputs.rain_probability_pct}% exceeds {defer_prob}% threshold with forecast rain {inputs.forecast_rain_mm} mm."
        else:
            template = f"Recommend WAIT. Soil moisture {inputs.soil_moisture_pct}% satisfies trigger threshold {trigger:.1f}% for {inputs.crop_stage.value}."

        return {
            "factors": factors,
            "fired_rules": rec.fired_rules,
            "template_narrative": template,
        }
