"""Prompt builder for scenario generation."""

from __future__ import annotations

import json
from typing import Any, Dict


def build_scenario_prompt(payload: Dict[str, Any]) -> str:
    role = payload.get("role", "Plant Scientist")
    module = payload.get("module", "Adaptive target")
    concept = payload.get("target_concept", "multifactor diagnostics")
    difficulty = payload.get("difficulty", "Intermediate")
    scenario_mode = payload.get("scenario_mode", "guided")
    weak_concepts = payload.get("historical_weak_concepts", [])
    recent_history = payload.get("recent_history", [])
    weak_list = ", ".join(weak_concepts) if weak_concepts else "None"
    recent_history_json = json.dumps(recent_history, ensure_ascii=False)

    return f"""
You are a CEA technical scenario designer for leafy greens teams.

Return strict JSON with fields:
- title
- role
- module
- primary_concepts (list)
- difficulty
- scenario_text
- background_context
- data_points (object)
- question_to_user
- ideal_reasoning_targets (list)

Inputs:
- role: {role}
- module: {module}
- target concept: {concept}
- difficulty: {difficulty}
- scenario mode: {scenario_mode}
- historical weak concepts: {weak_list}
- recent learner history: {recent_history_json}

Difficulty rules:
- Beginner:
  - Clear causal links with realistic production data.
  - Standard troubleshooting data available with minimal ambiguity.
  - Reinforce basic diagnostic structure.
- Intermediate:
  - Blend multivariable environmental and physiological signals.
  - Omit at least one meaningful diagnostic datapoint.
  - Require user to identify follow-up data requests.
- Advanced:
  - High-stakes production incident with conflicting telemetry.
  - Severe informational deficits and operational/economic tradeoffs.
  - No single obvious answer; reward systematic reasoning.

Requirements:
- Build a realistic leafy greens professional scenario with high operational fidelity.
- Blend multiple interacting factors, such as:
  - Root-zone aeration failure connected to VPD stress.
  - Sensor telemetry conflicts across EC, pH, moisture, or irrigation timing.
  - Crop quality decline tied to mechanical, environmental, and physiological variables.
  - Economic/operational tradeoffs where obvious fixes carry consequences.
- Include environmental, nutritional, crop, and operational signals where relevant.
- Include enough ambiguity to force diagnostic reasoning and validation steps.
- Do not reveal final answer directly.
""".strip()
