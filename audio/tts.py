"""
audio/tts.py — synthesise a podcast script using Gemini multi-speaker TTS.

Model: gemini-3.1-flash-tts-preview

The script is split into chunks of CHUNK_SIZE turns. Each chunk is sent as a
single multi-speaker dialogue call, producing one MP3 per chunk in temp_dir.

Checkpointing: each chunk file is named chunk_NNN_<hash>.mp3 where the hash
is derived from the chunk's dialogue content. On rerun, existing chunk files
are skipped so generation resumes from the first missing chunk.

Retry logic: up to MAX_RETRIES attempts per chunk with exponential backoff and
jitter, handling both HTTP 5xx errors and the text-token failure mode (missing
inline_data in the response).
"""

import hashlib
import io
import os
import random
import time
from pathlib import Path

from google import genai
from google.genai import types
from pydub import AudioSegment

import config


# ── Constants ──────────────────────────────────────────────────────────────────

GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
CHUNK_SIZE       = 10
MAX_RETRIES      = 5

# Gemini TTS output: raw PCM, 24 kHz, 16-bit signed, mono, little-endian
PCM_SAMPLE_RATE  = 24_000
PCM_SAMPLE_WIDTH = 2        # bytes (16-bit)
PCM_CHANNELS     = 1

# Base delays per retry attempt index 0–4 (before jitter)
_BACKOFF_DELAYS = [1, 2, 4, 8, 16]


# ── Public API ─────────────────────────────────────────────────────────────────

async def synthesise_script(
    script: list[dict[str, str]],
    temp_dir: str | None = None,
) -> list[str]:
    """
    Synthesise a full podcast script using Gemini multi-speaker TTS.

    Splits script into chunks of CHUNK_SIZE turns, calls Gemini once per chunk,
    and saves one MP3 per chunk in temp_dir. Already-completed chunks are
    skipped on rerun (checkpointing via content hash in filename).

    Args:
        script   : List of {"host": str, "line": str} dicts.
        temp_dir : Directory for chunk files. Defaults to config.TEMP_DIR.

    Returns:
        Ordered list of paths to the generated chunk MP3s.
    """
    temp_dir = temp_dir or config.TEMP_DIR
    os.makedirs(temp_dir, exist_ok=True)

    client       = genai.Client(api_key=config.GEMINI_API_KEY)
    style_prompt = config.TTS_STYLE_PROMPT
    chunks       = [script[i : i + CHUNK_SIZE] for i in range(0, len(script), CHUNK_SIZE)]
    total_chunks = len(chunks)
    total_turns  = len(script)

    print(f"[audio] Synthesising {total_turns} turns in {total_chunks} chunk(s) "
          f"via {GEMINI_TTS_MODEL}...")

    chunk_paths: list[str] = []

    for i, chunk in enumerate(chunks):
        dialogue   = _format_dialogue(chunk)
        chunk_path = _chunk_path(temp_dir, i, dialogue)

        if os.path.exists(chunk_path):
            size_kb = os.path.getsize(chunk_path) / 1024
            print(f"[audio] Chunk {i + 1}/{total_chunks} — skipped (cached, {size_kb:.0f} KB)")
            chunk_paths.append(chunk_path)
            continue

        start = i * CHUNK_SIZE + 1
        end   = min((i + 1) * CHUNK_SIZE, total_turns)
        print(f"[audio] Chunk {i + 1}/{total_chunks} "
              f"(turns {start}–{end}) → {os.path.basename(chunk_path)}")

        pcm_bytes = _call_tts_with_retry(client, dialogue, style_prompt,
                                         chunk_num=i + 1, total_chunks=total_chunks)
        _pcm_to_mp3(pcm_bytes, chunk_path)
        chunk_paths.append(chunk_path)

    print(f"[audio] Done — {len(chunk_paths)} chunk(s) ready.")
    return chunk_paths


# ── Internal helpers ───────────────────────────────────────────────────────────

def _format_dialogue(chunk: list[dict[str, str]]) -> str:
    """Format turns as 'SpeakerAlias: line' block for Gemini multi-speaker input."""
    return "\n".join(f"{turn['host']}: {turn['line']}" for turn in chunk)


def _chunk_path(temp_dir: str, index: int, dialogue: str) -> str:
    """Deterministic chunk filename: chunk_NNN_<8-char content hash>.mp3"""
    content_hash = hashlib.md5(dialogue.encode()).hexdigest()[:8]
    return os.path.join(temp_dir, f"chunk_{index:03d}_{content_hash}.mp3")


def _build_tts_config() -> types.GenerateContentConfig:
    """Build the GenerateContentConfig with multi-speaker voice assignments."""
    return types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker=config.HOST_A_NAME,
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=config.HOST_A_VOICE,
                            )
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker=config.HOST_B_NAME,
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=config.HOST_B_VOICE,
                            )
                        ),
                    ),
                ]
            )
        ),
    )


def _call_tts_with_retry(
    client: genai.Client,
    dialogue: str,
    style_prompt: str,
    chunk_num: int,
    total_chunks: int,
) -> bytes:
    """
    Call Gemini TTS for one dialogue chunk, retrying up to MAX_RETRIES times.

    Retries on:
      - Any exception (covers HTTP 5xx from Gemini)
      - Response missing inline_data (text token returned instead of audio)

    Backoff: exponential (1s, 2s, 4s, 8s, 16s) + random jitter (0–1s per attempt).

    Returns raw PCM bytes on success.
    Raises RuntimeError with resume hint if all retries fail.
    """
    tts_config = _build_tts_config()
    contents   = f"{style_prompt}\n\n{dialogue}" if style_prompt else dialogue

    last_exc: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=GEMINI_TTS_MODEL,
                contents=contents,
                config=tts_config,
            )

            # Guard against the text-token failure mode
            part = response.candidates[0].content.parts[0]
            if not hasattr(part, "inline_data") or part.inline_data is None:
                raise ValueError(
                    "TTS response missing inline_data (text token returned instead of audio)"
                )

            audio_bytes = part.inline_data.data
            if not audio_bytes:
                raise ValueError("TTS response inline_data is empty")

            return audio_bytes

        except Exception as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                delay = _BACKOFF_DELAYS[attempt] + random.random()
                print(f"[audio] Chunk {chunk_num}/{total_chunks} attempt {attempt + 1} "
                      f"failed ({exc}). Retrying in {delay:.1f}s...")
                time.sleep(delay)

    raise RuntimeError(
        f"TTS failed at chunk {chunk_num}/{total_chunks} after {MAX_RETRIES} retries. "
        f"Last error: {last_exc}. "
        f"Rerun to resume from chunk {chunk_num}."
    ) from last_exc


def _pcm_to_mp3(pcm_bytes: bytes, output_path: str) -> None:
    """Convert raw PCM bytes (24 kHz / 16-bit / mono) to 128 kbps MP3."""
    segment = AudioSegment.from_raw(
        io.BytesIO(pcm_bytes),
        sample_width=PCM_SAMPLE_WIDTH,
        frame_rate=PCM_SAMPLE_RATE,
        channels=PCM_CHANNELS,
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    segment.export(output_path, format="mp3", bitrate="128k")


# ── CLI smoke-test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio

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
        print("\nChunks written:")
        for p in paths:
            size_kb = os.path.getsize(p) / 1024
            print(f"  {p}  ({size_kb:.1f} KB)")

    asyncio.run(_main())
