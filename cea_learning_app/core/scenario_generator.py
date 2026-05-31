"""Scenario generation service."""

from __future__ import annotations

from typing import List

from core.models import Scenario
from core.openai_service import OpenAIService
from prompts.scenario_prompts import build_scenario_prompt


class ScenarioGenerator:
    """Builds role-specific CEA scenarios using OpenAIService."""

    def __init__(self, openai_service: OpenAIService) -> None:
        self.openai_service = openai_service

    def generate(
        self,
        role: str,
        module: str,
        concept: str,
        difficulty: str,
        historical_weak_concepts: List[str],
    ) -> Scenario:
        prompt = build_scenario_prompt(role, module, concept, difficulty, historical_weak_concepts)
        payload = self.openai_service.generate_json(prompt, schema_name="scenario")
        payload.setdefault("role", role)
        payload.setdefault("module", module)
        payload.setdefault("difficulty", difficulty)
        return Scenario.from_dict(payload)
