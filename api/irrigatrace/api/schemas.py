"""
Pydantic v2 schemas for API requests and responses.
Auto-generates clean OpenAPI schema feeding TypeScript types.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PlotResponse(BaseModel):
    id: str
    code: str
    name: str
    area_ha: float
    soil_type: str
    crop: str
    variety: Optional[str] = None
    planting_date: str
    irrigation_method: str
    application_rate_mm_h: float
    geojson: Optional[str] = None
    current_stage: Optional[str] = None
    latest_reading: Optional[Dict[str, Any]] = None
    latest_decision: Optional[Dict[str, Any]] = None


class PlotCreateRequest(BaseModel):
    code: str
    name: str
    area_ha: float
    soil_type: str
    planting_date: str
    application_rate_mm_h: float
    variety: Optional[str] = "Co 86032"
    irrigation_method: Optional[str] = "DRIP"
    geojson: Optional[str] = None


class SensorReadingRequest(BaseModel):
    plot_id: str
    soil_moisture_pct: float
    temperature_c: float
    source: Optional[str] = "MANUAL"
    ts: Optional[str] = None


class WeatherSnapshotRequest(BaseModel):
    plot_id: str
    rain_probability_pct: float
    forecast_rain_mm: Optional[float] = 0.0
    horizon_h: Optional[int] = 48
    source: Optional[str] = "MANUAL"
    captured_at: Optional[str] = None


class SimulatorStepRequest(BaseModel):
    plot_id: str
    moisture_delta_pct: float = -1.5
    temperature_c: float = 32.0
    rain_probability_pct: float = 15.0
    forecast_rain_mm: float = 0.0


class EnginePreviewRequest(BaseModel):
    soil_moisture_pct: float
    temperature_c: float
    rain_probability_pct: float
    forecast_rain_mm: float = 0.0
    crop_stage: str = "GRAND_GROWTH"
    days_since_last_irrigation: int = 7
    application_rate_mm_h: float = 14.0
    active_root_zone_mm: int = 300


class EnginePreviewResponse(BaseModel):
    action: str
    duration_h: float
    confidence: float
    fired_rules: List[str]
    factors: List[Dict[str, Any]]
    template_narrative: str


class DecisionCreateRequest(BaseModel):
    plot_id: str
    sensor_reading_id: Optional[str] = None
    weather_snapshot_id: Optional[str] = None


class ReviewSubmitRequest(BaseModel):
    action: str  # APPROVE, MODIFY, REJECT
    reason_code: Optional[str] = None
    reason_text: Optional[str] = None
    final_action: Optional[str] = None
    final_duration_h: Optional[float] = None


class ActionRecordRequest(BaseModel):
    actual_duration_h: float
    executed_at: Optional[str] = None


class OutcomeRecordRequest(BaseModel):
    actual_duration_h: Optional[float] = None
    soil_moisture_after_pct: Optional[float] = None
    actual_rainfall_mm: Optional[float] = None
    water_stress_observed: Optional[int] = None
    crop_health_note: Optional[str] = None
    notes: Optional[str] = None


class TranslationRequest(BaseModel):
    language: str  # hi, kn


class SemanticSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5


class QueryParseRequest(BaseModel):
    user_query: str


class HealthResponse(BaseModel):
    db: str
    ollama: str
    qdrant: str
    gemini: str
    models: Dict[str, bool]
    status: str
