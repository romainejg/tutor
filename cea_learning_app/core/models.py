"""Dataclasses used throughout the CEA learning app."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class Scenario:
    title: str
    role: str
    module: str
    primary_concepts: List[str]
    difficulty: str
    scenario_text: str
    background_context: str
    data_points: Dict[str, Any]
    question_to_user: str
    ideal_reasoning_targets: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Scenario":
        return cls(**payload)


@dataclass
class Evaluation:
    overall_score: int
    diagnosis_accuracy: int
    biological_reasoning: int
    practical_recommendation: int
    tradeoff_awareness: int
    communication_clarity: int
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    missed_concepts: List[str] = field(default_factory=list)
    incorrect_assumptions: List[str] = field(default_factory=list)
    recommended_next_focus: str = ""
    evaluator_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Evaluation":
        dimension_scores = payload.get("dimension_scores", {})
        merged = {
            "overall_score": int(payload.get("overall_score", 0)),
            "diagnosis_accuracy": int(payload.get("diagnosis_accuracy", dimension_scores.get("diagnosis_accuracy", 0))),
            "biological_reasoning": int(payload.get("biological_reasoning", dimension_scores.get("biological_reasoning", 0))),
            "practical_recommendation": int(
                payload.get("practical_recommendation", dimension_scores.get("practical_recommendation", 0))
            ),
            "tradeoff_awareness": int(payload.get("tradeoff_awareness", dimension_scores.get("tradeoff_awareness", 0))),
            "communication_clarity": int(
                payload.get("communication_clarity", dimension_scores.get("communication_clarity", 0))
            ),
            "strengths": payload.get("strengths", []),
            "weaknesses": payload.get("weaknesses", []),
            "missed_concepts": payload.get("missed_concepts", []),
            "incorrect_assumptions": payload.get("incorrect_assumptions", []),
            "recommended_next_focus": payload.get("recommended_next_focus", ""),
            "evaluator_notes": payload.get("evaluator_notes", ""),
        }
        return cls(**merged)


@dataclass
class TutorFeedback:
    teaching_summary: str
    key_concepts: List[str]
    model_answer: str
    practical_rule_of_thumb: str
    next_study_prompt: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TutorFeedback":
        return cls(**payload)


@dataclass
class ConceptMastery:
    role_name: str
    module_name: str
    concept_name: str
    mastery_score: float
    attempts: int
    last_seen: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ConceptMastery":
        return cls(**payload)
