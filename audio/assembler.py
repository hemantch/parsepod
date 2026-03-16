"""
audio/assembler.py — stitch MP3 segments into a single episode file using pydub.

Each segment produced by tts.py is loaded, a configurable silence gap is
appended after each turn, and the whole thing is exported as a 128 kbps MP3.

pydub requires ffmpeg to be installed on the system for MP3 encoding/decoding.
"""

import os
from datetime import datetime
from pathlib import Path

from pydub import AudioSegment

import config


def assemble_episode(
    segment_paths: list[str],
    output_path: str | None = None,
    silence_ms: int | None = None,
) -> str:
    """
    Concatenate audio segments with silence between turns and export as MP3.

    Args:
        segment_paths : Ordered list of paths to individual MP3 segments.
        output_path   : Destination path for the final MP3.
                        If None, auto-generates a timestamped filename in
                        config.OUTPUT_DIR.
        silence_ms    : Milliseconds of silence between turns.
                        Defaults to config.SILENCE_BETWEEN_TURNS_MS.

    Returns:
        The output_path where the final MP3 was saved.

    Raises:
        FileNotFoundError : If any segment file doesn't exist.
        ValueError        : If segment_paths is empty.
    """
    if not segment_paths:
        raise ValueError("No segment paths provided — nothing to assemble.")

    silence_ms = silence_ms if silence_ms is not None else config.SILENCE_BETWEEN_TURNS_MS
    output_path = output_path or _default_output_path()

    # Ensure the output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Build the silence clip once and reuse it between turns
    gap = AudioSegment.silent(duration=silence_ms)

    print(f"[audio] Assembling {len(segment_paths)} segments "
          f"(+{silence_ms}ms silence between turns)...")

    episode = AudioSegment.empty()

    for i, path in enumerate(segment_paths):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Segment file not found: {path}")

        segment = AudioSegment.from_mp3(path)
        episode += segment

        # Add silence after every turn except the last
        if i < len(segment_paths) - 1:
            episode += gap

    # Export as 128 kbps stereo MP3
    episode.export(output_path, format="mp3", bitrate="128k")

    duration_s  = len(episode) / 1000
    duration_min = duration_s / 60
    size_mb     = os.path.getsize(output_path) / (1024 * 1024)

    print(f"[audio] Episode saved → {output_path}")
    print(f"[audio] Duration : {duration_min:.1f} min ({duration_s:.0f}s)")
    print(f"[audio] File size: {size_mb:.1f} MB")

    return output_path


def _default_output_path() -> str:
    """Generate a timestamped MP3 filename in config.OUTPUT_DIR."""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{config.PODCAST_NAME.lower()}_{timestamp}.mp3"
    return os.path.join(config.OUTPUT_DIR, filename)


# ── CLI smoke-test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import glob

    # Grab whatever segments are already in temp/ from a previous TTS run
    segments = sorted(glob.glob("temp/turn_*.mp3"))

    if not segments:
        print("No segments found in temp/. Run audio/tts.py first.")
    else:
        output = assemble_episode(segments)
        print(f"\nFinal episode: {output}")
