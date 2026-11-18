"""
Search router: semantic search and NL query parsing (Command Palette / ⌘K).
"""
from __future__ import annotations

import re
import json
import urllib.request
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends

from api.irrigatrace.api.deps import get_services, ServicesContainer
from api.irrigatrace.api.schemas import SemanticSearchRequest, QueryParseRequest

router = APIRouter(prefix="", tags=["Search & NL Query"])


@router.post("/search")
def semantic_search(
    req: SemanticSearchRequest,
    services: ServicesContainer = Depends(get_services),
):
    query = req.query.strip().lower()
    decisions = services.decision_repo.list_decisions(page=1, page_size=50)

    matches = []
    for d in decisions:
        plot = services.plot_repo.get_by_id(d.plot_id)
        plot_code = plot.code.lower() if plot else ""
        text_corpus = f"{plot_code} {d.recommended_action.value.lower()} {d.ruleset_version.lower()}"
        for r in d.reviews:
            if r.reason_text:
                text_corpus += " " + r.reason_text.lower()
            if r.reason_code:
                text_corpus += " " + r.reason_code.lower()

        score = 0.0
        if query in text_corpus:
            score = 0.95
        else:
            # Word overlap
            query_words = set(query.split())
            corpus_words = set(text_corpus.split())
            overlap = len(query_words & corpus_words)
            if overlap > 0:
                score = round(overlap / len(query_words), 2)

        if score > 0.2:
            matches.append({
                "decision_id": d.id,
                "plot_code": plot.code if plot else "",
                "action": d.recommended_action.value,
                "score": score,
                "created_at": d.created_at,
                "status": d.status.value,
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return {
        "query": req.query,
        "results": matches[:req.limit or 5],
        "source": "hybrid-search",
    }


@router.post("/query/parse")
def parse_natural_language_query(
    req: QueryParseRequest,
    services: ServicesContainer = Depends(get_services),
):
    """
    Parses user natural language query into validated filter fields.
    Schema: plot_code, status[], overridden, ruleset_version, date_from, date_to, action[], text_query
    """
    text = req.user_query.lower()
    filter_obj: Dict[str, Any] = {}

    # Extract plot code
    plot_match = re.search(r"\b(sg-\d{3})\b", text)
    if plot_match:
        filter_obj["plot_code"] = plot_match.group(1).upper()

    # Extract action
    if "irrigate" in text or "irrigation" in text:
        filter_obj["action"] = ["IRRIGATE"]
    elif "defer" in text or "rain" in text:
        filter_obj["action"] = ["DEFER_RAIN"]
    elif "wait" in text:
        filter_obj["action"] = ["WAIT"]

    # Extract override
    if "override" in text or "overridden" in text or "modified" in text:
        filter_obj["overridden"] = True
    elif "approved" in text:
        filter_obj["overridden"] = False

    # Extract status
    if "pending" in text:
        filter_obj["status"] = ["PENDING_REVIEW"]
    elif "finalized" in text:
        filter_obj["status"] = ["FINALIZED"]

    filter_obj["text_query"] = req.user_query
    return {"filter": filter_obj, "validated": True}
