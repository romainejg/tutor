"""Adaptive logic for recommendation and concept mastery updates."""

from __future__ import annotations

from typing import Dict

from core.curriculum import CurriculumManager
from core.database import DatabaseManager
from core.models import Evaluation, Scenario


class AdaptiveEngine:
    """Simple MVP adaptive engine for concept mastery."""

    def __init__(self, database: DatabaseManager, curriculum: CurriculumManager) -> None:
        self.database = database
        self.curriculum = curriculum

    def process_evaluation(self, scenario: Scenario, evaluation: Evaluation) -> None:
        tracked_concepts = set(scenario.primary_concepts) | set(evaluation.missed_concepts)
        for concept in tracked_concepts:
            current = self.database.get_concept_mastery(limit=500, role_name=scenario.role)
            row = next(
                (
                    item
                    for item in current
                    if item["module_name"] == scenario.module and item["concept_name"] == concept
                ),
                {"mastery_score": 50.0},
            )
            mastery = float(row.get("mastery_score", 50.0))
            recent = self.database.get_recent_scores_for_concept(scenario.role, scenario.module, concept, limit=2)

            if evaluation.overall_score < 70 or concept in evaluation.missed_concepts:
                mastery -= 5
            elif len(recent) == 2 and all(score >= 85 for score in recent):
                mastery += 5
            elif evaluation.overall_score >= 85:
                mastery += 2

            self.database.update_concept_mastery(scenario.role, scenario.module, concept, mastery)

    def recommend_today_practice(self) -> Dict[str, str]:
        existing = self.database.get_today_recommendation()
        if existing:
            return {
                "role_name": existing["role_name"],
                "module_name": existing["module_name"],
                "concept_name": existing["concept_name"],
                "reason": existing["reason"],
            }

        weak = self.database.get_weak_concepts(limit=1)
        if weak:
            recommendation = {
                "role_name": weak[0]["role_name"],
                "module_name": weak[0]["module_name"],
                "concept_name": weak[0]["concept_name"],
                "reason": "Prioritized weak concept based on low mastery score.",
            }
        else:
            role = self.curriculum.get_roles()[0]
            module = self.curriculum.get_modules_by_role(role)[0]
            concept = self.curriculum.get_concepts_by_module(role, module)[0]
            recommendation = {
                "role_name": role,
                "module_name": module,
                "concept_name": concept,
                "reason": "Starting baseline practice progression.",
            }

        self.database.save_daily_recommendation(**recommendation)
        return recommendation
