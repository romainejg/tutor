"""SQLite persistence layer for the CEA learning app."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import DATABASE_PATH
from core.curriculum import CurriculumManager
from core.models import Evaluation, Scenario, TutorFeedback


class DatabaseManager:
    """Handles schema creation, seeding, and data persistence."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = Path(db_path or DATABASE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
        self._seed_curriculum_if_needed()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT
                );
                CREATE TABLE IF NOT EXISTS modules (
                    id INTEGER PRIMARY KEY,
                    role_name TEXT,
                    module_name TEXT,
                    description TEXT
                );
                CREATE TABLE IF NOT EXISTS concept_mastery (
                    id INTEGER PRIMARY KEY,
                    role_name TEXT,
                    module_name TEXT,
                    concept_name TEXT,
                    mastery_score REAL,
                    attempts INTEGER,
                    last_seen TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS scenarios (
                    id INTEGER PRIMARY KEY,
                    role_name TEXT,
                    module_name TEXT,
                    difficulty TEXT,
                    title TEXT,
                    scenario_text TEXT,
                    background_context TEXT,
                    data_points_json TEXT,
                    primary_concepts_json TEXT,
                    ideal_reasoning_targets_json TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY,
                    scenario_id INTEGER,
                    user_response TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY,
                    response_id INTEGER,
                    overall_score INTEGER,
                    diagnosis_accuracy INTEGER,
                    biological_reasoning INTEGER,
                    practical_recommendation INTEGER,
                    tradeoff_awareness INTEGER,
                    communication_clarity INTEGER,
                    strengths_json TEXT,
                    weaknesses_json TEXT,
                    missed_concepts_json TEXT,
                    incorrect_assumptions_json TEXT,
                    recommended_next_focus TEXT,
                    evaluator_notes TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS tutor_feedback (
                    id INTEGER PRIMARY KEY,
                    response_id INTEGER,
                    teaching_summary TEXT,
                    key_concepts_json TEXT,
                    model_answer TEXT,
                    practical_rule_of_thumb TEXT,
                    next_study_prompt TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS daily_recommendations (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    role_name TEXT,
                    module_name TEXT,
                    concept_name TEXT,
                    reason TEXT,
                    created_at TEXT
                );
                """
            )

    def _seed_curriculum_if_needed(self) -> None:
        curriculum = CurriculumManager().get_all_curriculum()
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            role_count = conn.execute("SELECT COUNT(*) AS count FROM roles").fetchone()["count"]
            module_count = conn.execute("SELECT COUNT(*) AS count FROM modules").fetchone()["count"]
            if role_count == 0:
                conn.executemany(
                    "INSERT INTO roles (name, description) VALUES (?, ?)",
                    [(role, data.get("description", "")) for role, data in curriculum.items()],
                )
            if module_count == 0:
                module_rows: List[tuple[str, str, str]] = []
                mastery_rows: List[tuple[str, str, str, float, int, str, str, str]] = []
                for role, data in curriculum.items():
                    modules: Dict[str, List[str]] = data.get("modules", {})  # type: ignore[assignment]
                    for module_name, concepts in modules.items():
                        module_rows.append((role, module_name, f"Core training module for {role}."))
                        for concept in concepts:
                            mastery_rows.append((role, module_name, concept, 50.0, 0, "", now, now))
                conn.executemany(
                    "INSERT INTO modules (role_name, module_name, description) VALUES (?, ?, ?)",
                    module_rows,
                )
                conn.executemany(
                    """
                    INSERT INTO concept_mastery
                    (role_name, module_name, concept_name, mastery_score, attempts, last_seen, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    mastery_rows,
                )

    def save_scenario(self, scenario: Scenario) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO scenarios
                (role_name, module_name, difficulty, title, scenario_text, background_context,
                 data_points_json, primary_concepts_json, ideal_reasoning_targets_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scenario.role,
                    scenario.module,
                    scenario.difficulty,
                    scenario.title,
                    scenario.scenario_text,
                    scenario.background_context,
                    json.dumps(scenario.data_points),
                    json.dumps(scenario.primary_concepts),
                    json.dumps(scenario.ideal_reasoning_targets),
                    datetime.utcnow().isoformat(),
                ),
            )
            return int(cur.lastrowid)

    def save_response(self, scenario_id: int, user_response: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO responses (scenario_id, user_response, created_at) VALUES (?, ?, ?)",
                (scenario_id, user_response, datetime.utcnow().isoformat()),
            )
            return int(cur.lastrowid)

    def save_evaluation(self, response_id: int, evaluation: Evaluation) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO evaluations
                (response_id, overall_score, diagnosis_accuracy, biological_reasoning, practical_recommendation,
                 tradeoff_awareness, communication_clarity, strengths_json, weaknesses_json, missed_concepts_json,
                 incorrect_assumptions_json, recommended_next_focus, evaluator_notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    response_id,
                    evaluation.overall_score,
                    evaluation.diagnosis_accuracy,
                    evaluation.biological_reasoning,
                    evaluation.practical_recommendation,
                    evaluation.tradeoff_awareness,
                    evaluation.communication_clarity,
                    json.dumps(evaluation.strengths),
                    json.dumps(evaluation.weaknesses),
                    json.dumps(evaluation.missed_concepts),
                    json.dumps(evaluation.incorrect_assumptions),
                    evaluation.recommended_next_focus,
                    evaluation.evaluator_notes,
                    datetime.utcnow().isoformat(),
                ),
            )
            return int(cur.lastrowid)

    def save_tutor_feedback(self, response_id: int, tutor_feedback: TutorFeedback) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO tutor_feedback
                (response_id, teaching_summary, key_concepts_json, model_answer,
                 practical_rule_of_thumb, next_study_prompt, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    response_id,
                    tutor_feedback.teaching_summary,
                    json.dumps(tutor_feedback.key_concepts),
                    tutor_feedback.model_answer,
                    tutor_feedback.practical_rule_of_thumb,
                    tutor_feedback.next_study_prompt,
                    datetime.utcnow().isoformat(),
                ),
            )
            return int(cur.lastrowid)

    def get_recent_scores_for_concept(self, role_name: str, module_name: str, concept_name: str, limit: int = 5) -> List[int]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT e.overall_score
                FROM evaluations e
                JOIN responses r ON r.id = e.response_id
                JOIN scenarios s ON s.id = r.scenario_id
                WHERE s.role_name = ? AND s.module_name = ? AND s.primary_concepts_json LIKE ?
                ORDER BY e.id DESC
                LIMIT ?
                """,
                (role_name, module_name, f'%"{concept_name}"%', limit),
            ).fetchall()
            return [int(r["overall_score"]) for r in rows]

    def update_concept_mastery(self, role_name: str, module_name: str, concept_name: str, score: float) -> None:
        now = datetime.utcnow().isoformat()
        bounded = max(0.0, min(100.0, score))
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, attempts FROM concept_mastery
                WHERE role_name = ? AND module_name = ? AND concept_name = ?
                """,
                (role_name, module_name, concept_name),
            ).fetchone()
            if row:
                conn.execute(
                    """
                    UPDATE concept_mastery
                    SET mastery_score = ?, attempts = ?, last_seen = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (bounded, int(row["attempts"]) + 1, now, now, row["id"]),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO concept_mastery
                    (role_name, module_name, concept_name, mastery_score, attempts, last_seen, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (role_name, module_name, concept_name, bounded, 1, now, now, now),
                )

    def get_concept_mastery(self, limit: int = 10, role_name: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM concept_mastery"
        params: List[Any] = []
        if role_name:
            query += " WHERE role_name = ?"
            params.append(role_name)
        query += " ORDER BY mastery_score ASC, attempts DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_weak_concepts(self, limit: int = 3) -> List[Dict[str, Any]]:
        return self.get_concept_mastery(limit=limit)

    def get_today_recommendation(self) -> Optional[Dict[str, Any]]:
        today = date.today().isoformat()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM daily_recommendations WHERE date = ? ORDER BY id DESC LIMIT 1", (today,)
            ).fetchone()
            return dict(row) if row else None

    def save_daily_recommendation(self, role_name: str, module_name: str, concept_name: str, reason: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO daily_recommendations (date, role_name, module_name, concept_name, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (date.today().isoformat(), role_name, module_name, concept_name, reason, datetime.utcnow().isoformat()),
            )

    def get_recent_attempts(self, limit: int = 20, role_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT r.id AS response_id, s.id AS scenario_id, s.role_name, s.module_name, s.title,
                   e.overall_score, r.created_at
            FROM responses r
            JOIN scenarios s ON s.id = r.scenario_id
            LEFT JOIN evaluations e ON e.response_id = r.id
        """
        params: List[Any] = []
        if role_filter:
            query += " WHERE s.role_name = ?"
            params.append(role_filter)
        query += " ORDER BY r.id DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_attempt_details(self, response_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT s.*, r.user_response, r.id AS response_id,
                       e.*, t.teaching_summary, t.key_concepts_json, t.model_answer,
                       t.practical_rule_of_thumb, t.next_study_prompt
                FROM responses r
                JOIN scenarios s ON s.id = r.scenario_id
                LEFT JOIN evaluations e ON e.response_id = r.id
                LEFT JOIN tutor_feedback t ON t.response_id = r.id
                WHERE r.id = ?
                """,
                (response_id,),
            ).fetchone()
            if not row:
                return None
            payload = dict(row)
            for key in [
                "data_points_json",
                "primary_concepts_json",
                "ideal_reasoning_targets_json",
                "strengths_json",
                "weaknesses_json",
                "missed_concepts_json",
                "incorrect_assumptions_json",
                "key_concepts_json",
            ]:
                if payload.get(key):
                    payload[key] = json.loads(payload[key])
            return payload

    def get_average_score_by_role(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT s.role_name, ROUND(AVG(e.overall_score), 1) AS avg_score, COUNT(*) AS attempts
                FROM evaluations e
                JOIN responses r ON r.id = e.response_id
                JOIN scenarios s ON s.id = r.scenario_id
                GROUP BY s.role_name
                ORDER BY avg_score DESC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def get_total_practice_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM responses").fetchone()
            return int(row["count"])

    def get_recent_performance(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT s.role_name, s.module_name, e.overall_score, r.created_at
                FROM evaluations e
                JOIN responses r ON r.id = e.response_id
                JOIN scenarios s ON s.id = r.scenario_id
                ORDER BY e.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def reset_database(self, confirmed: bool) -> bool:
        if not confirmed:
            return False
        if self.db_path.exists():
            self.db_path.unlink()
        self._create_tables()
        self._seed_curriculum_if_needed()
        return True
