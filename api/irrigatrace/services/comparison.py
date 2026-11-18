"""
ComparisonService with deterministic flip analysis.
Obeys Invariant 6: No invented causality. Uses engine-grounded flip analysis only.
"""
from __future__ import annotations

import json
from typing import Dict, Any, List, Optional

from api.irrigatrace.domain.models import (
    DecisionComparison,
    EngineInputs,
    CropStage,
    RecommendedAction,
)
from api.irrigatrace.domain.engine import RuleSet, IrrigationEngine
from api.irrigatrace.domain.ports import DecisionRepository


class ComparisonService:
    def __init__(self, decision_repo: DecisionRepository):
        self.decision_repo = decision_repo

    def compare(self, a_id: str, b_id: str) -> DecisionComparison:
        snap_a = self.decision_repo.get_snapshot(a_id)
        snap_b = self.decision_repo.get_snapshot(b_id)
        if not snap_a:
            raise ValueError(f"Snapshot not found for decision {a_id}")
        if not snap_b:
            raise ValueError(f"Snapshot not found for decision {b_id}")

        dec_a = self.decision_repo.get_by_id(a_id)
        dec_b = self.decision_repo.get_by_id(b_id)
        if not dec_a or not dec_b:
            raise ValueError("Decisions not found")

        inputs_a = json.loads(snap_a.inputs_json)
        inputs_b = json.loads(snap_b.inputs_json)

        ruleset_a = RuleSet.from_json(snap_a.ruleset_json)
        ruleset_b = RuleSet.from_json(snap_b.ruleset_json)

        # 1. Input Deltas
        input_deltas = []
        unit_map = {
            "soil_moisture_pct": "pp",
            "temperature_c": "C",
            "rain_probability_pct": "pp",
            "forecast_rain_mm": "mm",
            "days_since_last_irrigation": "days",
            "application_rate_mm_h": "mm/h",
            "active_root_zone_mm": "mm",
            "crop_stage": "",
        }

        keys_to_compare = [
            "soil_moisture_pct", "temperature_c", "rain_probability_pct",
            "forecast_rain_mm", "crop_stage", "days_since_last_irrigation",
            "application_rate_mm_h", "active_root_zone_mm",
        ]

        differing_keys = []
        for k in keys_to_compare:
            val_a = inputs_a.get(k)
            val_b = inputs_b.get(k)
            if val_a != val_b:
                differing_keys.append(k)
                delta = None
                if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                    delta = round(val_b - val_a, 2)
                input_deltas.append({
                    "field": k,
                    "a": val_a,
                    "b": val_b,
                    "delta": delta,
                    "unit": unit_map.get(k, ""),
                })

        # 2. Output Deltas
        output_deltas = [
            {
                "field": "action",
                "a": dec_a.recommended_action.value,
                "b": dec_b.recommended_action.value,
                "changed": dec_a.recommended_action != dec_b.recommended_action,
            },
            {
                "field": "duration_h",
                "a": dec_a.recommended_duration_h,
                "b": dec_b.recommended_duration_h,
                "delta": round(dec_b.recommended_duration_h - dec_a.recommended_duration_h, 2),
                "unit": "hours",
            },
            {
                "field": "confidence",
                "a": dec_a.confidence,
                "b": dec_b.confidence,
                "delta": round(dec_b.confidence - dec_a.confidence, 2),
            },
        ]

        # 3. Rule Deltas
        rules_a = set()
        rules_b = set()
        for ev in dec_a.events:
            if ev.event_type.value == "RECOMMENDATION_GENERATED":
                rules_a.update(json.loads(ev.payload_json).get("fired_rules", []))
        for ev in dec_b.events:
            if ev.event_type.value == "RECOMMENDATION_GENERATED":
                rules_b.update(json.loads(ev.payload_json).get("fired_rules", []))

        rule_deltas = {
            "added": sorted(list(rules_b - rules_a)),
            "removed": sorted(list(rules_a - rules_b)),
            "retained": sorted(list(rules_a & rules_b)),
        }

        # 4. Flip Analysis
        # For each differing input: run engine on A's inputs with i := B's input
        flips = []
        base_obj_a = self._dict_to_engine_inputs(inputs_a)
        orig_action_a = dec_a.recommended_action

        for key in differing_keys:
            modified_dict_a = dict(inputs_a)
            modified_dict_a[key] = inputs_b[key]
            mod_inputs = self._dict_to_engine_inputs(modified_dict_a)
            rec_mod = IrrigationEngine.recommend(mod_inputs, ruleset_a)

            flips_action = (rec_mod.action != orig_action_a)
            flips.append({
                "input": key,
                "alone_flips_action": flips_action,
                "original_action": orig_action_a.value,
                "flipped_to": rec_mod.action.value if flips_action else None,
                "resulting_duration_h": rec_mod.duration_h,
                "from_value": inputs_a[key],
                "to_value": inputs_b[key],
            })

        # Summary text generation (deterministic)
        flipped_inputs = [f["input"] for f in flips if f["alone_flips_action"]]
        if flipped_inputs:
            flip_text = f"Input '{', '.join(flipped_inputs)}' alone flips the recommendation from {dec_a.recommended_action.value} to {dec_b.recommended_action.value}."
        else:
            flip_text = f"No single input alone flips the action; the changes in {', '.join(differing_keys)} coincided with the new recommendation."

        summary = {
            "text": f"Comparing {a_id} with {b_id}: {flip_text}",
            "source": "deterministic_flip_analysis",
            "differing_inputs_count": len(differing_keys),
            "rulesets_differ": (ruleset_a.version != ruleset_b.version),
        }

        return DecisionComparison(
            a_id=a_id,
            b_id=b_id,
            input_deltas=input_deltas,
            output_deltas=output_deltas,
            rule_deltas=rule_deltas,
            flips=flips,
            summary=summary,
        )

    def _dict_to_engine_inputs(self, d: Dict[str, Any]) -> EngineInputs:
        return EngineInputs(
            soil_moisture_pct=float(d["soil_moisture_pct"]),
            temperature_c=float(d["temperature_c"]),
            rain_probability_pct=float(d["rain_probability_pct"]),
            forecast_rain_mm=float(d.get("forecast_rain_mm", 0.0)),
            crop_stage=CropStage(d["crop_stage"]),
            days_since_last_irrigation=int(d.get("days_since_last_irrigation", 7)),
            application_rate_mm_h=float(d["application_rate_mm_h"]),
            active_root_zone_mm=int(d["active_root_zone_mm"]),
            sensor_reading_ts=d.get("sensor_reading_ts"),
        )
