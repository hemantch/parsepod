"""audio — text-to-speech and MP3 assembly."""

from .tts import synthesise_script
from .assembler import assemble_episode

__all__ = ["synthesise_script", "assemble_episode"]
