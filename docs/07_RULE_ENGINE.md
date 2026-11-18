# 07 — Rule Engine (`rules-v1.4.2`)

Deliberately simple, documented, deterministic. Thresholds are **illustrative placeholders for a prototype** — mark them so in UI and docs; if KIAAR/agronomy values become available, edit the YAML and bump the version (never edit a released version).

## Inputs (`EngineInputs`, all stored in the snapshot)
`soil_moisture_pct`, `temperature_c`, `rain_probability_pct`, `forecast_rain_mm`, `crop_stage`, `days_since_last_irrigation`, `application_rate_mm_h`, `active_root_zone_mm`(from stage)

## Crop stage from planting date (sugarcane, illustrative)
| Stage | Days after planting |
|---|---|
| `ESTABLISHMENT` | 0–35 |
| `TILLERING` | 36–100 |
| `GRAND_GROWTH` | 101–270 |
| `MATURITY` | 271+ |

## `rules-v1.4.2.yaml`
```yaml
version: rules-v1.4.2
stage_params:
  ESTABLISHMENT: {trigger_vwc: 24, target_vwc: 32, active_root_zone_mm: 200}
  TILLERING:     {trigger_vwc: 23, target_vwc: 32, active_root_zone_mm: 250}
  GRAND_GROWTH:  {trigger_vwc: 25, target_vwc: 34, active_root_zone_mm: 300}
  MATURITY:      {trigger_vwc: 18, target_vwc: 26, active_root_zone_mm: 250}
temperature:
  hot_above_c: 30
  trigger_uplift_pp_per_c: 0.3      # raises trigger when hot
  max_uplift_pp: 2.0
rain:
  defer_if_prob_ge: 60              # -> DEFER_RAIN
  partial_if_prob_ge: 30            # -> reduce duration
  partial_discount_per_10pct: 0.05  # of duration, per 10 pp above 30
duration:
  min_h: 0.5
  max_h: 6.0
  round_to_h: 0.1
confidence:
  base: 0.55
  margin_weight: 0.35               # * min(1, (trigger - moisture)/6)
  rain_uncertain_band: [30, 70]
  rain_uncertain_penalty: 0.15
  stale_sensor_hours: 3
  stale_penalty: 0.10
  min: 0.05
  max: 0.98
```

## Algorithm (pure function)
```
stage = params[crop_stage]
hot_uplift = min(max_uplift, max(0, T - hot_above_c) * uplift_per_c)
trigger = stage.trigger_vwc + hot_uplift

if rain_prob >= defer_if_prob_ge:                       -> action DEFER_RAIN, duration 0, fired [R-RAIN-HIGH]
elif moisture >= trigger:                               -> action WAIT, duration 0, fired [R-MOISTURE-OK] (+ R-RAIN-* if relevant)
else:                                                   -> action IRRIGATE
     deficit_pp = stage.target_vwc - moisture
     deficit_mm = deficit_pp/100 * stage.active_root_zone_mm
     raw_h      = deficit_mm / application_rate_mm_h
     if rain_prob >= partial_if_prob_ge: raw_h *= 1 - (floor((rain_prob-30)/10)+1)*discount ; fired += R-RAIN-PARTIAL
     else fired += R-RAIN-NONE
     duration = clamp(round(raw_h,1), min_h, max_h) ; fired += R-TRIGGER-LOW ; (+R-HOT-UPLIFT if hot_uplift>0)
confidence per YAML; return Recommendation(action, duration, confidence, fired_rules)
```
**Worked example (must pass as a unit test):** Grand Growth, moisture 21, temp 33, rain 12, rate 14 mm/h → hot_uplift 0.9, trigger 25.9; deficit 13 pp → 39 mm → 39/14 = 2.79 → **2.8 h, IRRIGATE**, fired `[R-TRIGGER-LOW, R-HOT-UPLIFT, R-RAIN-NONE]`. Confidence ≈ 0.84.
**Second example:** Grand Growth, moisture 29, temp 29, rain 72 → **DEFER_RAIN** (R-RAIN-HIGH). (The product spec calls this "Wait"; UI label for `DEFER_RAIN` is "Wait — rain expected".)

## Deterministic explanation (authoritative text)
Build `factors[]`, each:
```json
{"id":"F1","input":"soil_moisture_pct","value":21,"unit":"%","comparison":"below","threshold":25.9,"effect":"supports_irrigation","text":"Soil moisture 21% is below the Grand Growth trigger of 25.9% (25% + 0.9 hot-weather uplift)."}
```
Factor order: moisture vs trigger → temperature uplift → rain → crop stage → duration derivation (deficit pp → mm → hours). Template sentence is assembled from factors (this is the fallback narrative).

## Comparison + flip analysis
1. `input_deltas`: every field in `EngineInputs` that differs, with signed delta and unit (`pp` for percentage-point changes).
2. `output_deltas`: action, duration, confidence.
3. `rule_deltas`: fired rules added/removed.
4. **Flip analysis**: for each differing input `i`: run engine on `A.inputs` with `i := B.inputs[i]`; record `alone_flips_action` and resulting action/duration. Repeat reversed (B with A's value). Report both directions. Text rule: "alone flips" only if true; otherwise "coincided with". Mention that interactions between inputs are not isolated.
5. Both decisions' **own pinned rulesets** are used for their own reproduction; flip analysis uses A's ruleset and says so if rulesets differ (and adds a warning chip "different rule versions").

## Reproduce check
`reproduce(decision_id)`: load snapshot → instantiate `RuleSet.from_json(snapshot.ruleset_json)` → run `IrrigationEngine` → compare with stored recommendation (action, duration, confidence, fired rules). Also compare `engine_code_sha256` to the current engine file hash: if the hash differs but outputs match, report "match (engine code changed)".

## Property tests (see doc 12)
Monotonic: lowering moisture never reduces duration; raising rain prob never increases duration; output in `[0, max_h]`; deterministic across 1000 random inputs.
