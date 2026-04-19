# 🎙️ Parsepod

> *Turn any topic into a compelling two-host podcast episode — automatically.*

Parsepod is an AI-powered podcast generator that researches any topic from the web, writes a natural two-host script, and converts it to audio — all in one click.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-blue?logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

🚀 **[Live Demo → parsepod.streamlit.app](https://parsepod.streamlit.app)**

---

## ✨ What it does

```
You type a topic
      ↓
🔍 Tavily searches & scrapes the web
      ↓
🧠 Gemini 2.5 Flash writes a two-host script
      ↓
🎤 Gemini 3.1 Flash TTS voices Thomas & Libby
    (multi-speaker, 10 turns per API call)
      ↓
🎧 pydub assembles everything into one MP3
      ↓
▶️ You listen in the browser
```

---

## 🎭 Meet the Hosts

| Host | Voice | Personality |
|------|-------|-------------|
| 🇬🇧 **Thomas** | `Charon` | British male, analytical, dry wit |
| 🇬🇧 **Libby** | `Kore` | British female, warm, curious |

Voices are Gemini TTS prebuilt voices. Change them via `HOST_A_VOICE` / `HOST_B_VOICE` in `.env`.

---

## 🛠️ Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| 🔍 Search + Scrape | [Tavily API](https://tavily.com) | AI-native, returns clean text |
| 🧠 LLM Brain | [Gemini 2.5 Flash](https://ai.google.dev) — `gemini-2.5-flash` | Stable, structured JSON output |
| 🎤 Text to Speech | [Gemini 3.1 Flash TTS](https://ai.google.dev) — `gemini-3.1-flash-tts-preview` | Native multi-speaker dialogue, natural prosody |
| 🎵 Audio Assembly | [pydub](https://github.com/jiaaro/pydub) + ffmpeg | PCM → MP3 conversion and assembly |
| 🖥️ Frontend | [Streamlit](https://streamlit.io) | Fast, Python-native UI |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- ffmpeg (`brew install ffmpeg` on Mac)
- API keys for Tavily and Google Gemini

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
GEMINI_API_KEY=your-gemini-key-here
EPISODE_DURATION_MINUTES=3
```

Get your API keys:
- 🔍 **Tavily** → [tavily.com](https://tavily.com) — 1,000 free searches/month
- 🧠🎤 **Gemini** → [aistudio.google.com](https://aistudio.google.com) — generous free tier; one key covers both LLM and TTS

### 5. Run the app

```bash
streamlit run ui/app.py
```

Opens at **http://localhost:8501** 🎉

---

## ☁️ Deploy to Streamlit Cloud

### Step-by-step

1. **Fork or push** this repo to your GitHub account.

2. Go to **[share.streamlit.io](https://share.streamlit.io)** and click **New app**.

3. Select your repo, set the branch to `main`, and set the **Main file path** to:
   ```
   ui/app.py
   ```

4. Click **Advanced settings** and paste the following into the **Secrets** panel:

   ```toml
   TAVILY_API_KEY   = "tvly-your-key-here"
   GEMINI_API_KEY   = "your-gemini-key-here"
   EPISODE_DURATION_MINUTES = "3"
   ```

5. Click **Deploy**. Streamlit Cloud will:
   - Install system packages from `packages.txt` (includes **ffmpeg** — required by pydub)
   - Install Python packages from `requirements.txt`
   - Start the app automatically

> **Note:** `packages.txt` in the repo root lists `ffmpeg`. Streamlit Cloud runs `apt-get install ffmpeg` automatically before starting the app — no manual server setup needed.

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
│   ├── writer.py        # Gemini 2.5 Flash script generation
│   └── prompts.py       # Prompt templates
├── 🎵 audio/
│   ├── tts.py           # Gemini multi-speaker TTS (chunked, checkpointed)
│   └── assembler.py     # pydub MP3 assembly
├── 🖥️ ui/
│   └── app.py           # Streamlit frontend
├── 📤 output/           # Final MP3 files
├── 🗂️ temp/             # Intermediate chunk MP3s (checkpointed)
├── packages.txt         # System packages (ffmpeg) for Streamlit Cloud
├── config.py            # Environment config
├── run.py               # CLI entry point
└── CLAUDE.md            # Project notes
```

---

## 💰 Cost Breakdown

| Service | Free Tier | Per Episode (est.) |
|---------|-----------|-------------|
| Tavily | 1,000 searches/month | ~$0.001 |
| Gemini 2.5 Flash (LLM) | 1,500 req/day via AI Studio | $0.00 on free tier |
| Gemini 3.1 Flash TTS | Generous free tier via AI Studio | $0.00 on free tier |
| **Total** | | **~$0.001** |

> 💡 Both Gemini models are covered by a single API key from [Google AI Studio](https://aistudio.google.com). Free tier limits are generous for personal use; check [Google's pricing page](https://ai.google.dev/pricing) for current quotas.

---

## 🗺️ Roadmap

- [x] 🔍 Web research with Tavily
- [x] 🧠 Script generation with Gemini 2.5 Flash
- [x] 🎤 Multi-speaker TTS with Gemini 3.1 Flash TTS
- [x] 🎵 Audio assembly with pydub
- [x] 🖥️ Streamlit UI
- [x] ☁️ Streamlit Cloud deployment
- [ ] 📄 Document upload (PDF, Word, PPT)
- [ ] 🔄 n8n workflow integration
- [ ] 🤖 CrewAI multi-agent pipeline
- [ ] 🎙️ RSS feed for podcast distribution

---

## 🔒 Security

- API keys stored in `.env` locally — never committed to git
- On Streamlit Cloud, keys are stored in the encrypted Secrets panel
- Output validation on all LLM responses
- Content capped at 5,000 chars per source to prevent prompt stuffing

---

## 🙏 Acknowledgements

- [Tavily](https://tavily.com) — AI-native search API
- [Google Gemini](https://ai.google.dev) — LLM and multi-speaker TTS
- [Streamlit](https://streamlit.io) — Python web app framework
- [Claude Code](https://claude.ai) — AI coding assistant that built this

---

## 📬 Built by

**Hemanth** — built with ☕ and Claude Code

---

*🎙️ Parsepod — Research. Script. Listen.*
