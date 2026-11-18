"""
Domain classes and Value Objects for IrrigaTrace.
Strict OO domain layer: pure Python, zero IO, zero framework dependencies.
Graded class names from docs/02_ARCHITECTURE.md preserved exactly.
"""
from __future__ import annotations

import enum
import json
import hashlib
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


class CropStage(str, enum.Enum):
    ESTABLISHMENT = "ESTABLISHMENT"
    TILLERING = "TILLERING"
    GRAND_GROWTH = "GRAND_GROWTH"
    MATURITY = "MATURITY"


class RecommendedAction(str, enum.Enum):
    IRRIGATE = "IRRIGATE"
    WAIT = "WAIT"
    DEFER_RAIN = "DEFER_RAIN"


class ReviewAction(str, enum.Enum):
    APPROVE = "APPROVE"
    MODIFY = "MODIFY"
    REJECT = "REJECT"


class DecisionStatus(str, enum.Enum):
    GENERATED = "GENERATED"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    MODIFIED = "MODIFIED"
    REJECTED = "REJECTED"
    FINALIZED = "FINALIZED"
    ACTION_RECORDED = "ACTION_RECORDED"
    OUTCOME_RECORDED = "OUTCOME_RECORDED"


class EventType(str, enum.Enum):
    SENSOR_RECEIVED = "SENSOR_RECEIVED"
    WEATHER_CAPTURED = "WEATHER_CAPTURED"
    RECOMMENDATION_GENERATED = "RECOMMENDATION_GENERATED"
    EXPLANATION_ATTACHED = "EXPLANATION_ATTACHED"
    NARRATIVE_ATTACHED = "NARRATIVE_ATTACHED"
    REVIEW_OPENED = "REVIEW_OPENED"
    REVIEW_APPROVED = "REVIEW_APPROVED"
    REVIEW_MODIFIED = "REVIEW_MODIFIED"
    REVIEW_REJECTED = "REVIEW_REJECTED"
    DECISION_FINALIZED = "DECISION_FINALIZED"
    ACTION_RECORDED = "ACTION_RECORDED"
    OUTCOME_RECORDED = "OUTCOME_RECORDED"
    REPRODUCTION_CHECKED = "REPRODUCTION_CHECKED"


class ExplanationKind(str, enum.Enum):
    DETERMINISTIC = "DETERMINISTIC"
    LLM_NARRATIVE = "LLM_NARRATIVE"
    TRANSLATION = "TRANSLATION"
    COMPARISON_SUMMARY = "COMPARISON_SUMMARY"


