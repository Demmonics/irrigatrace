"""
Multilingual advisory translation service using Gemini.
Translates English advisory into Hindi (hi) and Kannada (kn) with strict number verification.
"""
from __future__ import annotations

import json
import uuid
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from api.irrigatrace.domain.models import (
    DecisionExplanation,
    ExplanationKind,
    canonical_json,
)
from api.irrigatrace.domain.ports import DecisionRepository, Clock
from api.irrigatrace.services.narration import extract_numbers


class TranslationService:
    def __init__(self, decision_repo: DecisionRepository, clock: Clock, gemini_api_key: str = "", gemini_model: str = "gemini-2.5-flash"):
        self.decision_repo = decision_repo
        self.clock = clock
        self.api_key = gemini_api_key
        self.model = gemini_model

    def translate(self, decision_id: str, target_lang: str) -> DecisionExplanation:
        if target_lang not in ("hi", "kn"):
            raise ValueError("Supported languages: 'hi' (Hindi), 'kn' (Kannada)")

        explanations = self.decision_repo.get_explanations(decision_id)
        narrative_expl = next((e for e in explanations if e.kind == ExplanationKind.LLM_NARRATIVE), None)
        if not narrative_expl:
            narrative_expl = next((e for e in explanations if e.kind == ExplanationKind.DETERMINISTIC), None)
        if not narrative_expl:
            raise ValueError(f"No narrative found to translate for decision {decision_id}")

        content = json.loads(narrative_expl.content_json)
        english_text = content.get("narrative") or content.get("template_narrative") or ""
        english_numbers = extract_numbers(english_text)

        lang_name = "Hindi" if target_lang == "hi" else "Kannada"
        prompt = (
            f"You are a professional agricultural translator. Translate the following irrigation advisory into {lang_name} faithfully.\n"
            "Rules:\n"
            "1. Do not add or remove information.\n"
            "2. Keep all numbers, decimals, percentages, and units strictly unchanged.\n"
            "Return JSON: {\"translated_text\": \"...\"}\n\n"
            f"English advisory:\n{english_text}"
        )

        translated_text = ""
        provenance = {
            "source": "gemini",
            "model": self.model,
            "target_language": target_lang,
            "badge": "Machine-translated · not reviewed by a native speaker",
        }

        if self.api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    cand = data.get("candidates", [])[0]
                    res_text = cand.get("content", {}).get("parts", [])[0].get("text", "{}")
                    parsed = json.loads(res_text)
                    translated_text = parsed.get("translated_text", "")
            except Exception:
                pass

        if not translated_text:
            # Deterministic fallback message
            if target_lang == "hi":
                translated_text = f"[अनुवाद उपलब्ध नहीं] {english_text}"
            else:
                translated_text = f"[ಅನುವಾದ ಲಭ್ಯವಿಲ್ಲ] {english_text}"
            provenance["source"] = "fallback"

        # Verify numbers
        trans_numbers = extract_numbers(translated_text)
        # Check if numbers were preserved
        provenance["numbers_preserved"] = (english_numbers == trans_numbers or len(english_numbers - trans_numbers) == 0)

        now = self.clock.now_iso()
        expl_id = f"EXP-TR-{uuid.uuid4().hex[:6]}"
        explanation = DecisionExplanation(
            id=expl_id,
            decision_id=decision_id,
            kind=ExplanationKind.TRANSLATION,
            language=target_lang,
            content_json=canonical_json({"translated_text": translated_text, "original_text": english_text}),
            provenance_json=canonical_json(provenance),
            created_at=now,
        )
        self.decision_repo.save_explanation(explanation)
        return explanation
