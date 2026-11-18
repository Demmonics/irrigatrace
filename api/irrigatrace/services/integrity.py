"""
IntegrityService for cryptographic audit verification.
Verifies event hash chains, snapshot integrity, and status projection consistency.
"""
from __future__ import annotations

import json
from typing import Dict, Any, List, Optional

from api.irrigatrace.domain.models import (
    EventType,
    DecisionStatus,
    compute_hash,
    canonical_json,
)
from api.irrigatrace.domain.ports import DecisionRepository, Clock


class IntegrityService:
    def __init__(self, decision_repo: DecisionRepository, clock: Clock):
        self.decision_repo = decision_repo
        self.clock = clock

    def verify(self, decision_id: str) -> Dict[str, Any]:
        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            return {"valid": False, "reason": f"Decision {decision_id} not found", "decision_id": decision_id}

        events = self.decision_repo.get_events(decision_id)
        if not events:
            return {"valid": False, "reason": "No events found in audit chain", "decision_id": decision_id}

        # 1. Verify Snapshot SHA-256
        snapshot = self.decision_repo.get_snapshot(decision_id)
        if not snapshot:
            return {"valid": False, "reason": "Snapshot missing", "decision_id": decision_id}

        expected_snapshot_hash = compute_hash(canonical_json({
            "decision_id": snapshot.decision_id,
            "sensor_reading_id": snapshot.sensor_reading_id,
            "weather_snapshot_id": snapshot.weather_snapshot_id,
            "inputs_json": snapshot.inputs_json,
            "ruleset_json": snapshot.ruleset_json,
            "engine_version": snapshot.engine_version,
            "engine_code_sha256": snapshot.engine_code_sha256,
        }))
        if snapshot.snapshot_sha256 != expected_snapshot_hash:
            return {
                "valid": False,
                "reason": "Snapshot hash mismatch (inputs or ruleset tampered)",
                "decision_id": decision_id,
            }

        # 2. Recompute and Verify Event Hash Chain
        genesis_hash = compute_hash(f"GENESIS:{decision_id}")
        expected_prev_hash = genesis_hash

        projected_status = DecisionStatus.PENDING_REVIEW

        for i, ev in enumerate(events):
            seq_in_chain = i + 1
            if ev.prev_hash != expected_prev_hash:
                return {
                    "valid": False,
                    "broken_at_seq": seq_in_chain,
                    "reason": f"Hash chain broken at event {seq_in_chain}: prev_hash mismatch",
                    "decision_id": decision_id,
                }

            expected_ev_hash = compute_hash(
                canonical_json({
                    "actor_id": ev.actor_id,
                    "actor_role": ev.actor_role,
                    "decision_id": decision_id,
                    "event_type": ev.event_type.value,
                    "occurred_at": ev.occurred_at,
                    "payload": json.loads(ev.payload_json),
                    "seq_in_chain": seq_in_chain,
                }) + expected_prev_hash
            )

            if ev.event_hash != expected_ev_hash:
                return {
                    "valid": False,
                    "broken_at_seq": seq_in_chain,
                    "reason": f"Event hash invalid at sequence {seq_in_chain}",
                    "decision_id": decision_id,
                }

            expected_prev_hash = ev.event_hash

            # Project status
            if ev.event_type == EventType.DECISION_FINALIZED:
                projected_status = DecisionStatus.FINALIZED
            elif ev.event_type == EventType.ACTION_RECORDED:
                projected_status = DecisionStatus.ACTION_RECORDED
            elif ev.event_type == EventType.OUTCOME_RECORDED:
                projected_status = DecisionStatus.OUTCOME_RECORDED

        # 3. Check Status Projection
        if decision.status != projected_status:
            return {
                "valid": False,
                "reason": f"Status projection mismatch: row has '{decision.status.value}', event stream projects '{projected_status.value}'",
                "decision_id": decision_id,
            }

        return {
            "valid": True,
            "decision_id": decision_id,
            "event_count": len(events),
            "head_hash": events[-1].event_hash,
            "genesis_hash": genesis_hash,
            "status": decision.status.value,
            "verified_at": self.clock.now_iso(),
        }

    def verify_all(self) -> Dict[str, Any]:
        decisions = self.decision_repo.list_decisions(page=1, page_size=1000)
        total = len(decisions)
        valid_count = 0
        invalid_results = []

        for dec in decisions:
            res = self.verify(dec.id)
            if res.get("valid"):
                valid_count += 1
            else:
                invalid_results.append(res)

        return {
            "total_decisions": total,
            "valid_decisions": valid_count,
            "corrupted_decisions": len(invalid_results),
            "all_valid": (valid_count == total and total > 0),
            "invalid_details": invalid_results,
            "verified_at": self.clock.now_iso(),
        }