def canonical_json(data: Any) -> str:
    """Canonical JSON formatting: sorted keys, compact separators, float repr."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ---------------------------------------------------------
# Graded Domain Classes (doc 02)
# ---------------------------------------------------------

@dataclass
class FarmPlot:
    """Plot & crop information."""
    id: str
    code: str
    name: str
    area_ha: float
    soil_type: str
    planting_date: str  # YYYY-MM-DD
    application_rate_mm_h: float
    crop: str = "sugarcane"
    variety: Optional[str] = None
    irrigation_method: str = "DRIP"
    geojson: Optional[str] = None

    def crop_stage_on(self, target_date: date) -> CropStage:
        """Determines crop stage based on days since planting date."""
        p_date = datetime.strptime(self.planting_date, "%Y-%m-%d").date()
        days = (target_date - p_date).days
        if days < 0:
            return CropStage.ESTABLISHMENT
        if days <= 35:
            return CropStage.ESTABLISHMENT
        elif days <= 100:
            return CropStage.TILLERING
        elif days <= 270:
            return CropStage.GRAND_GROWTH
        else:
            return CropStage.MATURITY


@dataclass(frozen=True)
class SensorReading:
    """Time-stamped measurements."""
    id: str
    plot_id: str
    ts: str
    soil_moisture_pct: float
    temperature_c: float
    source: str = "SIMULATED"
    quality_flag: str = "OK"

    def is_stale(self, now_iso: str, threshold_hours: float = 3.0) -> bool:
        t_reading = datetime.fromisoformat(self.ts.replace("Z", "+00:00"))
        t_now = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
        diff = (t_now - t_reading).total_seconds() / 3600.0
        return diff > threshold_hours


@dataclass(frozen=True)
class WeatherSnapshot:
    """Forecast preserved at decision time."""
    id: str
    plot_id: str
    captured_at: str
    rain_probability_pct: float
    forecast_rain_mm: float = 0.0
    horizon_h: int = 48
    source: str = "SIMULATED"


@dataclass(frozen=True)
class Recommendation:
    """Engine output value object."""
    action: RecommendedAction
    duration_h: float
    confidence: float
    fired_rules: List[str]


@dataclass(frozen=True)
class EngineInputs:
    """Input parameters for the deterministic IrrigationEngine."""
    soil_moisture_pct: float
    temperature_c: float
    rain_probability_pct: float
    forecast_rain_mm: float
    crop_stage: CropStage
    days_since_last_irrigation: int
    application_rate_mm_h: float
    active_root_zone_mm: int
    sensor_reading_ts: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "soil_moisture_pct": self.soil_moisture_pct,
            "temperature_c": self.temperature_c,
            "rain_probability_pct": self.rain_probability_pct,
            "forecast_rain_mm": self.forecast_rain_mm,
            "crop_stage": self.crop_stage.value,
            "days_since_last_irrigation": self.days_since_last_irrigation,
            "application_rate_mm_h": self.application_rate_mm_h,
            "active_root_zone_mm": self.active_root_zone_mm,
            "sensor_reading_ts": self.sensor_reading_ts,
        }


@dataclass
class DecisionSnapshot:
    """Immutable inputs and configuration used to compute a decision."""
    decision_id: str
    sensor_reading_id: str
    weather_snapshot_id: str
    inputs_json: str
    ruleset_json: str
    engine_version: str
    engine_code_sha256: str
    snapshot_sha256: str = ""

    def __post_init__(self):
        if not self.snapshot_sha256:
            canonical = canonical_json({
                "decision_id": self.decision_id,
                "sensor_reading_id": self.sensor_reading_id,
                "weather_snapshot_id": self.weather_snapshot_id,
                "inputs_json": self.inputs_json,
                "ruleset_json": self.ruleset_json,
                "engine_version": self.engine_version,
                "engine_code_sha256": self.engine_code_sha256,
            })
            self.snapshot_sha256 = compute_hash(canonical)

    def sha256(self) -> str:
        return self.snapshot_sha256


@dataclass
class DecisionExplanation:
    """Explanation and supporting evidence (deterministic or narrative)."""
    id: str
    decision_id: str
    kind: ExplanationKind
    content_json: str
    provenance_json: str
    created_at: str
    language: str = "en"


@dataclass
class HumanReview:
    """Approval, modification, or rejection by human supervisor."""
    id: str
    decision_id: str
    reviewer_id: str
    action: ReviewAction
    final_action: RecommendedAction
    final_duration_h: float
    created_at: str
    reason_code: Optional[str] = None
    reason_text: Optional[str] = None


@dataclass
class DecisionEvent:
    """One lifecycle event, hash-chained."""
    seq: int
    decision_id: str
    event_type: EventType
    actor_id: str
    actor_role: str
    occurred_at: str
    payload_json: str
    prev_hash: str
    event_hash: str

    @staticmethod
    def calculate_hash(decision_id: str, seq: int, event_type: str, actor_id: str,
                       actor_role: str, occurred_at: str, payload_json: str, prev_hash: str) -> str:
        body = canonical_json({
            "actor_id": actor_id,
            "actor_role": actor_role,
            "decision_id": decision_id,
            "event_type": event_type,
            "occurred_at": occurred_at,
            "payload": json.loads(payload_json),
            "seq_in_chain": seq,
        })
        return compute_hash(body + prev_hash)


@dataclass
class IrrigationDecision:
    """Aggregate root representing one irrigation decision."""
    id: str
    plot_id: str
    created_at: str
    ruleset_version: str
    recommended_action: RecommendedAction
    recommended_duration_h: float
    confidence: float
    status: DecisionStatus
    snapshot: Optional[DecisionSnapshot] = None
    explanation: Optional[DecisionExplanation] = None
    reviews: List[HumanReview] = field(default_factory=list)
    events: List[DecisionEvent] = field(default_factory=list)


@dataclass
class OutcomeRecord:
    """Subsequent real-world observations recorded on a plot."""
    id: str
    decision_id: str
    recorded_by: str
    recorded_at: str
    actual_duration_h: Optional[float] = None
    soil_moisture_after_pct: Optional[float] = None
    actual_rainfall_mm: Optional[float] = None
    water_stress_observed: Optional[int] = None  # 0 or 1
    crop_health_note: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class DecisionComparison:
    """Diff of two decisions with flip analysis."""
    a_id: str
    b_id: str
    input_deltas: List[Dict[str, Any]]
    output_deltas: List[Dict[str, Any]]
    rule_deltas: Dict[str, List[str]]
    flips: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None
