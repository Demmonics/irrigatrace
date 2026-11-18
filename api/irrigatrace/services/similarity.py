"""
SimilaritySearchService and DecisionTextBuilder.
Handles semantic search, similar past decisions, and deterministic SQL nearest-neighbor fallback.
Obeys Invariant 8: Qdrant is a derived index; SQL is the source of truth.
"""
from __future__ import annotations

import json
import uuid
import math
from typing import Dict, Any, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from api.irrigatrace.domain.models import (
    IrrigationDecision,
    DecisionSnapshot,
    HumanReview,
    canonical_json,
)
from api.irrigatrace.domain.ports import DecisionRepository, PlotRepository


class DecisionTextBuilder:
    """Builds a deterministic canonical textual summary for embedding."""

    @staticmethod
    def build(decision: IrrigationDecision, plot_code: str, snapshot: DecisionSnapshot) -> str:
        inputs = json.loads(snapshot.inputs_json)
        stage = inputs.get("crop_stage", "unknown").lower()
        moisture = inputs.get("soil_moisture_pct", 0)
        temp = inputs.get("temperature_c", 0)
        rain_prob = inputs.get("rain_probability_pct", 0)

        action = decision.recommended_action.value.lower()
        duration = decision.recommended_duration_h

        final_part = ""
        if decision.reviews:
            rev = decision.reviews[-1]
            if rev.action.value == "MODIFY":
                final_part = f" Final: modified to {rev.final_duration_h} h. Reason: {rev.reason_code or 'overridden'}."
            elif rev.action.value == "REJECT":
                final_part = f" Final: rejected. Reason: {rev.reason_code or 'rejected'}."
            else:
                final_part = " Final: approved."

        return (
            f"Plot {plot_code} {stage}. "
            f"Soil moisture {moisture}%, temperature {temp}C, rain probability {rain_prob}%. "
            f"Recommended {action} {duration} h.{final_part}"
        )


