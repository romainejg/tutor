"""Prompt builder for scenario generation."""

from __future__ import annotations

from typing import List


def build_scenario_prompt(role: str, module: str, concept: str, difficulty: str, weak_concepts: List[str]) -> str:
    weak_list = ", ".join(weak_concepts) if weak_concepts else "None"
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
- historical weak concepts: {weak_list}

Difficulty rules:
- Beginner: Obvious but realistic signal, fewer variables.
- Intermediate: Multiple plausible causes, some missing info.
- Advanced: Conflicting variables, tradeoffs, uncertain baseline.

Requirements:
- Build a realistic leafy greens professional scenario.
- Keep it ambiguous enough to require reasoning.
- Include environmental, nutritional, crop, and operational signals where appropriate.
- Do not reveal final answer directly.
""".strip()
