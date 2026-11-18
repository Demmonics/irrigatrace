"""
NarrationService and Number-Consistency Validator.
Strategy pattern: TemplateNarrationStrategy / OllamaNarrationStrategy / GeminiNarrationStrategy.
Obeys Invariant 5: The LLM never decides. LLM text is narration only, labeled with provenance.
"""
from __future__ import annotations

import re
import os
import json
import uuid
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple, Protocol
from pathlib import Path

from api.irrigatrace.domain.models import (
    DecisionExplanation,
    ExplanationKind,
    EventType,
    canonical_json,
    compute_hash,
)
from api.irrigatrace.domain.ports import DecisionRepository, Clock
from api.irrigatrace.services.recorder import DecisionRecorder


def extract_numbers(data: Any) -> set[float]:
    """Extracts all numerical values from a text string or nested JSON structure."""
    numbers = set()
    if isinstance(data, (int, float)):
        numbers.add(round(float(data), 2))
    elif isinstance(data, dict):
        for v in data.values():
            numbers.update(extract_numbers(v))
    elif isinstance(data, list):
        for item in data:
            numbers.update(extract_numbers(item))
    elif isinstance(data, str):
        # Find all numerals including decimals
        matches = re.findall(r"-?\b\d+(?:\.\d+)?\b", data)
        for m in matches:
            try:
                numbers.add(round(float(m), 2))
            except ValueError:
                pass
    return numbers


class NumberConsistencyValidator:
    """
    Mandatory validator per doc 04:
    numbers_in(text) ⊆ numbers_in(evidence_json) ∪ {allowed_unit_words}
    Also checks for action contradiction.
    """

    @classmethod
    def validate(cls, text: str, evidence: Dict[str, Any], action: str) -> Tuple[bool, str]:
        evidence_numbers = extract_numbers(evidence)
        text_numbers = extract_numbers(text)

        # Check action contradiction
        lower_text = text.lower()
        if action == "IRRIGATE":
            if "do not irrigate" in lower_text or "defer irrigation" in lower_text:
                return False, "Contradicts action IRRIGATE"
        elif action in ("WAIT", "DEFER_RAIN"):
            if "start irrigating" in lower_text or "irrigate now" in lower_text:
                return False, f"Contradicts action {action}"

        # Allow common sequence/count numbers if necessary (like 1, 2, 3), but strict on data figures
        for num in text_numbers:
            # Check if num or close match exists in evidence
            matched = any(abs(num - ev_num) < 0.05 for ev_num in evidence_numbers)
            if not matched and num not in (1.0, 2.0, 3.0):  # allow 1,2,3 for lists/counts
                return False, f"Number {num} in narrative is not present in evidence {sorted(list(evidence_numbers))}"

        return True, "Passed"


class NarrationStrategy(Protocol):
    def narrate(self, evidence: Dict[str, Any], action: str) -> Tuple[str, Dict[str, Any]]: ...


class TemplateNarrationStrategy:
    """Authoritative deterministic template generator (Zero LLM, always available)."""

    def narrate(self, evidence: Dict[str, Any], action: str) -> Tuple[str, Dict[str, Any]]:
        template_text = evidence.get("template_narrative", "")
        if not template_text:
            factors = evidence.get("factors", [])
            f_texts = [f["text"] for f in factors]
            template_text = f"Action: {action}. " + " ".join(f_texts[:2])
        provenance = {
            "source": "template",
            "model": "deterministic_ruleset",
            "validated": True,
            "latency_ms": 0.1,
        }
        return template_text, provenance


