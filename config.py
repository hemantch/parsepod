"""
config.py — centralised settings loaded from .env
All modules import from here rather than reading os.environ directly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ── Podcast identity ──────────────────────────────────────────────────────────
PODCAST_NAME: str = os.getenv("PODCAST_NAME", "Parsepod")

HOST_A_NAME: str  = os.getenv("HOST_A_NAME", "Ryan")
HOST_B_NAME: str  = os.getenv("HOST_B_NAME", "Jenny")
HOST_A_VOICE: str = os.getenv("HOST_A_VOICE", "en-GB-RyanNeural")
HOST_B_VOICE: str = os.getenv("HOST_B_VOICE", "en-US-JennyNeural")

# ── Paths ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
TEMP_DIR: str   = os.getenv("TEMP_DIR",   "./temp")

# ── Episode settings ──────────────────────────────────────────────────────────
EPISODE_DURATION_MINUTES: int = int(os.getenv("EPISODE_DURATION_MINUTES", "30"))
SILENCE_BETWEEN_TURNS_MS: int = int(os.getenv("SILENCE_BETWEEN_TURNS_MS", "450"))

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
