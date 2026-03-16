"""
ui/app.py — Parsepod Streamlit frontend (premium dark redesign).

Run with:  streamlit run ui/app.py
"""

import asyncio
import base64
import glob
import json
import os
import sys
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Parsepod — AI Podcast Generator",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Design tokens ──────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, sans-serif !important;
    background: #07070f !important;
}

/* ── Kill Streamlit chrome ── */
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.stDecoration { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── Main container ── */
.main .block-container {
    max-width: 780px !important;
    padding: 0 1.5rem 5rem !important;
    margin: 0 auto !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0f1e; }
::-webkit-scrollbar-thumb { background: #2d2d5a; border-radius: 3px; }

/* ════════════════════════════════
   HERO
   ════════════════════════════════ */
.pp-hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
}
.pp-logo {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.25rem;
}
.pp-logo-icon {
    width: 46px; height: 46px;
    background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 30px rgba(139,92,246,0.4);
}
.pp-logo-name {
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: #e2e8f0;
}
.pp-hero-title {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -1.5px;
    line-height: 1.1;
    margin: 0 0 1rem;
    background: linear-gradient(135deg, #c4b5fd 0%, #8b5cf6 40%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.pp-hero-sub {
    font-size: 1.05rem;
    color: #64748b;
    font-weight: 400;
    margin: 0 0 0.75rem;
}
.pp-hero-badges {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.pp-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 12px;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 999px;
    font-size: 0.75rem;
    color: #a78bfa;
    font-weight: 500;
}

/* ════════════════════════════════
   INPUT CARD
   ════════════════════════════════ */
.pp-input-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 1.75rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}
.pp-input-label {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.6rem;
}

/* Override Streamlit text input */
.stTextInput > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div:focus-within {
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.12) !important;
}
.stTextInput input {
    font-size: 1.05rem !important;
    color: #e2e8f0 !important;
    padding: 0.8rem 1rem !important;
    background: transparent !important;
}
.stTextInput input::placeholder { color: #334155 !important; }

/* Override Streamlit primary button — Generate */
div[data-testid="stButtonGroup"] > button[kind="primary"],
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 50%, #06b6d4 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    padding: 0.75rem 2rem !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 0 30px rgba(139,92,246,0.35) !important;
    transition: transform 0.15s, box-shadow 0.2s !important;
    width: 100% !important;
}
div[data-testid="stButtonGroup"] > button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 0 45px rgba(139,92,246,0.5) !important;
}

/* Secondary / outline buttons (History, Load) */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    transition: border-color 0.15s, color 0.15s !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: rgba(139,92,246,0.5) !important;
    color: #c4b5fd !important;
}

/* ════════════════════════════════
   STAGE PROGRESS
   ════════════════════════════════ */