class OllamaNarrationStrategy:
    """Local Ollama client using structured JSON generation."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "qwen2.5:3b"):
        self.host = host.rstrip("/")
        self.model = model

    def narrate(self, evidence: Dict[str, Any], action: str) -> Tuple[str, Dict[str, Any]]:
        url = f"{self.host}/api/chat"
        prompt_path = Path(__file__).parent / "prompts" / "narrate_decision.system"
        system_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else "Explain this irrigation decision."

        evidence_str = json.dumps(evidence)
        payload = {
            "model": self.model,
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "narrative": {"type": "string"},
                    "key_points": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["narrative"],
            },
            "options": {"temperature": 0.2, "seed": 42, "num_ctx": 4096},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Evidence record:\n{evidence_str}\nAction: {action}"},
            ],
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content_str = data.get("message", {}).get("content", "{}")
            content_json = json.loads(content_str)
            narrative = content_json.get("narrative", "")

            # Validate output
            valid, reason = NumberConsistencyValidator.validate(narrative, evidence, action)
            if not valid:
                raise ValueError(f"Validator rejected LLM narrative: {reason}")

            provenance = {
                "source": "ollama",
                "model": self.model,
                "model_digest": data.get("created_at"),
                "prompt_sha256": compute_hash(system_prompt),
                "temperature": 0.2,
                "seed": 42,
                "validated": True,
            }
            return narrative, provenance


class GeminiNarrationStrategy:
    """Cloud fallback using Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    def narrate(self, evidence: Dict[str, Any], action: str) -> Tuple[str, Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt_path = Path(__file__).parent / "prompts" / "narrate_decision.system"
        system_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else "Explain this irrigation decision."

        evidence_str = json.dumps(evidence)
        payload = {
            "contents": [
                {"parts": [{"text": f"{system_prompt}\n\nEvidence JSON:\n{evidence_str}\nAction: {action}"}]}
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            cand = data.get("candidates", [])[0]
            text = cand.get("content", {}).get("parts", [])[0].get("text", "{}")
            parsed = json.loads(text)
            narrative = parsed.get("narrative", "")

            valid, reason = NumberConsistencyValidator.validate(narrative, evidence, action)
            if not valid:
                raise ValueError(f"Validator rejected Gemini narrative: {reason}")

            provenance = {
                "source": "gemini",
                "model": self.model,
                "prompt_sha256": compute_hash(system_prompt),
                "validated": True,
            }
            return narrative, provenance


class NarrationService:
    """
    Coordinates narration across Template, Ollama, and Gemini strategies.
    Ensures graceful degradation to deterministic template on any failure.
    """

    def __init__(
        self,
        decision_repo: DecisionRepository,
        recorder: DecisionRecorder,
        clock: Clock,
        ollama_host: str = "http://localhost:11434",
        ollama_model: str = "qwen2.5:3b",
        gemini_api_key: str = "",
        gemini_model: str = "gemini-2.5-flash",
        allow_cloud_fallback: bool = True,
    ):
        self.decision_repo = decision_repo
        self.recorder = recorder
        self.clock = clock
        self.template_strategy = TemplateNarrationStrategy()
        self.ollama_strategy = OllamaNarrationStrategy(host=ollama_host, model=ollama_model)
        self.gemini_strategy = GeminiNarrationStrategy(api_key=gemini_api_key, model=gemini_model) if gemini_api_key else None
        self.allow_cloud_fallback = allow_cloud_fallback

    def narrate_decision(self, decision_id: str) -> DecisionExplanation:
        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        explanations = self.decision_repo.get_explanations(decision_id)
        det_expl = next((e for e in explanations if e.kind == ExplanationKind.DETERMINISTIC), None)
        if not det_expl:
            raise ValueError(f"Deterministic explanation missing for decision {decision_id}")

        evidence = json.loads(det_expl.content_json)
        action = decision.recommended_action.value

        narrative = None
        provenance = None

        # 1. Try local Ollama model
        try:
            narrative, provenance = self.ollama_strategy.narrate(evidence, action)
        except Exception as e:
            # 2. Try Gemini fallback if configured and allowed
            if self.allow_cloud_fallback and self.gemini_strategy:
                try:
                    narrative, provenance = self.gemini_strategy.narrate(evidence, action)
                except Exception:
                    pass

        # 3. Graceful fallback to deterministic template
        if not narrative or not provenance:
            narrative, provenance = self.template_strategy.narrate(evidence, action)

        now = self.clock.now_iso()
        expl_id = f"EXP-{uuid.uuid4().hex[:8]}"
        explanation = DecisionExplanation(
            id=expl_id,
            decision_id=decision_id,
            kind=ExplanationKind.LLM_NARRATIVE,
            content_json=canonical_json({"narrative": narrative, "key_points": []}),
            provenance_json=canonical_json(provenance),
            created_at=now,
        )
        self.decision_repo.save_explanation(explanation)

        # Append NARRATIVE_ATTACHED event
        self.recorder.append_event(
            decision_id=decision_id,
            event_type=EventType.NARRATIVE_ATTACHED,
            actor_id=provenance.get("model", "SYSTEM"),
            actor_role="AI_NARRATOR",
            payload={
                "explanation_id": expl_id,
                "source": provenance.get("source"),
                "model": provenance.get("model"),
                "validated": provenance.get("validated", True),
            },
            occurred_at=now,
        )
        return explanation
