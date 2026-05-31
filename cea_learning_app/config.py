"""Application configuration for the CEA learning app."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "app.db"))


def get_api_key() -> Optional[str]:
    """Return OpenAI API key from env first, then Streamlit secrets if available."""
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key

    try:
        import streamlit as st

        secret_key = st.secrets.get("OPENAI_API_KEY")
        if secret_key:
            return str(secret_key)
    except Exception:
        return None
    return None


def is_mock_mode() -> bool:
    """Enable deterministic mock mode whenever key is unavailable."""
    return get_api_key() is None


MOCK_MODE = is_mock_mode()
