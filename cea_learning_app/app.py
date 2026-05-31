"""Streamlit entry point for the CEA daily scenario learning app."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config import AVAILABLE_MODELS, get_default_model_label, get_model_id, is_mock_mode
from core.adaptive_engine import AdaptiveEngine
from core.curriculum import CurriculumManager
from core.database import DatabaseManager
from core.evaluator import ResponseEvaluator
from core.openai_service import OpenAIService
from core.scenario_generator import ScenarioGenerator
from core.session_manager import LearningSession
from core.tutor import Tutor

st.set_page_config(page_title="CEA Learning App", page_icon="🌱", layout="wide")


@st.cache_resource
def build_services() -> dict:
    curriculum = CurriculumManager()
    db = DatabaseManager()
    selected_label = st.session_state.get("selected_model_label", get_default_model_label())
    model = get_model_id(selected_label)
    openai_service = OpenAIService(model=model)
    scenario_generator = ScenarioGenerator(openai_service)
    evaluator = ResponseEvaluator(openai_service)
    tutor = Tutor(openai_service)
    adaptive_engine = AdaptiveEngine(db, curriculum)
    session = LearningSession(db, scenario_generator, evaluator, tutor, adaptive_engine)
    return {
        "curriculum": curriculum,
        "db": db,
        "openai_service": openai_service,
        "adaptive_engine": adaptive_engine,
        "session": session,
    }


services = build_services()
curriculum: CurriculumManager = services["curriculum"]
db: DatabaseManager = services["db"]
openai_service: OpenAIService = services["openai_service"]
adaptive_engine: AdaptiveEngine = services["adaptive_engine"]
learning_session: LearningSession = services["session"]

st.sidebar.title("CEA Learning")
page = st.sidebar.radio("Navigate", ["Dashboard", "Practice", "Review History", "Curriculum", "Settings"])


if page == "Dashboard":
    st.title("Dashboard")
    recommendation = adaptive_engine.recommend_today_practice()
    st.subheader("Today's Recommended Practice")
    st.info(
        f"{recommendation['role_name']} → {recommendation['module_name']} → {recommendation['concept_name']}\n\n"
        f"Reason: {recommendation['reason']}"
    )

    st.subheader("Average Score by Role")
    score_rows = db.get_average_score_by_role()
    if score_rows:
        st.dataframe(pd.DataFrame(score_rows), use_container_width=True)
    else:
        st.write("No attempts yet.")

    st.subheader("Top 3 Weakest Concepts")
    weak_rows = db.get_weak_concepts(limit=3)
    if weak_rows:
        st.dataframe(pd.DataFrame(weak_rows), use_container_width=True)

    st.subheader("Recent Attempts")
    attempts = db.get_recent_attempts(limit=8)
    if attempts:
        st.dataframe(pd.DataFrame(attempts), use_container_width=True)

    st.metric("Total Practice Count", db.get_total_practice_count())
    # TODO: add persistent streak counter logic.

elif page == "Practice":
    st.title("Practice")
    roles = curriculum.get_roles() + ["Cross-Functional / Dynamic"]
    selected_role = st.selectbox("Role", roles)
    selected_difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])

    def _build_scenario_payload(use_adaptive_target: bool) -> dict:
        preferred_role = selected_role if selected_role in curriculum.get_roles() else None
        recent_history = db.get_recent_performance(limit=6)
        scenario_mode = "next_practice" if use_adaptive_target else "guided"

        if selected_role == "Cross-Functional / Dynamic":
            scenario_mode = "surprise_me"

        if use_adaptive_target or selected_role == "Cross-Functional / Dynamic":
            target = adaptive_engine.recommend_next_practice_target(preferred_role=preferred_role)
        else:
            role_weak = db.get_concept_mastery(limit=1, role_name=preferred_role) if preferred_role else []
            concept_hint = role_weak[0]["concept_name"] if role_weak else None
            target = {
                **adaptive_engine.resolve_curriculum_target(preferred_role, concept_hint),
                "recent_history": recent_history,
            }

        target_role = target.get("role_name", preferred_role or curriculum.get_roles()[0])
        weak_for_role = [c["concept_name"] for c in db.get_concept_mastery(limit=5, role_name=target_role)]

        return {
            "role": target_role,
            "module": target.get("module_name", "Adaptive target"),
            "difficulty": selected_difficulty,
            "target_concept": target.get("concept_name"),
            "historical_weak_concepts": weak_for_role,
            "recent_history": target.get("recent_history", recent_history),
            "scenario_mode": scenario_mode,
        }

    col_generate, col_next = st.columns(2)
    generate_clicked = col_generate.button("Generate Scenario", type="primary")
    next_clicked = col_next.button("Generate Next Practice Scenario")

    if generate_clicked or next_clicked:
        with st.spinner("Generating scenario..."):
            scenario_payload = _build_scenario_payload(use_adaptive_target=next_clicked)
            scenario = learning_session.generate_scenario(scenario_payload)
            st.success(f"Scenario generated: {scenario.title}")

    scenario = st.session_state.get("current_scenario")
    if scenario:
        st.subheader(scenario.title)
        st.markdown(f"**Scenario**: {scenario.scenario_text}")
        st.markdown(f"**Background**: {scenario.background_context}")
        st.markdown("**Data Points**")
        st.json(scenario.data_points)
        st.markdown(f"**Question**: {scenario.question_to_user}")

        response_text = st.text_area("Your Response", key="practice_response", height=220)
        if st.button("Submit Answer"):
            if not response_text.strip():
                st.warning("Please enter a response before submitting.")
            else:
                with st.spinner("Evaluating response and generating tutor feedback..."):
                    evaluation, tutor_feedback = learning_session.submit_response(response_text)
                if evaluation and tutor_feedback:
                    st.success("Evaluation complete.")

    evaluation = st.session_state.get("latest_evaluation")
    tutor_feedback = st.session_state.get("latest_tutor_feedback")
    if evaluation:
        st.subheader("Evaluation")
        st.metric("Overall Score", evaluation.overall_score)
        st.write("**Rubric Breakdown**")
        st.write(
            {
                "diagnosis_accuracy": evaluation.diagnosis_accuracy,
                "biological_reasoning": evaluation.biological_reasoning,
                "practical_recommendation": evaluation.practical_recommendation,
                "tradeoff_awareness": evaluation.tradeoff_awareness,
                "communication_clarity": evaluation.communication_clarity,
            }
        )
        st.write("**Strengths**", evaluation.strengths)
        st.write("**Weaknesses**", evaluation.weaknesses)
        st.write("**Missed Concepts**", evaluation.missed_concepts)
        st.write("**Incorrect Assumptions**", evaluation.incorrect_assumptions)
        st.write("**Recommended Next Focus**", evaluation.recommended_next_focus)
        st.write("**Evaluator Notes**", evaluation.evaluator_notes)

    if tutor_feedback:
        st.subheader("Tutor Feedback")
        st.write("**Teaching Summary**", tutor_feedback.teaching_summary)
        st.write("**Model Answer**", tutor_feedback.model_answer)
        st.write("**Practical Rule of Thumb**", tutor_feedback.practical_rule_of_thumb)
        st.write("**Next Study Prompt**", tutor_feedback.next_study_prompt)

elif page == "Review History":
    st.title("Review History")
    role_filter = st.selectbox("Filter by role", ["All"] + curriculum.get_roles())
    rows = db.get_recent_attempts(limit=100, role_filter=None if role_filter == "All" else role_filter)
    if not rows:
        st.write("No history yet.")
    else:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        response_id = st.selectbox("Select attempt", [int(r["response_id"]) for r in rows])
        details = db.get_attempt_details(response_id)
        if details:
            st.subheader("Attempt Details")
            st.write("**Scenario**", details.get("scenario_text"))
            st.write("**Background**", details.get("background_context"))
            st.write("**Data Points**", details.get("data_points_json", {}))
            st.write("**User Response**", details.get("user_response", ""))
            st.write("**Scores**", {
                "overall": details.get("overall_score"),
                "diagnosis_accuracy": details.get("diagnosis_accuracy"),
                "biological_reasoning": details.get("biological_reasoning"),
                "practical_recommendation": details.get("practical_recommendation"),
                "tradeoff_awareness": details.get("tradeoff_awareness"),
                "communication_clarity": details.get("communication_clarity"),
            })
            st.write("**Strengths**", details.get("strengths_json", []))
            st.write("**Weaknesses**", details.get("weaknesses_json", []))
            st.write("**Missed Concepts**", details.get("missed_concepts_json", []))
            st.write("**Incorrect Assumptions**", details.get("incorrect_assumptions_json", []))
            st.write("**Evaluator Notes**", details.get("evaluator_notes", ""))
            st.write("**Teaching Summary**", details.get("teaching_summary", ""))
            st.write("**Model Answer**", details.get("model_answer", ""))
            st.write("**Rule of Thumb**", details.get("practical_rule_of_thumb", ""))
            st.write("**Next Study Prompt**", details.get("next_study_prompt", ""))

elif page == "Curriculum":
    st.title("Curriculum")
    all_curriculum = curriculum.get_all_curriculum()
    mastery_rows = db.get_concept_mastery(limit=1000)
    mastery_map = {(r["role_name"], r["module_name"], r["concept_name"]): float(r["mastery_score"]) for r in mastery_rows}

    for role, role_data in all_curriculum.items():
        st.header(role)
        st.caption(role_data.get("description", ""))
        modules = role_data.get("modules", {})
        for module_name, concepts in modules.items():
            st.subheader(module_name)
            for concept in concepts:
                score = mastery_map.get((role, module_name, concept), 50.0)
                st.write(f"{concept} ({score:.1f}/100)")
                st.progress(min(max(score / 100, 0.0), 1.0))

elif page == "Settings":
    st.title("Settings")
    st.subheader("API Status")
    if is_mock_mode():
        st.warning("Running in local mock fallback mode.")
    else:
        st.success("Running with OpenAI API streaming enabled.")

    default_label = st.session_state.get("selected_model_label", get_default_model_label())
    if default_label not in AVAILABLE_MODELS:
        default_label = get_default_model_label()
    selected_model_label = st.selectbox(
        "Model",
        options=list(AVAILABLE_MODELS.keys()),
        index=list(AVAILABLE_MODELS.keys()).index(default_label),
    )
    if st.button("Apply Model"):
        st.session_state.selected_model_label = selected_model_label
        selected_model_id = get_model_id(selected_model_label)
        openai_service.set_model(selected_model_id)
        st.success(f"Model updated to {selected_model_label} ({selected_model_id})")

    st.subheader("Reset Database")
    confirm = st.checkbox("I understand this will permanently delete local learning history.")
    if st.button("Reset Local Database", disabled=not confirm):
        if db.reset_database(confirmed=confirm):
            st.cache_resource.clear()
            st.success("Database reset complete.")
            st.rerun()
        else:
            st.error("Reset cancelled.")
