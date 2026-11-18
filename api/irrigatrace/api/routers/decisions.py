"""
Decisions router: lifecycle, case file, review, replay, reproduce, similar, and SSE streaming.
"""
from __future__ import annotations

import json
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import StreamingResponse

from api.irrigatrace.api.deps import (
    get_services,
    ServicesContainer,
    get_current_user,
    require_role,
)
from api.irrigatrace.api.schemas import (
    DecisionCreateRequest,
    ReviewSubmitRequest,
    ActionRecordRequest,
    OutcomeRecordRequest,
    TranslationRequest,
)
from api.irrigatrace.domain.models import (
    ReviewAction,
    RecommendedAction,
    DecisionStatus,
    ExplanationKind,
)
from api.irrigatrace.api.sse import broadcaster

router = APIRouter(prefix="/decisions", tags=["Decisions"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_decision(
    req: DecisionCreateRequest,
    background_tasks: BackgroundTasks,
    user: Dict[str, str] = Depends(require_role("SUPERVISOR", "ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    try:
        decision = services.recorder.record_new_decision(
            plot_id=req.plot_id,
            ruleset=services.ruleset,
            sensor_reading_id=req.sensor_reading_id,
            weather_snapshot_id=req.weather_snapshot_id,
            actor_id=user["id"],
            actor_role=user["role"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Trigger background narration and indexing
    background_tasks.add_task(services.narration_service.narrate_decision, decision.id)
    background_tasks.add_task(services.similarity_service.index_decision, decision.id)

    return get_decision(decision.id, services)


@router.get("")
def list_decisions(
    plot_code: Optional[str] = Query(None),
    status: Optional[List[str]] = Query(None),
    overridden: Optional[bool] = Query(None),
    ruleset: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    action: Optional[List[str]] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    services: ServicesContainer = Depends(get_services),
):
    decisions = services.decision_repo.list_decisions(
        plot_code=plot_code,
        status=status,
        overridden=overridden,
        ruleset_version=ruleset,
        date_from=date_from,
        date_to=date_to,
        action=action,
        search_query=q,
        page=page,
        page_size=page_size,
    )
    total = services.decision_repo.count_decisions(
        plot_code=plot_code,
        status=status,
        overridden=overridden,
    )

    items = []
    for d in decisions:
        plot = services.plot_repo.get_by_id(d.plot_id)
        last_review = d.reviews[-1] if d.reviews else None
        final_info = None
        if last_review:
            final_info = {
                "action": last_review.final_action.value,
                "duration_h": last_review.final_duration_h,
                "source": "HUMAN_APPROVED" if last_review.action == ReviewAction.APPROVE else "HUMAN_MODIFIED",
            }
        items.append({
            "id": d.id,
            "plot": {"id": plot.id, "code": plot.code, "name": plot.name} if plot else {"id": d.plot_id, "code": "UNKNOWN"},
            "created_at": d.created_at,
            "status": d.status.value,
            "recommendation": {
                "action": d.recommended_action.value,
                "duration_h": d.recommended_duration_h,
                "confidence": d.confidence,
                "ruleset_version": d.ruleset_version,
            },
            "final": final_info,
            "overridden": any(r.action != ReviewAction.APPROVE for r in d.reviews),
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{decision_id}")
def get_decision(decision_id: str, services: ServicesContainer = Depends(get_services)):
    dec = services.decision_repo.get_by_id(decision_id)
    if not dec:
        raise HTTPException(status_code=404, detail="Decision not found")

    plot = services.plot_repo.get_by_id(dec.plot_id)
    snapshot = services.decision_repo.get_snapshot(decision_id)
    explanations = services.decision_repo.get_explanations(decision_id)
    reviews = services.decision_repo.get_reviews(decision_id)
    outcome = services.decision_repo.get_outcome(decision_id)
    integrity = services.integrity_service.verify(decision_id)

    det_expl = next((e for e in explanations if e.kind == ExplanationKind.DETERMINISTIC), None)
    narr_expl = next((e for e in explanations if e.kind == ExplanationKind.LLM_NARRATIVE), None)
    tr_expls = [e for e in explanations if e.kind == ExplanationKind.TRANSLATION]

    final_info = None
    if reviews:
        last_rev = reviews[-1]
        final_info = {
            "action": last_rev.final_action.value,
            "duration_h": last_rev.final_duration_h,
            "source": "HUMAN_APPROVED" if last_rev.action == ReviewAction.APPROVE else "HUMAN_MODIFIED",
        }

    return {
        "id": dec.id,
        "plot": {"id": plot.id, "code": plot.code, "name": plot.name, "area_ha": plot.area_ha} if plot else {"id": dec.plot_id},
        "status": dec.status.value,
        "created_at": dec.created_at,
        "recommendation": {
            "action": dec.recommended_action.value,
            "duration_h": dec.recommended_duration_h,
            "confidence": dec.confidence,
            "ruleset_version": dec.ruleset_version,
        },
        "final": final_info,
        "snapshot": {
            "inputs": json.loads(snapshot.inputs_json) if snapshot else {},
            "engine_version": snapshot.engine_version if snapshot else "",
            "snapshot_sha256": snapshot.snapshot_sha256 if snapshot else "",
        } if snapshot else None,
        "explanation": {
            "deterministic": json.loads(det_expl.content_json) if det_expl else None,
            "narrative": {
                "text": json.loads(narr_expl.content_json).get("narrative", "") if narr_expl else "",
                "provenance": json.loads(narr_expl.provenance_json) if narr_expl else None,
            } if narr_expl else None,
            "translations": [
                {
                    "language": t.language,
                    "content": json.loads(t.content_json),
                    "provenance": json.loads(t.provenance_json),
                } for t in tr_expls
            ],
        },
        "reviews": [
            {
                "id": r.id,
                "reviewer_id": r.reviewer_id,
                "action": r.action.value,
                "reason_code": r.reason_code,
                "reason_text": r.reason_text,
                "final_action": r.final_action.value,
                "final_duration_h": r.final_duration_h,
                "created_at": r.created_at,
            } for r in reviews
        ],
        "outcome": {
            "id": outcome.id,
            "recorded_by": outcome.recorded_by,
            "recorded_at": outcome.recorded_at,
            "actual_duration_h": outcome.actual_duration_h,
            "soil_moisture_after_pct": outcome.soil_moisture_after_pct,
            "actual_rainfall_mm": outcome.actual_rainfall_mm,
            "water_stress_observed": outcome.water_stress_observed,
            "crop_health_note": outcome.crop_health_note,
            "notes": outcome.notes,
        } if outcome else None,
        "integrity": {
            "valid": integrity.get("valid", False),
            "events": len(dec.events),
            "head_hash": integrity.get("head_hash"),
        },
    }


@router.post("/{decision_id}/review")
def review_decision(
    decision_id: str,
    req: ReviewSubmitRequest,
    user: Dict[str, str] = Depends(require_role("SUPERVISOR", "ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    try:
        action_enum = ReviewAction(req.action.upper())
        final_act_enum = RecommendedAction(req.final_action.upper()) if req.final_action else None
        review = services.review_service.submit_review(
            decision_id=decision_id,
            reviewer_id=user["id"],
            reviewer_role=user["role"],
            action=action_enum,
            reason_code=req.reason_code,
            reason_text=req.reason_text,
            final_action=final_act_enum,
            final_duration_h=req.final_duration_h,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return get_decision(decision_id, services)


@router.post("/{decision_id}/action")
def record_decision_action(
    decision_id: str,
    req: ActionRecordRequest,
    user: Dict[str, str] = Depends(require_role("SUPERVISOR", "ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    try:
        res = services.outcome_service.record_action(
            decision_id=decision_id,
            actual_duration_h=req.actual_duration_h,
            executed_at=req.executed_at or services.clock.now_iso(),
            actor_id=user["id"],
            actor_role=user["role"],
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{decision_id}/outcome")
def record_decision_outcome(
    decision_id: str,
    req: OutcomeRecordRequest,
    user: Dict[str, str] = Depends(require_role("SUPERVISOR", "ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    try:
        outcome = services.outcome_service.record_outcome(
            decision_id=decision_id,
            recorded_by=user["id"],
            actual_duration_h=req.actual_duration_h,
            soil_moisture_after_pct=req.soil_moisture_after_pct,
            actual_rainfall_mm=req.actual_rainfall_mm,
            water_stress_observed=req.water_stress_observed,
            crop_health_note=req.crop_health_note,
            notes=req.notes,
        )
        return {"id": outcome.id, "status": "recorded"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{decision_id}/replay")
def get_decision_replay(decision_id: str, services: ServicesContainer = Depends(get_services)):
    timeline = services.replay_service.timeline(decision_id)
    return {"decision_id": decision_id, "timeline": timeline}


@router.get("/{decision_id}/replay/state")
def get_decision_state_at(
    decision_id: str,
    at: str = Query(..., description="Target ISO timestamp"),
    services: ServicesContainer = Depends(get_services),
):
    try:
        return services.replay_service.state_at(decision_id, at)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{decision_id}/reproduce")
def check_reproduction(decision_id: str, services: ServicesContainer = Depends(get_services)):
    try:
        return services.replay_service.reproduce(decision_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{decision_id}/similar")
def get_similar_decisions(
    decision_id: str,
    limit: int = Query(5, ge=1, le=10),
    same_plot: bool = Query(False),
    services: ServicesContainer = Depends(get_services),
):
    try:
        return services.similarity_service.find_similar(decision_id, limit=limit, same_plot=same_plot)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{decision_id}/translate")
def translate_decision(
    decision_id: str,
    req: TranslationRequest,
    user: Dict[str, str] = Depends(require_role("SUPERVISOR", "ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    try:
        expl = services.translation_service.translate(decision_id, req.language)
        return {
            "id": expl.id,
            "language": expl.language,
            "content": json.loads(expl.content_json),
            "provenance": json.loads(expl.provenance_json),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{decision_id}/stream")
async def stream_decision_events(decision_id: str):
    queue = broadcaster.subscribe(decision_id)

    async def event_generator():
        try:
            while True:
                msg = await queue.get()
                yield msg
        except asyncio.CancelledError:
            pass
        finally:
            broadcaster.unsubscribe(decision_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
