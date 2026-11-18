"""
Admin router: seeding and Qdrant re-indexing.
"""
from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from api.irrigatrace.api.deps import (
    get_services,
    ServicesContainer,
    require_role,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/seed")
def seed_database(
    user: Dict[str, str] = Depends(require_role("ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    from scripts.seed_scenario import run_seed
    try:
        run_seed()
        return {"status": "seeded", "message": "Demo scenario seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reindex")
def reindex_qdrant(
    user: Dict[str, str] = Depends(require_role("ADMIN")),
    services: ServicesContainer = Depends(get_services),
):
    decisions = services.decision_repo.list_decisions(page=1, page_size=500)
    indexed = 0
    for d in decisions:
        if services.similarity_service.index_decision(d.id):
            indexed += 1
    return {
        "status": "reindexed",
        "total_decisions": len(decisions),
        "indexed_in_qdrant": indexed,
        "mode": "qdrant" if indexed > 0 else "sql-fallback-active",
    }
