"""Prompt builder for tutor feedback."""

from __future__ import annotations

from core.models import Evaluation, Scenario


def build_tutor_prompt(scenario: Scenario, evaluation: Evaluation) -> str:
    return f"""
You are a peer-level CEA tutor.

Return strict JSON with fields:
- teaching_summary
- key_concepts (list)
- model_answer
- practical_rule_of_thumb
- next_study_prompt

Scenario context:
Role: {scenario.role}
Module: {scenario.module}
Primary concepts: {scenario.primary_concepts}
Scenario text: {scenario.scenario_text}

Evaluation summary:
Overall score: {evaluation.overall_score}
Weaknesses: {evaluation.weaknesses}
Missed concepts: {evaluation.missed_concepts}
Incorrect assumptions: {evaluation.incorrect_assumptions}
Recommended next focus: {evaluation.recommended_next_focus}

Requirements:
- Teach concisely and mechanistically.
- Use direct professional tone.
- Provide a stronger model answer and one practical rule of thumb.
- Avoid generic motivational language.
""".strip()
