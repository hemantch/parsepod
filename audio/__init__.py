"""audio — text-to-speech and MP3 assembly."""

from .tts import synthesise_turn
from .assembler import assemble_episode

__all__ = ["synthesise_turn", "assemble_episode"]
