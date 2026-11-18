"""
Audit router: GET /audit/verify and GET /audit/verify-all.
"""
from __future__ import annotations

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from api.irrigatrace.api.deps import get_services, ServicesContainer

router = APIRouter(prefix="/audit", tags=["Audit & Integrity"])


@router.get("/verify")
def verify_decision_integrity(
    decision_id: str = Query(..., description="Decision ID to audit"),
    services: ServicesContainer = Depends(get_services),
):
    res = services.integrity_service.verify(decision_id)
    if not res.get("valid"):
        return res
    return res


@router.get("/verify-all")
def verify_all_decisions(services: ServicesContainer = Depends(get_services)):
    return services.integrity_service.verify_all()
