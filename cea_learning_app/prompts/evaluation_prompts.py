"""Prompt builder for response evaluation."""

from __future__ import annotations

from core.models import Scenario


def build_evaluation_prompt(scenario: Scenario, user_response: str) -> str:
    return f"""
You are an expert CEA evaluator. Assess the user response fairly and rigorously.

Return strict JSON with fields:
- overall_score (0-100)
- dimension_scores (object with keys: diagnosis_accuracy, biological_reasoning, practical_recommendation, tradeoff_awareness, communication_clarity)
- strengths (list)
- weaknesses (list)
- missed_concepts (list)
- incorrect_assumptions (list)
- recommended_next_focus (string)
- evaluator_notes (string)

Scenario:
Title: {scenario.title}
Role: {scenario.role}
Module: {scenario.module}
Difficulty: {scenario.difficulty}
Scenario text: {scenario.scenario_text}
Background context: {scenario.background_context}
Data points: {scenario.data_points}
Question: {scenario.question_to_user}
Ideal reasoning targets: {scenario.ideal_reasoning_targets}

User response:
{user_response}

Scoring guidance:
- Reward practical reasoning, explicit diagnostics, and tradeoff awareness.
- Penalize unsupported assumptions, overconfidence, and missed diagnostic uncertainty.
- Keep feedback concise and professional.
""".strip()
