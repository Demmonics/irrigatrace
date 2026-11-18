"""
Plots, Sensors, Weather, Simulator, and Engine Preview router.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, date
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from api.irrigatrace.api.deps import (
    get_services,
    ServicesContainer,
    get_current_user,
    require_role,
)
from api.irrigatrace.api.schemas import (
    PlotResponse,
    PlotCreateRequest,
    SensorReadingRequest,
    WeatherSnapshotRequest,
    SimulatorStepRequest,
    EnginePreviewRequest,
    EnginePreviewResponse,
)
from api.irrigatrace.domain.models import (
    FarmPlot,
    SensorReading,
    WeatherSnapshot,
    EngineInputs,
    CropStage,
)
from api.irrigatrace.domain.engine import IrrigationEngine

router = APIRouter(prefix="", tags=["Plots & Sensors"])


@router.get("/plots", response_model=List[PlotResponse])
def list_plots(services: ServicesContainer = Depends(get_services)):
    plots = services.plot_repo.list_all()
    result = []
    now_date = datetime.now(timezone.utc).date()
    for p in plots:
        stage = p.crop_stage_on(now_date).value
        latest_reading = services.sensor_repo.get_latest_for_plot(p.id)
        latest_decision = services.decision_repo.get_latest_for_plot(p.id)
        result.append(
            PlotResponse(
                id=p.id,
                code=p.code,
                name=p.name,
                area_ha=p.area_ha,
                soil_type=p.soil_type,
                crop=p.crop,
                variety=p.variety,
                planting_date=p.planting_date,
                irrigation_method=p.irrigation_method,
                application_rate_mm_h=p.application_rate_mm_h,
                geojson=p.geojson,
                current_stage=stage,
                latest_reading={
                    "soil_moisture_pct": latest_reading.soil_moisture_pct,
                    "temperature_c": latest_reading.temperature_c,
                    "ts": latest_reading.ts,
                } if latest_reading else None,
                latest_decision={
                    "id": latest_decision.id,
                    "action": latest_decision.recommended_action.value,
                    "duration_h": latest_decision.recommended_duration_h,
                    "status": latest_decision.status.value,
                    "created_at": latest_decision.created_at,
                } if latest_decision else None,
            )
        )
    return result


@router.get("/plots/{plot_id}", response_model=PlotResponse)
def get_plot(plot_id: str, services: ServicesContainer = Depends(get_services)):
    p = services.plot_repo.get_by_id(plot_id)
    if not p:
        p = services.plot_repo.get_by_code(plot_id)
    if not p:
        raise HTTPException(status_code=404, detail="Plot not found")

    now_date = datetime.now(timezone.utc).date()
    stage = p.crop_stage_on(now_date).value
    latest_reading = services.sensor_repo.get_latest_for_plot(p.id)
    latest_decision = services.decision_repo.get_latest_for_plot(p.id)

    return PlotResponse(
        id=p.id,
        code=p.code,
        name=p.name,
        area_ha=p.area_ha,
        soil_type=p.soil_type,
        crop=p.crop,
        variety=p.variety,
        planting_date=p.planting_date,
        irrigation_method=p.irrigation_method,
        application_rate_mm_h=p.application_rate_mm_h,
        geojson=p.geojson,
        current_stage=stage,
        latest_reading={
            "soil_moisture_pct": latest_reading.soil_moisture_pct,
            "temperature_c": latest_reading.temperature_c,
            "ts": latest_reading.ts,
        } if latest_reading else None,
        latest_decision={
            "id": latest_decision.id,
            "action": latest_decision.recommended_action.value,
            "duration_h": latest_decision.recommended_duration_h,
            "status": latest_decision.status.value,
            "created_at": latest_decision.created_at,
        } if latest_decision else None,
    )


@router.post("/plots", response_model=PlotResponse)
def create_plot(
    req: PlotCreateRequest,
    user: Dict[str, str] = Depends(require_role("ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    plot_id = f"plot-{uuid.uuid4().hex[:8]}"
    plot = FarmPlot(
        id=plot_id,
        code=req.code,
        name=req.name,
        area_ha=req.area_ha,
        soil_type=req.soil_type,
        crop="sugarcane",
        variety=req.variety,
        planting_date=req.planting_date,
        irrigation_method=req.irrigation_method or "DRIP",
        application_rate_mm_h=req.application_rate_mm_h,
        geojson=req.geojson,
    )
    services.plot_repo.save(plot)
    return get_plot(plot_id, services)


@router.post("/sensor-readings")
def record_sensor_reading(
    req: SensorReadingRequest,
    user: Dict[str, str] = Depends(require_role("SUPERVISOR", "ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    plot = services.plot_repo.get_by_id(req.plot_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    reading = SensorReading(
        id=f"read-{uuid.uuid4().hex[:8]}",
        plot_id=req.plot_id,
        ts=req.ts or services.clock.now_iso(),
        soil_moisture_pct=req.soil_moisture_pct,
        temperature_c=req.temperature_c,
        source=req.source or "MANUAL",
        quality_flag="OK",
    )
    services.sensor_repo.save(reading)
    return {"id": reading.id, "status": "recorded"}


@router.post("/weather-snapshots")
def record_weather_snapshot(
    req: WeatherSnapshotRequest,
    user: Dict[str, str] = Depends(require_role("SUPERVISOR", "ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    plot = services.plot_repo.get_by_id(req.plot_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    snapshot = WeatherSnapshot(
        id=f"wsnap-{uuid.uuid4().hex[:8]}",
        plot_id=req.plot_id,
        captured_at=req.captured_at or services.clock.now_iso(),
        rain_probability_pct=req.rain_probability_pct,
        forecast_rain_mm=req.forecast_rain_mm or 0.0,
        horizon_h=req.horizon_h or 48,
        source=req.source or "MANUAL",
    )
    services.weather_repo.save(snapshot)
    return {"id": snapshot.id, "status": "recorded"}


@router.post("/simulator/step")
def simulator_step(
    req: SimulatorStepRequest,
    user: Dict[str, str] = Depends(require_role("ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    plot = services.plot_repo.get_by_id(req.plot_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    latest_reading = services.sensor_repo.get_latest_for_plot(plot.id)
    base_moisture = latest_reading.soil_moisture_pct if latest_reading else 28.0
    new_moisture = max(5.0, min(95.0, round(base_moisture + req.moisture_delta_pct, 1)))

    now = services.clock.now_iso()
    reading = SensorReading(
        id=f"sim-read-{uuid.uuid4().hex[:8]}",
        plot_id=plot.id,
        ts=now,
        soil_moisture_pct=new_moisture,
        temperature_c=req.temperature_c,
        source="SIMULATED",
        quality_flag="OK",
    )
    services.sensor_repo.save(reading)

    weather = WeatherSnapshot(
        id=f"sim-wsnap-{uuid.uuid4().hex[:8]}",
        plot_id=plot.id,
        captured_at=now,
        rain_probability_pct=req.rain_probability_pct,
        forecast_rain_mm=req.forecast_rain_mm,
        horizon_h=48,
        source="SIMULATED",
    )
    services.weather_repo.save(weather)

    return {
        "status": "stepped",
        "plot_id": plot.id,
        "soil_moisture_pct": new_moisture,
        "temperature_c": req.temperature_c,
        "rain_probability_pct": req.rain_probability_pct,
        "sensor_reading_id": reading.id,
        "weather_snapshot_id": weather.id,
    }


@router.post("/engine/preview", response_model=EnginePreviewResponse)
def engine_preview(
    req: EnginePreviewRequest,
    services: ServicesContainer = Depends(get_services),
):
    """
    Stateless calculation: inputs -> engine output + factors.
    Writes nothing to the database (powers Lab Bench live preview).
    """
    inputs = EngineInputs(
        soil_moisture_pct=req.soil_moisture_pct,
        temperature_c=req.temperature_c,
        rain_probability_pct=req.rain_probability_pct,
        forecast_rain_mm=req.forecast_rain_mm,
        crop_stage=CropStage(req.crop_stage),
        days_since_last_irrigation=req.days_since_last_irrigation,
        application_rate_mm_h=req.application_rate_mm_h,
        active_root_zone_mm=req.active_root_zone_mm,
    )
    rec = IrrigationEngine.recommend(inputs, services.ruleset)
    expl = IrrigationEngine.build_deterministic_explanation(inputs, services.ruleset, rec)

    return EnginePreviewResponse(
        action=rec.action.value,
        duration_h=rec.duration_h,
        confidence=rec.confidence,
        fired_rules=rec.fired_rules,
        factors=expl["factors"],
        template_narrative=expl["template_narrative"],
    )
