"""Learning session coordinator for Streamlit flows."""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st

from core.adaptive_engine import AdaptiveEngine
from core.database import DatabaseManager
from core.evaluator import ResponseEvaluator
from core.models import Evaluation, Scenario, TutorFeedback
from core.scenario_generator import ScenarioGenerator
from core.tutor import Tutor


class LearningSession:
    """Coordinates full scenario -> evaluate -> tutor -> adapt workflow."""

    SESSION_KEYS = {
        "current_scenario": None,
        "current_scenario_id": None,
        "latest_evaluation": None,
        "latest_tutor_feedback": None,
        "user_response": "",
    }

    def __init__(
        self,
        db: DatabaseManager,
        scenario_generator: ScenarioGenerator,
        evaluator: ResponseEvaluator,
        tutor: Tutor,
        adaptive_engine: AdaptiveEngine,
    ) -> None:
        self.db = db
        self.scenario_generator = scenario_generator
        self.evaluator = evaluator
        self.tutor = tutor
        self.adaptive_engine = adaptive_engine
        self._ensure_session_state()

    def _ensure_session_state(self) -> None:
        for key, default in self.SESSION_KEYS.items():
            if key not in st.session_state:
                st.session_state[key] = default

    def generate_scenario(
        self,
        payload: dict[str, Any],
    ) -> Scenario:
        scenario = self.scenario_generator.generate(payload)
        scenario_id = self.db.save_scenario(scenario)
        st.session_state.current_scenario = scenario
        st.session_state.current_scenario_id = scenario_id
        st.session_state.latest_evaluation = None
        st.session_state.latest_tutor_feedback = None
        return scenario

    def submit_response(self, user_response: str) -> tuple[Optional[Evaluation], Optional[TutorFeedback]]:
        scenario = st.session_state.current_scenario
        scenario_id = st.session_state.current_scenario_id
        if not scenario or not scenario_id:
            return None, None

        response_id = self.db.save_response(scenario_id, user_response)
        evaluation = self.evaluator.evaluate(scenario, user_response)
        self.db.save_evaluation(response_id, evaluation)
        tutor_feedback = self.tutor.teach(scenario, evaluation)
        self.db.save_tutor_feedback(response_id, tutor_feedback)
        self.adaptive_engine.process_evaluation(scenario, evaluation)

        st.session_state.user_response = user_response
        st.session_state.latest_evaluation = evaluation
        st.session_state.latest_tutor_feedback = tutor_feedback
        return evaluation, tutor_feedback
