"""
config.py — centralised settings loaded from .env (local) or st.secrets (Streamlit Cloud).
All modules import from here rather than reading os.environ directly.

Priority order for each value:
  1. st.secrets  (Streamlit Cloud — set in the app's Secrets panel)
  2. os.environ  (local .env loaded by python-dotenv)
  3. hard-coded default
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    """
    Read a config value from st.secrets (Streamlit Cloud) if available,
    falling back to os.environ, then the provided default.
    """
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)


# ── API Keys ──────────────────────────────────────────────────────────────────
TAVILY_API_KEY: str = _get("TAVILY_API_KEY")
GEMINI_API_KEY: str = _get("GEMINI_API_KEY")

# ── Podcast identity ──────────────────────────────────────────────────────────
PODCAST_NAME: str = _get("PODCAST_NAME", "Parsepod")

HOST_A_NAME: str  = _get("HOST_A_NAME", "Ryan")
HOST_B_NAME: str  = _get("HOST_B_NAME", "Jenny")
HOST_A_VOICE: str = _get("HOST_A_VOICE", "en-GB-RyanNeural")
HOST_B_VOICE: str = _get("HOST_B_VOICE", "en-US-JennyNeural")

# ── Paths ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR: str = _get("OUTPUT_DIR", "./output")
TEMP_DIR: str   = _get("TEMP_DIR",   "./temp")

# ── Episode settings ──────────────────────────────────────────────────────────
# Default is 3 minutes — override via .env or st.secrets
EPISODE_DURATION_MINUTES: int = int(_get("EPISODE_DURATION_MINUTES", "3"))
SILENCE_BETWEEN_TURNS_MS: int = int(_get("SILENCE_BETWEEN_TURNS_MS", "450"))

# ── Validation ────────────────────────────────────────────────────────────────
def validate():
    """Raise early if required API keys are missing."""
    missing = []
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please add them to your .env file."
        )
