"""Application configuration for the CEA learning app."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import streamlit as st

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "app.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

AVAILABLE_MODELS = {
    "GPT-4o Mini (Cost-Efficient)": "gpt-4o-mini",
    "GPT-4o (High Performance Reasoning)": "gpt-4o",
    "o1-Mini (Advanced Logical Planning)": "o1-mini",
}

DEFAULT_MODEL = "gpt-4o-mini"


def get_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    return api_key or ""


def is_mock_mode() -> bool:
    return get_api_key() == ""


def get_model_id(selected_label: Optional[str]) -> str:
    """Resolve selected model label to API model id with safe fallback."""
    if selected_label and selected_label in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[selected_label]
    return DEFAULT_MODEL


def get_default_model_label() -> str:
    """Return display label for DEFAULT_MODEL or first available option."""
    for label, model_id in AVAILABLE_MODELS.items():
        if model_id == DEFAULT_MODEL:
            return label
    return next(iter(AVAILABLE_MODELS))
