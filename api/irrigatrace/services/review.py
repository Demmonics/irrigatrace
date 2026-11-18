"""
ReviewService for IrrigaTrace.
Enforces Invariant 1: Never overwrite the AI's original recommendation.
Human reviews are new records; emits hash-chained events and updates status.
"""
from __future__ import annotations

import uuid
from typing import Optional, Dict, Any

from api.irrigatrace.domain.models import (
    HumanReview,
    ReviewAction,
    RecommendedAction,
    DecisionStatus,
    EventType,
    canonical_json,
)
from api.irrigatrace.domain.ports import DecisionRepository, Clock
from api.irrigatrace.services.recorder import DecisionRecorder


class ReviewService:
    def __init__(
        self,
        decision_repo: DecisionRepository,
        recorder: DecisionRecorder,
        clock: Clock,
    ):
        self.decision_repo = decision_repo
        self.recorder = recorder
        self.clock = clock

    def mark_review_opened(self, decision_id: str, reviewer_id: str, reviewer_role: str) -> None:
        events = self.decision_repo.get_events(decision_id)
        if not any(e.event_type == EventType.REVIEW_OPENED for e in events):
            self.recorder.append_event(
                decision_id=decision_id,
                event_type=EventType.REVIEW_OPENED,
                actor_id=reviewer_id,
                actor_role=reviewer_role,
                payload={"reviewer_id": reviewer_id},
            )

    def submit_review(
        self,
        decision_id: str,
        reviewer_id: str,
        reviewer_role: str,
        action: ReviewAction,
        reason_code: Optional[str] = None,
        reason_text: Optional[str] = None,
        final_action: Optional[RecommendedAction] = None,
        final_duration_h: Optional[float] = None,
        occurred_at: Optional[str] = None,
    ) -> HumanReview:
        if reviewer_role == "AUDITOR":
            raise PermissionError("Auditors are read-only and cannot submit reviews")

        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        if decision.status == DecisionStatus.FINALIZED:
            raise ValueError("Decision is already finalized")

        # Validation per DDL CHECK
        if action != ReviewAction.APPROVE:
            if not reason_code or not reason_text or not reason_text.strip():
                raise ValueError("reason_code and non-empty reason_text are required when modifying or rejecting")

        # Determine final action and duration
        if action == ReviewAction.APPROVE:
            f_act = decision.recommended_action
            f_dur = decision.recommended_duration_h
        elif action == ReviewAction.MODIFY:
            if final_action is None:
                raise ValueError("final_action is required when modifying a decision")
            f_act = final_action
            f_dur = float(final_duration_h if final_duration_h is not None else decision.recommended_duration_h)
        elif action == ReviewAction.REJECT:
            f_act = RecommendedAction.WAIT
            f_dur = 0.0
        else:
            raise ValueError(f"Unknown review action: {action}")

        now = occurred_at or self.clock.now_iso()
        review_id = f"REV-{uuid.uuid4().hex[:8]}"

        review = HumanReview(
            id=review_id,
            decision_id=decision_id,
            reviewer_id=reviewer_id,
            action=action,
            final_action=f_act,
            final_duration_h=f_dur,
            created_at=now,
            reason_code=reason_code,
            reason_text=reason_text,
        )
        self.decision_repo.save_review(review)

        # Append REVIEW_* event
        if action == ReviewAction.APPROVE:
            ev_type = EventType.REVIEW_APPROVED
        elif action == ReviewAction.MODIFY:
            ev_type = EventType.REVIEW_MODIFIED
        else:
            ev_type = EventType.REVIEW_REJECTED

        self.recorder.append_event(
            decision_id=decision_id,
            event_type=ev_type,
            actor_id=reviewer_id,
            actor_role=reviewer_role,
            payload={
                "review_id": review_id,
                "action": action.value,
                "reason_code": reason_code,
                "reason_text": reason_text,
                "final_action": f_act.value,
                "final_duration_h": f_dur,
            },
            occurred_at=now,
        )

        # Append DECISION_FINALIZED event
        self.recorder.append_event(
            decision_id=decision_id,
            event_type=EventType.DECISION_FINALIZED,
            actor_id=reviewer_id,
            actor_role=reviewer_role,
            payload={
                "final_action": f_act.value,
                "final_duration_h": f_dur,
                "source": "HUMAN_APPROVED" if action == ReviewAction.APPROVE else "HUMAN_OVERRIDDEN",
            },
            occurred_at=now,
        )

        # Update decision status projection
        self.decision_repo.update_status(decision_id, DecisionStatus.FINALIZED)
        return review
