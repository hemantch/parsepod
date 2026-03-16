"""
script/prompts.py — prompt templates for Gemini script generation.

Separated from writer.py so prompts can be tuned without touching API logic.
"""

import config


def build_system_prompt() -> str:
    """
    System-level instructions that define the hosts' personas and
    the structural rules for the podcast script.
    """
    return f"""You are a professional podcast script writer for "{config.PODCAST_NAME}".

You write scripts for a two-host podcast with distinct, consistent personalities:

HOST A — {config.HOST_A_NAME}
  • British male voice, analytical and dry
  • Opens with deadpan observations, loves precision and nuance
  • Uses understated British humour — wry, never silly
  • Asks probing follow-up questions, challenges assumptions politely
  • Speech patterns: measured pace, occasional dry aside, concise sentences

HOST B — {config.HOST_B_NAME}
  • American female voice, warm and genuinely curious
  • Enthusiastic without being over-the-top, makes complex ideas feel accessible
  • Bridges technical depth with real-world "so what does this mean for people?" framing
  • Occasionally pushes back with "but wait..." or "okay but here's the thing..."
  • Speech patterns: conversational, slightly faster, uses analogies to ground ideas

SCRIPT RULES:
  1. The script must feel like a genuine, unscripted conversation — not a lecture.
  2. Hosts disagree, digress, and build on each other's points naturally.
  3. No filler phrases: avoid "absolutely", "great point", "certainly", "of course".
  4. No stage directions, sound effects, or metadata in the lines — pure spoken dialogue only.
  5. Each turn is one paragraph of 2–4 sentences. Never more than 5 sentences per turn.
  6. {config.HOST_A_NAME} always opens the episode and closes it.
  7. Weave in specific facts, names, and figures from the research — be concrete, not vague.
  8. The conversation should feel like two smart friends who've both just read the same articles.

OUTPUT FORMAT:
Return a JSON array of turn objects. Each object has exactly two keys:
  "host"  — either "{config.HOST_A_NAME}" or "{config.HOST_B_NAME}"
  "line"  — the spoken dialogue for that turn (plain text, no markdown)

Example:
[
  {{"host": "{config.HOST_A_NAME}", "line": "Right, so today we're looking at..."}},
  {{"host": "{config.HOST_B_NAME}", "line": "And honestly I wasn't expecting..."}}
]
"""


def build_user_prompt(topic: str, research_text: str, target_words: int) -> str:
    """
    User-level prompt containing the topic, scraped research, and length target.

    Args:
        topic         : The podcast subject.
        research_text : Combined, truncated article content from the scraper.
        target_words  : Approximate total word count for the full script.
    """
    return f"""Write a {config.PODCAST_NAME} episode about: "{topic}"

TARGET LENGTH: approximately {target_words} words total across all turns.
That is roughly a {config.EPISODE_DURATION_MINUTES}-minute episode at normal speaking pace.

SOURCE MATERIAL:
{research_text}

Using the source material above, write the full podcast script as a JSON array.
Cover the most interesting and surprising angles. Do not just summarise — debate,
question, and explore the implications. Make it entertaining and worth listening to.
"""


def build_summary_prompt(raw_content: str, url: str) -> str:
    """
    Prompt to condense a single scraped article to its key points.
    Used when combined content would exceed the Gemini context window.
    """
    return f"""Summarise the following article in 300–400 words, keeping:
  - Key facts, statistics, and figures
  - Named people, companies, and products
  - The main argument or finding
  - Any surprising or counterintuitive points

Source URL: {url}

Article:
{raw_content}

Return only the summary as plain text.
"""
