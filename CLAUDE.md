# Parsepod

AI-powered podcast generator that searches the web for a given topic, summarises the content, generates a two-host podcast script, and converts it to audio saved as MP3.

## Tech Stack

- **Tavily API** — web search and scraping
- **Gemini API** — LLM brain for summarisation and script writing
- **Edge TTS** — text to speech (no API key needed)
- **pydub** — audio assembly
- **Streamlit** — frontend UI

## Hosts

| Host | Voice | Personality |
|------|-------|-------------|
| Ryan (Host A) | `en-GB-RyanNeural` | British male, analytical and dry |
| Jenny (Host B) | `en-US-JennyNeural` | American female, warm and curious |

## Project Structure

```
parsepod/
├── research/   # Tavily search and scraping
├── script/     # Gemini script generation
├── audio/      # Edge TTS and pydub assembly
├── ui/         # Streamlit frontend
├── output/     # Final MP3 files
└── temp/       # Intermediate audio segments
```

## Environment Variables

Create a `.env` file in the project root:

```
TAVILY_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

## Key Commands

```bash
# Start the Streamlit UI
streamlit run ui/app.py

# Run via CLI
python run.py "topic"
```

## Coding Style

- Clean, well-commented Python
- Use `async`/`await` where beneficial (Edge TTS, web requests)
- Keep each module focused on its single responsibility
