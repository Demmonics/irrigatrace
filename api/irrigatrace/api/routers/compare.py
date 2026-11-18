"""
Comparison router: GET /compare and helper endpoints.
"""
from __future__ import annotations

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from api.irrigatrace.api.deps import get_services, ServicesContainer

router = APIRouter(prefix="", tags=["Comparison"])


@router.get("/compare")
def compare_decisions(
    a: str = Query(..., description="Decision A ID"),
    b: str = Query(..., description="Decision B ID"),
    services: ServicesContainer = Depends(get_services),
):
    try:
        comparison = services.comparison_service.compare(a, b)
        return {
            "a": comparison.a_id,
            "b": comparison.b_id,
            "input_deltas": comparison.input_deltas,
            "output_deltas": comparison.output_deltas,
            "rule_deltas": comparison.rule_deltas,
            "flips": comparison.flips,
            "summary": comparison.summary,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plots/{plot_id}/previous-decision")
def get_previous_decision(
    plot_id: str,
    before: Optional[str] = Query(None, description="ISO timestamp ceiling"),
    services: ServicesContainer = Depends(get_services),
):
    plot = services.plot_repo.get_by_id(plot_id)
    if not plot:
        plot = services.plot_repo.get_by_code(plot_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    dec = services.decision_repo.get_latest_for_plot(plot.id, before_date=before)
    if not dec:
        raise HTTPException(status_code=404, detail="No previous decision found")

    return {
        "id": dec.id,
        "plot_id": dec.plot_id,
        "action": dec.recommended_action.value,
        "duration_h": dec.recommended_duration_h,
        "created_at": dec.created_at,
        "status": dec.status.value,
    }