class SimilaritySearchService:
    def __init__(
        self,
        decision_repo: DecisionRepository,
        plot_repo: PlotRepository,
        qdrant_client: Optional[QdrantClient] = None,
        ollama_host: str = "http://localhost:11434",
        embed_model: str = "nomic-embed-text",
    ):
        self.decision_repo = decision_repo
        self.plot_repo = plot_repo
        self.qdrant = qdrant_client
        self.ollama_host = ollama_host
        self.embed_model = embed_model
        self.collection_name = "decisions_v1"

    def get_embedding(self, text: str) -> Optional[List[float]]:
        import urllib.request
        try:
            url = f"{self.ollama_host.rstrip('/')}/api/embed"
            payload = {"model": self.embed_model, "input": text}
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                embeddings = data.get("embeddings")
                if embeddings and len(embeddings) > 0:
                    return embeddings[0]
        except Exception:
            pass
        return None

    def index_decision(self, decision_id: str) -> bool:
        if not self.qdrant:
            return False

        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            return False

        snapshot = self.decision_repo.get_snapshot(decision_id)
        if not snapshot:
            return False

        plot = self.plot_repo.get_by_id(decision.plot_id)
        plot_code = plot.code if plot else "UNKNOWN"

        text = DecisionTextBuilder.build(decision, plot_code, snapshot)
        vector = self.get_embedding(text)
        if not vector:
            return False

        # Ensure collection exists
        try:
            self.qdrant.get_collection(self.collection_name)
        except Exception:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(size=768, distance=qmodels.Distance.COSINE),
            )

        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, decision_id))
        inputs = json.loads(snapshot.inputs_json)
        payload = {
            "decision_id": decision_id,
            "plot_code": plot_code,
            "action": decision.recommended_action.value,
            "status": decision.status.value,
            "ruleset_version": decision.ruleset_version,
            "created_at": decision.created_at,
            "text": text,
            "crop_stage": inputs.get("crop_stage"),
            "moisture": inputs.get("soil_moisture_pct"),
            "temperature": inputs.get("temperature_c"),
            "rain_prob": inputs.get("rain_probability_pct"),
        }

        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[qmodels.PointStruct(id=point_id, vector=vector, payload=payload)],
        )
        return True

    def find_similar(self, decision_id: str, limit: int = 5, same_plot: bool = False) -> Dict[str, Any]:
        """
        Finds similar past decisions using Qdrant with SQL-nearest-neighbor fallback.
        """
        target_dec = self.decision_repo.get_by_id(decision_id)
        if not target_dec:
            raise ValueError(f"Decision {decision_id} not found")

        target_snap = self.decision_repo.get_snapshot(decision_id)
        if not target_snap:
            raise ValueError(f"Snapshot for decision {decision_id} not found")

        target_inputs = json.loads(target_snap.inputs_json)
        target_plot = self.plot_repo.get_by_id(target_dec.plot_id)
        target_code = target_plot.code if target_plot else ""

        # Try Qdrant semantic search first
        if self.qdrant:
            try:
                target_text = DecisionTextBuilder.build(target_dec, target_code, target_snap)
                vector = self.get_embedding(target_text)
                if vector:
                    query_filter = None
                    if same_plot and target_code:
                        query_filter = qmodels.Filter(
                            must=[qmodels.FieldCondition(key="plot_code", match=qmodels.MatchValue(value=target_code))]
                        )
                    results = self.qdrant.search(
                        collection_name=self.collection_name,
                        query_vector=vector,
                        query_filter=query_filter,
                        limit=limit + 1,
                    )
                    hits = []
                    for r in results:
                        d_id = r.payload.get("decision_id")
                        if d_id == decision_id:
                            continue
                        dec_item = self.decision_repo.get_by_id(d_id)
                        snap_item = self.decision_repo.get_snapshot(d_id)
                        inputs_item = json.loads(snap_item.inputs_json) if snap_item else {}
                        deltas = {
                            "moisture_diff": round(inputs_item.get("soil_moisture_pct", 0) - target_inputs.get("soil_moisture_pct", 0), 1),
                            "temp_diff": round(inputs_item.get("temperature_c", 0) - target_inputs.get("temperature_c", 0), 1),
                            "rain_diff": round(inputs_item.get("rain_probability_pct", 0) - target_inputs.get("rain_probability_pct", 0), 1),
                        }
                        hits.append({
                            "decision_id": d_id,
                            "plot_code": r.payload.get("plot_code"),
                            "action": r.payload.get("action"),
                            "score": round(float(r.score), 3),
                            "created_at": r.payload.get("created_at"),
                            "deltas": deltas,
                        })
                    if hits:
                        return {
                            "source": "qdrant-vector",
                            "label": "Similar past decisions (semantic match — not proof of causal similarity)",
                            "results": hits[:limit],
                        }
            except Exception:
                pass

        # SQL-based Nearest-Neighbour Fallback
        all_decisions = self.decision_repo.list_decisions(
            plot_code=target_code if same_plot else None,
            page=1,
            page_size=100,
        )

        ranked = []
        t_moist = float(target_inputs.get("soil_moisture_pct", 0))
        t_temp = float(target_inputs.get("temperature_c", 0))
        t_rain = float(target_inputs.get("rain_probability_pct", 0))

        for dec in all_decisions:
            if dec.id == decision_id:
                continue
            snap = self.decision_repo.get_snapshot(dec.id)
            if not snap:
                continue
            inp = json.loads(snap.inputs_json)
            c_moist = float(inp.get("soil_moisture_pct", 0))
            c_temp = float(inp.get("temperature_c", 0))
            c_rain = float(inp.get("rain_probability_pct", 0))

            # Normalized Euclidean distance
            dist = math.sqrt(
                ((c_moist - t_moist) / 20.0) ** 2 +
                ((c_temp - t_temp) / 10.0) ** 2 +
                ((c_rain - t_rain) / 50.0) ** 2
            )
            score = max(0.0, round(1.0 - (dist / 3.0), 3))
            p = self.plot_repo.get_by_id(dec.plot_id)
            code = p.code if p else ""
            ranked.append({
                "decision_id": dec.id,
                "plot_code": code,
                "action": dec.recommended_action.value,
                "score": score,
                "created_at": dec.created_at,
                "deltas": {
                    "moisture_diff": round(c_moist - t_moist, 1),
                    "temp_diff": round(c_temp - t_temp, 1),
                    "rain_diff": round(c_rain - t_rain, 1),
                },
                "_dist": dist,
            })

        ranked.sort(key=lambda x: x["_dist"])
        cleaned = [{k: v for k, v in item.items() if k != "_dist"} for item in ranked[:limit]]

        return {
            "source": "sql-fallback",
            "label": "Similar past decisions (normalized distance match — not proof of causal similarity)",
            "results": cleaned,
        }
