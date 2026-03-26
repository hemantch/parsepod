# Parsepod

AI-powered podcast generator that searches the web for a given topic, generates a two-host podcast script, and converts it to audio saved as MP3. No summarisation step — raw scraped content (capped at 5,000 chars/page) is passed directly to the LLM.

## Tech Stack

- **Tavily API** — web search and scraping (`AsyncTavilyClient`)
- **Groq API** — LLM brain, model `llama-3.3-70b-versatile`, JSON mode
- **Edge TTS** — text to speech, free, no API key needed
- **pydub** + **ffmpeg** — audio assembly and MP3 export
- **Streamlit** — premium dark UI (purple/indigo theme, glassmorphism)

## Hosts

| Host | Voice | Personality |
|------|-------|-------------|
| Ryan (Host A) | `en-GB-ThomasNeural` | British male, analytical, dry wit |
| Jenny (Host B) | `en-GB-LibbyNeural` | British female, warm, curious |

To change voices: edit `HOST_A_VOICE` / `HOST_B_VOICE` in `.env`.
Full voice reference with alternatives is in `audio/tts.py`.

## Project Structure

```
parsepod/
├── research/
│   ├── searcher.py      # Tavily search (MAX_RESULTS=8, advanced depth)
│   └── scraper.py       # Tavily extract (MAX_URLS=3, 5k chars/page cap)
├── script/
│   ├── writer.py        # Groq script generation (llama-3.3-70b-versatile)
│   └── prompts.py       # System + user prompt builders
├── audio/
│   ├── tts.py           # Edge TTS synthesis, sequential per turn
│   └── assembler.py     # pydub MP3 assembly, 450ms silence between turns
├── ui/
│   └── app.py           # Streamlit UI — premium studio theme
├── output/              # Final MP3 + JSON metadata files
├── temp/                # Intermediate per-turn MP3 segments
├── config.py            # Settings: st.secrets → os.environ → default
├── run.py               # CLI entry point
├── requirements.txt
└── packages.txt         # ffmpeg for Streamlit Cloud
```

## Environment Variables

```env
TAVILY_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
PODCAST_NAME=Parsepod
HOST_A_NAME=Ryan
HOST_B_NAME=Jenny
HOST_A_VOICE=en-GB-ThomasNeural
HOST_B_VOICE=en-GB-LibbyNeural
OUTPUT_DIR=./output
TEMP_DIR=./temp
EPISODE_DURATION_MINUTES=3
SILENCE_BETWEEN_TURNS_MS=450
```

Config priority: `st.secrets` (Streamlit Cloud) → `.env` → hard-coded default.

## Key Commands

```bash
# Start the Streamlit UI
streamlit run ui/app.py

# Run via CLI
python run.py "topic"

# List all available Edge TTS voices
edge-tts --list-voices
```

## Streamlit Cloud Deployment

- API keys go in the app's **Secrets** panel as TOML
- `packages.txt` lists `ffmpeg` (installed via apt before startup)
- `audioop-lts; python_version >= "3.13"` in `requirements.txt` handles Python 3.13+ compat
- `.streamlit/config.toml` sets the dark theme and disables usage stats

## UI Design

- Background `#0a0a0f`, accent gradient purple (`#a855f7`) → cyan (`#22d3ee`)
- Glassmorphism cards with `backdrop-filter: blur`
- Animated hero soundwave + glow orbs
- **On Air studio panel** during generation: two host avatar cards with EQ bars, pulsing REC dot, 4-stage progress (Research → Script → Recording → Mixing)
- Custom HTML5 audio player (iframe via `components.html`) with waveform and inline download button
- All `st.markdown()` HTML strings are compact (no 4-space indentation — avoids markdown code-block rendering bug)

## Important: HTML in st.markdown

Never indent HTML passed to `st.markdown(..., unsafe_allow_html=True)` with 4+ spaces. The markdown parser treats 4-space-indented lines as code blocks, causing raw HTML to display as text. Use string concatenation or `f'...'` one-liners instead of multiline f-strings with indentation.

## Coding Style

- Clean, well-commented Python
- `async`/`await` for Edge TTS and Tavily; Groq client is synchronous
- Each module has a single responsibility
- No summarisation step — content is capped at the scraper level (5k chars/page)
- No retry/fallback logic in the LLM layer — fail fast and surface errors

## UI State (March 2026)

- The UI was fully redesigned with a dark broadcast studio aesthetic (background `#0a0a0f`, purple → cyan gradient, glassmorphism)
- **Hero section is a single centered column** — the previous two-column layout (`st.columns([3, 2])`) was removed entirely
- All hero elements stack vertically and are center-aligned; `!important` CSS overrides are required to beat Streamlit's default left-align styles
- Subheadline (`.pp-sub`): `text-align: center !important; width: 100% !important; max-width: 520px !important; margin: 0 auto !important;`
- "YOUR TOPIC" label (`.pp-card-label`): `text-align: center !important; display: block !important; width: 100% !important; max-width: 600px !important; margin: 0 auto !important;`
- Input form (`[data-testid="stForm"]`): `max-width: 600px !important; margin: 0 auto !important;`
- Host chips (`.pp-host-chips`) are centered with `justify-content: center`; they display **Thomas** and **Libby** (the voice names, not Ryan/Jenny)
- Progress stages during generation use `st.empty()` populated via `stage_slot.markdown(..., unsafe_allow_html=True)`
- Navbar (fixed, frosted-glass) includes: How it works · About · Launch Studio CTA button
- Footer links: GitHub · Docs · Privacy
- **Rule:** when overriding Streamlit default styles, always use `!important` and the most specific selector available — bare class selectors are often not specific enough
