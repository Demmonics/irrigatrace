"""
Server-Sent Events (SSE) broker for live decision timeline updates.
"""
from __future__ import annotations

import asyncio
import json
from typing import Dict, Set
from api.irrigatrace.domain.models import DecisionEvent


class EventBroadcaster:
    def __init__(self):
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}

    def subscribe(self, decision_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        if decision_id not in self._subscribers:
            self._subscribers[decision_id] = set()
        self._subscribers[decision_id].add(q)
        return q

    def unsubscribe(self, decision_id: str, q: asyncio.Queue) -> None:
        if decision_id in self._subscribers:
            self._subscribers[decision_id].discard(q)
            if not self._subscribers[decision_id]:
                del self._subscribers[decision_id]

    def publish(self, event: DecisionEvent) -> None:
        decision_id = event.decision_id
        if decision_id in self._subscribers:
            data = {
                "seq": event.seq,
                "event_type": event.event_type.value,
                "occurred_at": event.occurred_at,
                "actor_id": event.actor_id,
                "payload": json.loads(event.payload_json),
            }
            msg = f"event: {event.event_type.value}\ndata: {json.dumps(data)}\n\n"
            for q in list(self._subscribers[decision_id]):
                try:
                    q.put_nowait(msg)
                except Exception:
                    pass


broadcaster = EventBroadcaster()
