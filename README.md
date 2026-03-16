# 🎙️ Parsepod

> *Turn any topic into a compelling two-host podcast episode — automatically.*

Parsepod is an AI-powered podcast generator that researches any topic from the web, writes a natural two-host script, and converts it to audio — all in one click.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini_API-Free_Tier-orange?logo=google&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ What it does

```
You type a topic
      ↓
🔍 Tavily searches & scrapes the web
      ↓
🧠 Gemini summarises and writes a two-host script
      ↓
🎤 Edge TTS voices Ryan & Jenny
      ↓
🎧 pydub assembles everything into one MP3
      ↓
▶️ You listen in the browser
```

---

## 🎭 Meet the Hosts

| Host | Voice | Personality |
|------|-------|-------------|
| 🇬🇧 **Ryan** | `en-GB-RyanNeural` | British, analytical, dry wit |
| 🇺🇸 **Jenny** | `en-US-JennyNeural` | American, warm, curious |

---

## 🛠️ Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| 🔍 Search + Scrape | [Tavily API](https://tavily.com) | AI-native, returns clean text |
| 🧠 LLM Brain | [Gemini API](https://aistudio.google.com) | Free tier, generous limits |
| 🎤 Text to Speech | [Edge TTS](https://github.com/rany2/edge-tts) | Free, 400+ voices, no limits |
| 🎵 Audio Assembly | [pydub](https://github.com/jiaaro/pydub) | Simple MP3 assembly |
| 🖥️ Frontend | [Streamlit](https://streamlit.io) | Fast, Python-native UI |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- ffmpeg (`brew install ffmpeg` on Mac)
- API keys for Tavily and Gemini

### 1. Clone the repo

```bash
git clone https://github.com/hemantch/parsepod.git
cd parsepod
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up API keys

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```env
TAVILY_API_KEY=tvly-your-key-here
GEMINI_API_KEY=AIza-your-key-here
```

Get your free API keys:
- 🔍 **Tavily** → [tavily.com](https://tavily.com) — 1,000 free searches/month
- 🧠 **Gemini** → [aistudio.google.com](https://aistudio.google.com) — free tier, no credit card

### 5. Run the app

```bash
streamlit run ui/app.py
```

Opens at **http://localhost:8501** 🎉

---

## 🖥️ CLI Usage

Generate an episode directly from the terminal:

```bash
python run.py "the rise of open source AI models"
```

---

## 📁 Project Structure

```
parsepod/
├── 🔍 research/
│   ├── searcher.py      # Tavily search
│   └── scraper.py       # Tavily extract
├── 📝 script/
│   └── writer.py        # Gemini script generation
├── 🎵 audio/
│   ├── tts.py           # Edge TTS synthesis
│   └── assembler.py     # pydub MP3 assembly
├── 🖥️ ui/
│   └── app.py           # Streamlit frontend
├── 📤 output/           # Final MP3 files
├── 🗂️ temp/             # Intermediate segments
├── config.py            # Environment config
├── run.py               # CLI entry point
└── CLAUDE.md            # Claude Code memory
```

---

## 💰 Cost Breakdown

| Service | Free Tier | Per Episode |
|---------|-----------|-------------|
| Tavily | 1,000/month | ~$0.001 |
| Gemini API | 100 req/day | ~$0.00 |
| Edge TTS | Unlimited | $0.00 |
| **Total** | | **~$0.001** |

> 💡 Essentially free to run for personal use!

---

## 🗺️ Roadmap

- [x] 🔍 Web research with Tavily
- [x] 🧠 Script generation with Gemini
- [x] 🎤 Two-host TTS with Edge TTS
- [x] 🎵 Audio assembly with pydub
- [x] 🖥️ Streamlit UI
- [ ] ☁️ Streamlit Cloud deployment
- [ ] 📄 Document upload (PDF, Word, PPT)
- [ ] 🔄 n8n workflow integration
- [ ] 🤖 CrewAI multi-agent pipeline
- [ ] 🎙️ RSS feed for podcast distribution

---

## 🔒 Security

- API keys stored in `.env` — never committed to git
- Prompt injection protection on all Gemini calls
- Content sanitisation on scraped web content
- Output validation on all LLM responses

---

## 🙏 Acknowledgements

- [Tavily](https://tavily.com) — AI-native search API
- [Google AI Studio](https://aistudio.google.com) — Gemini API
- [Edge TTS](https://github.com/rany2/edge-tts) — Microsoft Edge voices
- [Streamlit](https://streamlit.io) — Python web app framework
- [Claude Code](https://claude.ai) — AI coding assistant that built this

---

## 📬 Built by

**Hemanth** — built with ☕ and Claude Code

---

*🎙️ Parsepod — Research. Script. Listen.*