.stages-wrap {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin: 1.25rem 0;
}
.stage-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1rem;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.stage-card.active {
    border-color: rgba(139,92,246,0.5);
    box-shadow: 0 0 20px rgba(139,92,246,0.15);
    animation: pulse-border 2s ease-in-out infinite;
}
.stage-card.done {
    border-color: rgba(52,211,153,0.35);
    background: rgba(52,211,153,0.04);
}
@keyframes pulse-border {
    0%, 100% { box-shadow: 0 0 15px rgba(139,92,246,0.12); }
    50%       { box-shadow: 0 0 28px rgba(139,92,246,0.28); }
}
.stage-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    display: block;
}
.stage-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 0.2rem;
}
.stage-desc {
    font-size: 0.73rem;
    color: #475569;
    margin-bottom: 0.5rem;
    line-height: 1.4;
}
.stage-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.stage-pill.waiting { background: rgba(255,255,255,0.05); color: #475569; }
.stage-pill.active  { background: rgba(139,92,246,0.2);   color: #a78bfa; }
.stage-pill.done    { background: rgba(52,211,153,0.15);   color: #34d399; }

/* sub-progress bar inside stage card */
.stage-progress {
    height: 2px;
    background: rgba(255,255,255,0.05);
    border-radius: 1px;
    margin-top: 0.6rem;
    overflow: hidden;
}
.stage-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #8b5cf6, #06b6d4);
    border-radius: 1px;
    transition: width 0.4s ease;
}

/* Streamlit native progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #7c3aed, #8b5cf6, #06b6d4) !important;
    border-radius: 999px !important;
}
.stProgress > div > div {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 999px !important;
    height: 4px !important;
}

/* ════════════════════════════════
   TRANSCRIPT
   ════════════════════════════════ */
.transcript-wrap { display: flex; flex-direction: column; gap: 10px; padding: 0.25rem 0; }
.turn {
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.turn-avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 2px;
    letter-spacing: 0.3px;
}
.ryan-avatar  { background: rgba(96,165,250,0.15); color: #60a5fa; border: 1px solid rgba(96,165,250,0.25); }
.jenny-avatar { background: rgba(251,146,60,0.12); color: #fb923c; border: 1px solid rgba(251,146,60,0.22); }
.turn-bubble {
    flex: 1;
    padding: 0.7rem 0.95rem;
    border-radius: 0 12px 12px 12px;
    font-size: 0.88rem;
    line-height: 1.6;
    color: #cbd5e1;
}
.ryan-bubble  {
    background: rgba(96,165,250,0.06);
    border: 1px solid rgba(96,165,250,0.12);
}
.jenny-bubble {
    background: rgba(251,146,60,0.06);
    border: 1px solid rgba(251,146,60,0.12);
}
.turn-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.ryan-label  { color: #60a5fa; }
.jenny-label { color: #fb923c; }

/* ════════════════════════════════
   EXPANDERS
   ════════════════════════════════ */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}
.streamlit-expanderContent {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    background: rgba(255,255,255,0.015) !important;
}

/* ════════════════════════════════
   HISTORY PANEL
   ════════════════════════════════ */
.hist-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0.5rem 0 1rem;
}
.hist-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 1.5rem;
}
.hist-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    transition: border-color 0.2s, background 0.2s;
}
.hist-card:hover {
    background: rgba(139,92,246,0.06);
    border-color: rgba(139,92,246,0.3);
}
.hist-topic {
    font-size: 0.87rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 0.3rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.hist-meta {
    font-size: 0.72rem;
    color: #475569;
    margin-bottom: 0.5rem;
}
.hist-pill {
    display: inline-block;
    padding: 2px 8px;
    background: rgba(139,92,246,0.1);
    border-radius: 999px;
    font-size: 0.7rem;
    color: #a78bfa;
}

/* ════════════════════════════════
   EMPTY STATE
   ════════════════════════════════ */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #2d2d5a;
}
.empty-state-icon { font-size: 3.5rem; margin-bottom: 1rem; opacity: 0.4; }
.empty-state-text { font-size: 0.95rem; font-weight: 500; color: #334155; }
.empty-state-sub  { font-size: 0.82rem; color: #1e293b; margin-top: 0.4rem; }

/* ════════════════════════════════
   RESULT META ROW
   ════════════════════════════════ */
.meta-row {
    display: flex;
    gap: 20px;
    align-items: center;
    flex-wrap: wrap;
    margin: 0.6rem 0 1.25rem;
}
.meta-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.8rem;
    color: #64748b;
}
.meta-icon { font-size: 0.85rem; }
.result-topic {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: #e2e8f0;
    margin: 1.5rem 0 0;
}
.section-divider {
    height: 1px;
    background: rgba(255,255,255,0.05);
    margin: 1.5rem 0;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "generating":    False,
    "script":        None,
    "research_data": None,
    "output_path":   None,
    "episode_meta":  None,
    "error":         None,
    "stage":         0,       # 0=idle 1=research 2=script 3=audio 4=done
    "tts_progress":  0,
    "tts_total":     0,
    "show_history":  False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run(coro):
    return asyncio.run(coro)

def _fmt_dur(s):
    m, sec = divmod(int(s or 0), 60)
    return f"{m}:{sec:02d}"

def _load_history():
    files = sorted(glob.glob(os.path.join(config.OUTPUT_DIR, "*.json")), reverse=True)
    out = []
    for f in files:
        try:
            out.append(json.load(open(f)))
        except Exception:
            pass
    return out

def _save_meta(meta):
    json_path = meta["mp3_path"].replace(".mp3", ".json")
    json.dump(meta, open(json_path, "w"), indent=2)

def _b64_audio(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ── Custom audio player component ─────────────────────────────────────────────

def render_player(mp3_path: str, meta: dict):
    """Render a fully custom-styled HTML5 audio player."""
    audio_b64 = _b64_audio(mp3_path)
    topic     = meta.get("topic", "Episode")
    dur_s     = meta.get("duration_s", 0)
    dur_str   = _fmt_dur(dur_s)
    turns     = meta.get("turns", "?")
    words     = f"{meta.get('words', 0):,}" if meta.get("words") else "—"

    html = f"""<!DOCTYPE html><html><head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: transparent;
    font-family: -apple-system, 'Inter', BlinkMacSystemFont, sans-serif;
    padding: 0;
  }}
  .player {{
    background: linear-gradient(135deg, #13112a 0%, #0d0d20 100%);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 18px;
    padding: 18px 20px 16px;
    box-shadow: 0 0 40px rgba(139,92,246,0.1);
  }}
  .player-top {{
    display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
  }}
  .player-art {{
    width: 46px; height: 46px; flex-shrink: 0;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 0 20px rgba(139,92,246,0.35);
  }}
  .player-info {{ flex: 1; min-width: 0; }}
  .player-title {{
    font-size: 13px; font-weight: 600; color: #e2e8f0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    margin-bottom: 3px;
  }}
  .player-meta {{ font-size: 11px; color: #475569; }}
  .player-meta span {{ margin-right: 10px; }}
  .controls {{
    display: flex; align-items: center; gap: 12px;
  }}
  .play-btn {{
    width: 40px; height: 40px; flex-shrink: 0;
    background: linear-gradient(135deg, #7c3aed, #8b5cf6);
    border: none; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    box-shadow: 0 0 20px rgba(139,92,246,0.4);
    transition: transform .12s, box-shadow .2s;
    outline: none;
  }}
  .play-btn:hover {{ transform: scale(1.08); box-shadow: 0 0 32px rgba(139,92,246,0.6); }}
  .play-btn:active {{ transform: scale(0.96); }}
  .play-btn svg {{ width: 15px; height: 15px; fill: #fff; margin-left: 2px; }}
  .play-btn.playing svg {{ margin-left: 0; }}
  .time {{ font-size: 11px; color: #64748b; flex-shrink: 0; width: 34px; }}
  .time.right {{ text-align: right; color: #334155; }}
  .track {{
    flex: 1; height: 4px;
    background: rgba(255,255,255,0.06);
    border-radius: 2px; cursor: pointer; position: relative;
    transition: height .15s;
  }}
  .track:hover {{ height: 6px; }}
  .track-fill {{
    height: 100%; width: 0%;
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    border-radius: 2px; pointer-events: none;
  }}
  .track-thumb {{
    position: absolute; top: 50%; transform: translateY(-50%);
    width: 12px; height: 12px;
    background: #a78bfa; border-radius: 50%;
    pointer-events: none; left: 0%;
    margin-left: -6px;
    opacity: 0; transition: opacity .15s;
    box-shadow: 0 0 8px rgba(139,92,246,0.6);
  }}
  .track:hover .track-thumb {{ opacity: 1; }}
  .vol {{ display: flex; align-items: center; gap: 6px; flex-shrink: 0; }}
  .vol-icon {{ font-size: 13px; cursor: pointer; color: #475569; user-select:none; }}
  .vol-range {{
    -webkit-appearance: none;
    width: 58px; height: 3px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px; outline: none; cursor: pointer;
  }}
  .vol-range::-webkit-slider-thumb {{
    -webkit-appearance: none;
    width: 10px; height: 10px;
    background: #8b5cf6; border-radius: 50%; cursor: pointer;
  }}
</style>
</head><body>
<div class="player">
  <div class="player-top">
    <div class="player-art">🎙️</div>
    <div class="player-info">
      <div class="player-title">{topic}</div>
      <div class="player-meta">
        <span>🎤 {turns} turns</span>
        <span>📝 {words} words</span>
        <span>⏱ {dur_str}</span>
      </div>
    </div>
  </div>
  <div class="controls">
    <button class="play-btn" id="playBtn" onclick="togglePlay()">
      <svg id="playIcon" viewBox="0 0 24 24"><path id="playPath" d="M8 5v14l11-7z"/></svg>
    </button>
    <span class="time" id="cur">0:00</span>
    <div class="track" id="track" onclick="seek(event)">
      <div class="track-fill" id="fill"></div>
      <div class="track-thumb" id="thumb"></div>
    </div>
    <span class="time right">{dur_str}</span>
    <div class="vol">
      <span class="vol-icon" onclick="toggleMute()">🔊</span>
      <input type="range" class="vol-range" min="0" max="1" step="0.02"
             value="1" oninput="audio.volume=this.value">
    </div>
  </div>
</div>
<audio id="audio" src="data:audio/mp3;base64,{audio_b64}"
       ontimeupdate="tick()" onended="ended()"></audio>
<script>
const audio = document.getElementById('audio');
const playBtn = document.getElementById('playBtn');
const playPath = document.getElementById('playPath');
const cur = document.getElementById('cur');
const fill = document.getElementById('fill');
const thumb = document.getElementById('thumb');
const PLAY = 'M8 5v14l11-7z';
const PAUSE = 'M6 19h4V5H6v14zm8-14v14h4V5h-4z';
function fmt(s) {{ return Math.floor(s/60)+':'+(Math.floor(s%60)+'').padStart(2,'0'); }}
function togglePlay() {{
  if (audio.paused) {{ audio.play(); playPath.setAttribute('d',PAUSE); playBtn.classList.add('playing'); }}
  else {{ audio.pause(); playPath.setAttribute('d',PLAY); playBtn.classList.remove('playing'); }}
}}
function tick() {{
  if (!audio.duration) return;
  const p = audio.currentTime / audio.duration;
  fill.style.width = (p*100) + '%';
  thumb.style.left = (p*100) + '%';
  cur.textContent = fmt(audio.currentTime);
}}
function seek(e) {{
  const r = e.currentTarget.getBoundingClientRect();
  audio.currentTime = ((e.clientX-r.left)/r.width) * audio.duration;
}}
function ended() {{ playPath.setAttribute('d',PLAY); playBtn.classList.remove('playing'); }}
function toggleMute() {{ audio.muted = !audio.muted; }}
</script>
</body></html>"""

    components.html(html, height=148)


# ── Stage cards renderer ───────────────────────────────────────────────────────

def render_stages(active: int, tts_done: int = 0, tts_total: int = 0):
    """
    Render the three stage cards.
    active: 1=research, 2=script, 3=audio, 4=all done
    """
    def card(n, icon, name, desc):
        if active > n:
            status, pill = "done",    "done",
        elif active == n:
            status, pill = "active",  "active"
        else:
            status, pill = "",        "waiting"

        pill_labels = {"done": "✓ Complete", "active": "● In progress", "waiting": "○ Waiting"}
        pill_label  = pill_labels[pill]

        # inner progress bar only on audio card when active
        prog_html = ""
        if n == 3 and active == 3 and tts_total > 0:
            pct = int((tts_done / tts_total) * 100)
            prog_html = f"""
            <div class="stage-progress">
              <div class="stage-progress-fill" style="width:{pct}%"></div>
            </div>"""

        return f"""
        <div class="stage-card {status}">
          <span class="stage-icon">{icon}</span>
          <div class="stage-name">{name}</div>
          <div class="stage-desc">{desc}</div>
          <span class="stage-pill {pill}">{pill_label}</span>
          {prog_html}
        </div>"""

    html = f"""
    <div class="stages-wrap">
      {card(1, "🔍", "Research",  "Searching &amp; scraping the web")}
      {card(2, "✍️", "Script",    "Writing with Gemini AI")}
      {card(3, "🎵", "Audio",     "Synthesising voices")}
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


# ── Pipeline ───────────────────────────────────────────────────────────────────

def run_pipeline(topic: str, stage_slot, progress_slot, status_slot):
    from research.scraper import search_and_scrape
    from script.writer    import generate_script
    from audio.tts        import synthesise_turn
    from audio.assembler  import assemble_episode

    voice_map = {config.HOST_A_NAME: config.HOST_A_VOICE,
                 config.HOST_B_NAME: config.HOST_B_VOICE}

    # Stage 1 — Research
    st.session_state.stage = 1
    stage_slot.empty()
    with stage_slot:
        render_stages(1)
    status_slot.markdown(
        '<p style="text-align:center;color:#64748b;font-size:0.85rem;">'
        '🔍 Searching the web…</p>', unsafe_allow_html=True)
    progress_slot.progress(5)

    research_data = _run(search_and_scrape(topic))
    n_sources = len(research_data.get("sources", []))
    n_scraped = len(research_data.get("content", []))

    # Stage 2 — Script
    st.session_state.stage = 2
    with stage_slot:
        render_stages(2)
    status_slot.markdown(
        '<p style="text-align:center;color:#64748b;font-size:0.85rem;">'
        f'✅ Found {n_sources} sources · ✍️ Writing script with Gemini…</p>',
        unsafe_allow_html=True)
    progress_slot.progress(35)

    script  = _run(generate_script(research_data))
    n_turns = len(script)
    n_words = sum(len(t["line"].split()) for t in script)

    # Stage 3 — Audio
    st.session_state.stage = 3
    os.makedirs(config.TEMP_DIR,   exist_ok=True)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    for old in glob.glob(os.path.join(config.TEMP_DIR, "turn_*.mp3")):
        os.remove(old)

    segment_paths = []

    for i, turn in enumerate(script):
        host  = turn["host"]
        voice = voice_map[host]
        path  = os.path.join(config.TEMP_DIR, f"turn_{i:03d}_{host.lower()}.mp3")

        with stage_slot:
            render_stages(3, tts_done=i, tts_total=n_turns)

        pct = 65 + int((i / n_turns) * 30)
        progress_slot.progress(pct)
        status_slot.markdown(
            f'<p style="text-align:center;color:#64748b;font-size:0.85rem;">'
            f'🎙️ Synthesising voice: <strong style="color:#a78bfa">{host}</strong> '
            f'— turn {i+1} / {n_turns}</p>',
            unsafe_allow_html=True)

        _run(synthesise_turn(turn["line"], voice, path))
        segment_paths.append(path)

    # Assemble
    status_slot.markdown(
        '<p style="text-align:center;color:#64748b;font-size:0.85rem;">'
        '🎵 Assembling final MP3…</p>', unsafe_allow_html=True)
    progress_slot.progress(97)

    output_path = assemble_episode(segment_paths)

    from pydub import AudioSegment as _AS
    audio   = _AS.from_mp3(output_path)
    dur_s   = len(audio) / 1000
    size_mb = os.path.getsize(output_path) / (1024 * 1024)

    st.session_state.stage = 4
    with stage_slot:
        render_stages(4)
    progress_slot.progress(100)
    status_slot.empty()

    meta = {
        "topic": topic, "timestamp": datetime.now().isoformat(),
        "turns": n_turns, "words": n_words,
        "duration_s": round(dur_s, 1), "size_mb": round(size_mb, 2),
        "mp3_path": output_path,
        "sources": [s["url"] for s in research_data.get("sources", [])],
    }
    _save_meta(meta)
    return script, research_data, output_path, meta


# ══════════════════════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════════════════════

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pp-hero">
  <div class="pp-logo">
    <div class="pp-logo-icon">🎙️</div>
    <span class="pp-logo-name">Parsepod</span>
  </div>
  <h1 class="pp-hero-title">Turn any topic into<br>a podcast episode</h1>
  <p class="pp-hero-sub">
    AI researches the web, writes a two-host script, and produces a full MP3 — in minutes.
  </p>
  <div class="pp-hero-badges">
    <span class="pp-badge">🔍 Tavily Search</span>
    <span class="pp-badge">✨ Gemini AI</span>
    <span class="pp-badge">🗣️ Edge TTS</span>
    <span class="pp-badge">🎵 MP3 Output</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Input card ─────────────────────────────────────────────────────────────────
st.markdown('<div class="pp-input-card">', unsafe_allow_html=True)
st.markdown('<div class="pp-input-label">What should the episode be about?</div>',
            unsafe_allow_html=True)

topic = st.text_input(
    "topic", label_visibility="collapsed",
    placeholder='e.g. "the rise of open source AI models"',
    disabled=st.session_state.generating,
)

generate_clicked = st.button(
    "✦ Generate Episode",
    type="primary",
    use_container_width=True,
    disabled=st.session_state.generating or not (topic or "").strip(),
)
st.markdown('</div>', unsafe_allow_html=True)

# ── Pipeline execution ─────────────────────────────────────────────────────────
if generate_clicked and topic.strip():
    for k in ("script", "research_data", "output_path", "episode_meta", "error"):
        st.session_state[k] = None
    st.session_state.generating   = True
    st.session_state.show_history = False

    stage_slot    = st.empty()
    progress_slot = st.progress(0)
    status_slot   = st.empty()

    try:
        config.validate()
        script, rd, out, meta = run_pipeline(
            topic.strip(), stage_slot, progress_slot, status_slot
        )
        st.session_state.script        = script
        st.session_state.research_data = rd
        st.session_state.output_path   = out
        st.session_state.episode_meta  = meta
    except Exception as exc:
        st.session_state.error = str(exc)
    finally:
        st.session_state.generating = False

    st.rerun()

# ── Error ──────────────────────────────────────────────────────────────────────
if st.session_state.error:
    st.markdown(f"""
    <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                border-radius:12px;padding:1rem 1.25rem;color:#fca5a5;font-size:0.88rem;">
      ⚠️ {st.session_state.error}
    </div>""", unsafe_allow_html=True)

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.output_path and os.path.exists(st.session_state.output_path):
    meta = st.session_state.episode_meta or {}

    st.markdown(
        f'<p class="result-topic">{meta.get("topic","Episode")}</p>',
        unsafe_allow_html=True)

    ts_str = (datetime.fromisoformat(meta["timestamp"]).strftime("%B %d, %Y · %H:%M")
              if meta.get("timestamp") else "")
    st.markdown(f"""
    <div class="meta-row">
      <span class="meta-item"><span class="meta-icon">📅</span>{ts_str}</span>
      <span class="meta-item"><span class="meta-icon">⏱</span>{_fmt_dur(meta.get("duration_s",0))}</span>
      <span class="meta-item"><span class="meta-icon">🎤</span>{meta.get("turns","?")} turns</span>
      <span class="meta-item"><span class="meta-icon">📝</span>{meta.get("words",0):,} words</span>
      <span class="meta-item"><span class="meta-icon">💾</span>{meta.get("size_mb",0):.1f} MB</span>
    </div>
    """, unsafe_allow_html=True)

    render_player(st.session_state.output_path, meta)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Transcript
    if st.session_state.script:
        with st.expander("📜  Transcript", expanded=False):
            turns_html = '<div class="transcript-wrap">'
            for turn in st.session_state.script:
                host = turn["host"]
                line = turn["line"]
                is_ryan    = host == config.HOST_A_NAME
                av_cls     = "ryan-avatar"  if is_ryan else "jenny-avatar"
                bub_cls    = "ryan-bubble"  if is_ryan else "jenny-bubble"
                lbl_cls    = "ryan-label"   if is_ryan else "jenny-label"
                initials   = host[:2].upper()
                turns_html += f"""
                <div class="turn">
                  <div class="turn-avatar {av_cls}">{initials}</div>
                  <div class="turn-bubble {bub_cls}">
                    <div class="turn-label {lbl_cls}">{host}</div>
                    {line}
                  </div>
                </div>"""
            turns_html += '</div>'
            st.markdown(turns_html, unsafe_allow_html=True)
    else:
        with st.expander("📜  Transcript", expanded=False):
            st.caption("Transcript not available for episodes loaded from history.")

    # Research brief
    sources = (
        (st.session_state.research_data or {}).get("sources", [])
        or [{"url": u, "title": u, "snippet": "", "score": 0}
            for u in meta.get("sources", [])]
    )
    if sources:
        with st.expander("🔍  Research Brief", expanded=False):
            for src in sources:
                score_pct = int((src.get("score") or 0) * 100)
                title = src.get("title") or src.get("url", "")
                st.markdown(
                    f'<div style="font-size:0.88rem;font-weight:600;color:#e2e8f0;'
                    f'margin-bottom:4px;">{title}</div>',
                    unsafe_allow_html=True)
                if src.get("snippet"):
                    st.markdown(
                        f'<div style="font-size:0.82rem;color:#64748b;margin-bottom:6px;'
                        f'line-height:1.5">{src["snippet"]}</div>',
                        unsafe_allow_html=True)
                c1, c2 = st.columns([5, 1])
                c1.markdown(
                    f"<a href='{src['url']}' target='_blank' "
                    f"style='font-size:0.78rem;color:#8b5cf6;text-decoration:none;'>"
                    f"↗ {src['url']}</a>",
                    unsafe_allow_html=True)
                if score_pct:
                    c2.markdown(
                        f"<div style='font-size:0.72rem;color:#475569;text-align:right;"
                        f"padding-top:2px'>{score_pct}% match</div>",
                        unsafe_allow_html=True)
                st.markdown(
                    '<div style="height:1px;background:rgba(255,255,255,0.04);'
                    'margin:10px 0"></div>', unsafe_allow_html=True)

# ── Empty state ────────────────────────────────────────────────────────────────
elif not st.session_state.generating and not st.session_state.error:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-state-icon">🎙️</div>
      <div class="empty-state-text">Your episode will appear here</div>
      <div class="empty-state-sub">
        Enter a topic above — Parsepod handles the rest.
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── History section ────────────────────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

hist_col1, hist_col2 = st.columns([4, 1])
with hist_col1:
    st.markdown(
        '<p style="font-size:0.88rem;font-weight:600;color:#334155;margin:0">'
        'Episode History</p>',
        unsafe_allow_html=True)
with hist_col2:
    toggle_label = "▲ Hide" if st.session_state.show_history else "▼ Show"
    if st.button(toggle_label, key="hist_toggle", use_container_width=True):
        st.session_state.show_history = not st.session_state.show_history
        st.rerun()

if st.session_state.show_history:
    history = _load_history()
    if not history:
        st.markdown(
            '<p style="text-align:center;color:#334155;font-size:0.85rem;padding:1.5rem 0">'
            'No episodes yet.</p>', unsafe_allow_html=True)
    else:
        # Render in a 2-column grid using Streamlit columns
        pairs = [history[i:i+2] for i in range(0, len(history), 2)]
        for pair in pairs:
            cols = st.columns(2)
            for col, ep in zip(cols, pair):
                with col:
                    ts = datetime.fromisoformat(ep["timestamp"])
                    st.markdown(f"""
                    <div class="hist-card">
                      <div class="hist-topic">{ep['topic']}</div>
                      <div class="hist-meta">
                        {ts.strftime('%b %d, %Y')} ·
                        {_fmt_dur(ep.get('duration_s',0))} ·
                        {ep.get('turns','?')} turns
                      </div>
                      <span class="hist-pill">{ep.get('size_mb',0):.1f} MB</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Load episode", key=f"load_{ep['timestamp']}",
                                 use_container_width=True):
                        st.session_state.output_path   = ep["mp3_path"]
                        st.session_state.episode_meta  = ep
                        st.session_state.script        = None
                        st.session_state.research_data = None
                        st.session_state.show_history  = False
                        st.rerun()
