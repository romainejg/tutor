"""OpenAI integration layer with robust mock fallback behavior."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from openai import OpenAI

from config import DEFAULT_MODEL, get_api_key


class OpenAIService:
    """Centralized API client wrapper and schema-safe JSON generation."""

    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or DEFAULT_MODEL
        self.api_key = get_api_key()
        self.mock_mode = not self.api_key
        self.client = OpenAI(api_key=self.api_key) if not self.mock_mode else None

    def set_model(self, model_name: str) -> None:
        self.model = model_name

    def generate_json(self, prompt: str, schema_name: Optional[str] = None) -> Dict[str, Any]:
        if self.mock_mode:
            return self._mock_response(schema_name)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
            )
            raw = completion.choices[0].message.content or "{}"
            payload = json.loads(raw)
            return self._validate_response(payload, schema_name)
        except Exception as exc:  # pragma: no cover - external API/network path
            fallback = self._fallback_response(schema_name)
            fallback["error"] = f"OpenAI request failed: {exc}"
            return fallback

    def _validate_response(self, payload: Dict[str, Any], schema_name: Optional[str]) -> Dict[str, Any]:
        expected = {
            "scenario": [
                "title",
                "role",
                "module",
                "primary_concepts",
                "difficulty",
                "scenario_text",
                "background_context",
                "data_points",
                "question_to_user",
                "ideal_reasoning_targets",
            ],
            "evaluation": [
                "overall_score",
                "dimension_scores",
                "strengths",
                "weaknesses",
                "missed_concepts",
                "incorrect_assumptions",
                "recommended_next_focus",
                "evaluator_notes",
            ],
            "tutor": [
                "teaching_summary",
                "key_concepts",
                "model_answer",
                "practical_rule_of_thumb",
                "next_study_prompt",
            ],
        }
        required_keys = expected.get(schema_name or "", [])
        if required_keys and not all(key in payload for key in required_keys):
            fallback = self._fallback_response(schema_name)
            fallback["error"] = "Malformed JSON response from model. Using fallback payload."
            return fallback
        return payload

    def _fallback_response(self, schema_name: Optional[str]) -> Dict[str, Any]:
        if schema_name == "scenario":
            return self._mock_scenario()
        if schema_name == "evaluation":
            return self._mock_evaluation()
        if schema_name == "tutor":
            return self._mock_tutor()
        return {"error": "Unknown schema"}

    def _mock_response(self, schema_name: Optional[str]) -> Dict[str, Any]:
        return self._fallback_response(schema_name)

    @staticmethod
    def _mock_scenario() -> Dict[str, Any]:
        return {
            "title": "Inner Leaf Tipburn During Late Expansion",
            "role": "Plant Scientist",
            "module": "Tipburn and calcium transport",
            "primary_concepts": ["calcium mobility", "VPD", "inner leaf development", "rapid growth"],
            "difficulty": "Intermediate",
            "scenario_text": (
                "In week 4 hydroponic butterhead lettuce, inner leaf margin necrosis appears in 9% of heads. "
                "Outer leaves stay visually healthy. Symptoms increased after a temperature strategy change."
            ),
            "background_context": (
                "Team raised night temperature for faster turns. Irrigation recipe and cultivar stayed constant. "
                "No visible pathogen pressure and roots remain white."
            ),
            "data_points": {
                "EC": "1.8 mS/cm",
                "pH": "5.8",
                "air_temperature": "shifted from 20°C to 24°C overnight",
                "overnight_humidity": "high (92-96%)",
                "airflow": "low in inner canopy",
            },
            "question_to_user": "What is your diagnosis and what immediate operational adjustments would you prioritize?",
            "ideal_reasoning_targets": [
                "Calcium transport is transpiration-driven and weak in enclosed inner leaves",
                "High overnight humidity lowers VPD and calcium movement",
                "Rapid growth can outpace calcium delivery",
                "Recommend VPD/airflow/night-temperature corrective plan and monitoring",
            ],
        }

    @staticmethod
    def _mock_evaluation() -> Dict[str, Any]:
        return {
            "overall_score": 76,
            "dimension_scores": {
                "diagnosis_accuracy": 78,
                "biological_reasoning": 80,
                "practical_recommendation": 72,
                "tradeoff_awareness": 70,
                "communication_clarity": 82,
            },
            "strengths": [
                "Correctly linked tipburn risk to calcium transport dynamics",
                "Suggested climate adjustment before changing nutrient recipe",
            ],
            "weaknesses": [
                "Did not quantify VPD targets",
                "Limited discussion of growth-rate tradeoff from warmer nights",
            ],
            "missed_concepts": ["inner leaf transpiration limitations", "airflow distribution"],
            "incorrect_assumptions": ["Assumed EC increase alone will resolve inner leaf calcium delivery"],
            "recommended_next_focus": "Practice diagnosing calcium transport under low VPD and high growth pressure.",
            "evaluator_notes": "Solid start; improve prioritization and uncertainty management.",
        }

    @staticmethod
    def _mock_tutor() -> Dict[str, Any]:
        return {
            "teaching_summary": (
                "Tipburn in inner leaves is usually a calcium transport problem, not total calcium supply. "
                "Low VPD and weak airflow reduce transpiration where demand is highest during rapid expansion."
            ),
            "key_concepts": ["calcium transport", "VPD", "airflow", "rapid growth dynamics"],
            "model_answer": (
                "I would prioritize restoring overnight VPD and canopy airflow first, while avoiding excessive night heat "
                "that accelerates growth beyond calcium delivery. Then track symptom progression and adjust fertigation only "
                "if tissue or sap data indicates true supply imbalance."
            ),
            "practical_rule_of_thumb": "When inner leaves burn first, tune climate-driven calcium transport before raising EC.",
            "next_study_prompt": "Compare two climate strategies and explain which one improves inner leaf calcium flow with fewer growth penalties.",
        }
