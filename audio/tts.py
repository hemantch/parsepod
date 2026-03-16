"""
audio/tts.py — convert a single script turn to an MP3 segment using Edge TTS.

Edge TTS is free, requires no API key, and streams audio directly from
Microsoft's Azure text-to-speech infrastructure via the edge-tts library.

Each call to synthesise_turn() produces one MP3 file in the temp directory,
named by turn index so the assembler can stitch them in order.
"""

import asyncio
import os
from pathlib import Path

import edge_tts

import config


# ── Voice reference ────────────────────────────────────────────────────────────
# Swap these in .env (HOST_A_VOICE / HOST_B_VOICE) to change the voices.
#
# British male                British female
# ─────────────────────────── ──────────────────────────────
# en-GB-ThomasNeural  ← current (natural, measured)
# en-GB-RyanNeural    (clear, slightly formal)
# en-GB-OliverNeural  (warm, conversational)
# en-GB-NoahNeural    (younger, relaxed)
#
#                             en-GB-LibbyNeural   ← current (warm, expressive)
#                             en-GB-SoniaNeural   (crisp, professional)
#                             en-GB-MaisieNeural  (light, friendly)
#
# American male               American female
# ─────────────────────────── ──────────────────────────────
# en-US-GuyNeural     (neutral, broadcast)
# en-US-AndrewNeural  (deep, authoritative)
# en-US-BrianNeural   (upbeat, conversational)
#
#                             en-US-JennyNeural   (warm, energetic)
#                             en-US-AriaNeural    (natural, expressive)
#                             en-US-SaraNeural    (calm, clear)
#
# Run `edge-tts --list-voices` in your terminal to see all 400+ options.
# ──────────────────────────────────────────────────────────────────────────────


async def synthesise_turn(text: str, voice: str, output_path: str) -> str:
    """
    Convert a single line of dialogue to speech and save it as an MP3.

    Args:
        text        : The spoken line (plain text, no SSML markup needed).
        voice       : Edge TTS voice identifier, e.g. "en-GB-RyanNeural".
        output_path : Full path where the MP3 segment will be written.

    Returns:
        output_path on success.

    Raises:
        edge_tts.exceptions.NoAudioReceived : If Edge TTS returns no audio
            (usually means the text was empty or the voice name was invalid).
    """
    # Ensure the parent directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(output_path)

    return output_path


async def synthesise_script(
    script: list[dict[str, str]],
    temp_dir: str | None = None,
) -> list[str]:
    """
    Synthesise every turn in a podcast script, saving one MP3 per turn.

    Runs turns sequentially to respect Edge TTS rate limits.

    Args:
        script   : List of {"host": str, "line": str} dicts.
        temp_dir : Directory for segment files. Defaults to config.TEMP_DIR.

    Returns:
        Ordered list of paths to the generated MP3 segments.
    """
    temp_dir = temp_dir or config.TEMP_DIR
    os.makedirs(temp_dir, exist_ok=True)

    # Map host names → voice identifiers from config
    voice_map = {
        config.HOST_A_NAME: config.HOST_A_VOICE,
        config.HOST_B_NAME: config.HOST_B_VOICE,
    }

    segment_paths: list[str] = []
    total = len(script)

    for i, turn in enumerate(script):
        host  = turn["host"]
        line  = turn["line"]
        voice = voice_map.get(host)

        if not voice:
            raise ValueError(
                f"Turn {i}: unknown host '{host}'. "
                f"Expected one of: {list(voice_map.keys())}"
            )

        # Zero-padded filename keeps directory listing in order
        segment_path = os.path.join(temp_dir, f"turn_{i:03d}_{host.lower()}.mp3")

        print(f"[audio] TTS {i + 1}/{total} [{host}] → {os.path.basename(segment_path)}")
        await synthesise_turn(line, voice, segment_path)

        segment_paths.append(segment_path)

    print(f"[audio] Synthesised {len(segment_paths)} segments.")
    return segment_paths


# ── CLI smoke-test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    async def _main():
        test_script = [
            {"host": config.HOST_A_NAME,
             "line": "Welcome to Parsepod. Today we're exploring something rather fascinating."},
            {"host": config.HOST_B_NAME,
             "line": "I'm so excited about this one! Let's dive right in."},
            {"host": config.HOST_A_NAME,
             "line": "Right. Let's keep it measured, shall we."},
        ]
        paths = await synthesise_script(test_script, temp_dir="temp")
        print("\nSegments written:")
        for p in paths:
            size_kb = os.path.getsize(p) / 1024
            print(f"  {p}  ({size_kb:.1f} KB)")

    asyncio.run(_main())
