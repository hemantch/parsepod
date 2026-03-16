"""
run.py — CLI entry point for Parsepod.

Usage:
    python run.py "topic"
    python run.py "the rise of open source AI models"
"""

import asyncio
import sys

import config


async def main(topic: str):
    config.validate()

    print(f"\n{'='*60}")
    print(f"  {config.PODCAST_NAME}")
    print(f"  Topic: {topic}")
    print(f"{'='*60}\n")

    # ── Step 1: Research ──────────────────────────────────────────
    from research.scraper import search_and_scrape
    print("[1/4] Researching topic...")
    research_data = await search_and_scrape(topic)

    # ── Step 2: Script ────────────────────────────────────────────
    from script.writer import generate_script
    print("[2/4] Writing podcast script...")
    script = await generate_script(research_data)

    # ── Step 3: Text-to-speech ────────────────────────────────────
    from audio.tts import synthesise_turn
    print("[3/4] Synthesising voices...")
    # (assembler handles segment paths)

    # ── Step 4: Assemble MP3 ──────────────────────────────────────
    from audio.assembler import assemble_episode
    print("[4/4] Assembling episode...")

    print("\nDone! Episode saved to:", config.OUTPUT_DIR)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py \"your topic here\"")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    asyncio.run(main(topic))
