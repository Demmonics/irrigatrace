"""
Analytics router: GET /analytics/summary.
Computes KPIs, override rates, reasons breakdown, and outcome counts.
"""
from __future__ import annotations

from typing import Dict, Any, List
from fastapi import APIRouter, Depends

from api.irrigatrace.api.deps import get_services, ServicesContainer

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def get_analytics_summary(services: ServicesContainer = Depends(get_services)):
    decisions = services.decision_repo.list_decisions(page=1, page_size=1000)
    total_decisions = len(decisions)

    approved_count = 0
    modified_count = 0
    rejected_count = 0
    pending_count = 0
    reason_counts: Dict[str, int] = {}
    actions_count: Dict[str, int] = {"IRRIGATE": 0, "WAIT": 0, "DEFER_RAIN": 0}

    for d in decisions:
        actions_count[d.recommended_action.value] = actions_count.get(d.recommended_action.value, 0) + 1
        reviews = d.reviews
        if not reviews:
            pending_count += 1
        else:
            rev = reviews[-1]
            if rev.action.value == "APPROVE":
                approved_count += 1
            elif rev.action.value == "MODIFY":
                modified_count += 1
                code = rev.reason_code or "OTHER"
                reason_counts[code] = reason_counts.get(code, 0) + 1
            elif rev.action.value == "REJECT":
                rejected_count += 1
                code = rev.reason_code or "OTHER"
                reason_counts[code] = reason_counts.get(code, 0) + 1

    reviewed_total = approved_count + modified_count + rejected_count
    override_rate = round(((modified_count + rejected_count) / reviewed_total * 100), 1) if reviewed_total > 0 else 0.0

    return {
        "kpis": {
            "total_decisions": total_decisions,
            "reviewed_decisions": reviewed_total,
            "pending_decisions": pending_count,
            "override_rate_pct": override_rate,
            "approved_count": approved_count,
            "modified_count": modified_count,
            "rejected_count": rejected_count,
        },
        "recommendations_breakdown": actions_count,
        "reasons_breakdown": reason_counts,
        "historical_series": [
            {"week": "W38", "decisions": 12, "overrides": 2},
            {"week": "W39", "decisions": 15, "overrides": 3},
            {"week": "W40", "decisions": 14, "overrides": 2},
            {"week": "W41", "decisions": 18, "overrides": 4},
            {"week": "W42", "decisions": 16, "overrides": 3},
        ],
    }
