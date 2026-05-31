"""Scenario generation service."""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.models import Scenario
from core.openai_service import OpenAIService
from prompts.scenario_prompts import build_scenario_prompt


class ScenarioGenerator:
    """Builds role-specific CEA scenarios using OpenAIService."""

    def __init__(self, openai_service: OpenAIService) -> None:
        self.openai_service = openai_service

    def generate(self, payload: Optional[Dict[str, Any]] = None) -> Scenario:
        request_payload = dict(payload or {})
        role = request_payload.get("role", "Plant Scientist")
        module = request_payload.get("module", "Adaptive target")
        concept = request_payload.get("target_concept", "multifactor diagnostics")
        difficulty = request_payload.get("difficulty", "Intermediate")

        request_payload.setdefault("role", role)
        request_payload.setdefault("module", module)
        request_payload.setdefault("target_concept", concept)
        request_payload.setdefault("difficulty", difficulty)
        request_payload.setdefault("historical_weak_concepts", [])
        request_payload.setdefault("recent_history", [])
        request_payload.setdefault("scenario_mode", "guided")

        prompt = build_scenario_prompt(request_payload)
        payload = self.openai_service.generate_json(prompt, schema_name="scenario")
        payload.setdefault("role", role)
        payload.setdefault("module", module)
        payload.setdefault("difficulty", difficulty)
        payload.setdefault("primary_concepts", [concept] if concept else [])
        payload.setdefault("data_points", {})
        payload.setdefault("ideal_reasoning_targets", [])
        return Scenario.from_dict(payload)
