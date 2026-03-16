# 🎙️ Parsepod

> *Turn any topic into a compelling two-host podcast episode — automatically.*

Parsepod is an AI-powered podcast generator that researches any topic from the web, writes a natural two-host script, and converts it to audio — all in one click.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange?logo=groq&logoColor=white)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

🚀 **[Live Demo → parsepod.streamlit.app](https://parsepod.streamlit.app)**

---

## ✨ What it does

```
You type a topic
      ↓
🔍 Tavily searches & scrapes the web
      ↓
🧠 Groq (LLaMA 3.3 70B) writes a two-host script
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
| 🧠 LLM Brain | [Groq API](https://console.groq.com) — LLaMA 3.3 70B | Free tier, blazing fast inference |
| 🎤 Text to Speech | [Edge TTS](https://github.com/rany2/edge-tts) | Free, 400+ voices, no limits |
| 🎵 Audio Assembly | [pydub](https://github.com/jiaaro/pydub) + ffmpeg | Simple MP3 assembly |
| 🖥️ Frontend | [Streamlit](https://streamlit.io) | Fast, Python-native UI |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- ffmpeg (`brew install ffmpeg` on Mac)
- API keys for Tavily and Groq

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
GROQ_API_KEY=gsk-your-key-here
EPISODE_DURATION_MINUTES=3
```

Get your free API keys:
- 🔍 **Tavily** → [tavily.com](https://tavily.com) — 1,000 free searches/month
- 🧠 **Groq** → [console.groq.com](https://console.groq.com) — free, no credit card required

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
   TAVILY_API_KEY = "tvly-your-key-here"
   GROQ_API_KEY   = "gsk-your-key-here"
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
│   ├── writer.py        # Groq script generation
│   └── prompts.py       # Prompt templates
├── 🎵 audio/
│   ├── tts.py           # Edge TTS synthesis
│   └── assembler.py     # pydub MP3 assembly
├── 🖥️ ui/
│   └── app.py           # Streamlit frontend
├── 📤 output/           # Final MP3 files
├── 🗂️ temp/             # Intermediate segments
├── packages.txt         # System packages (ffmpeg) for Streamlit Cloud
├── config.py            # Environment config
├── run.py               # CLI entry point
└── CLAUDE.md            # Project notes
```

---

## 💰 Cost Breakdown

| Service | Free Tier | Per Episode |
|---------|-----------|-------------|
| Tavily | 1,000 searches/month | ~$0.001 |
| Groq API | 14,400 req/day · 30M tokens/day | $0.00 |
| Edge TTS | Unlimited | $0.00 |
| **Total** | | **~$0.001** |

> 💡 Essentially free to run — Groq's free tier is extremely generous!

---

## 🗺️ Roadmap

- [x] 🔍 Web research with Tavily
- [x] 🧠 Script generation with Groq (LLaMA 3.3 70B)
- [x] 🎤 Two-host TTS with Edge TTS
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
- [Groq](https://console.groq.com) — ultra-fast LLaMA inference
- [Edge TTS](https://github.com/rany2/edge-tts) — Microsoft Edge voices
- [Streamlit](https://streamlit.io) — Python web app framework
- [Claude Code](https://claude.ai) — AI coding assistant that built this

---

## 📬 Built by

**Hemanth** — built with ☕ and Claude Code

---

*🎙️ Parsepod — Research. Script. Listen.*
