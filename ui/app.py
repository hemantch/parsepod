"""
ui/app.py — Parsepod · world-class dark UI inspired by Perplexity + Apple.

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
    page_title="Parsepod",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300&display=swap');

/* ─── Reset ─────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ─── Full black canvas ──────────────────────────────────────────────────── */
.stApp, .stApp > * {
    background: #0a0a0a !important;
}

/* ─── Kill all Streamlit chrome ──────────────────────────────────────────── */
#MainMenu, footer, header,
.stDeployButton, .stDecoration,
[data-testid="collapsedControl"],
[data-testid="stToolbar"],
[data-testid="manage-app-button"],
section[data-testid="stSidebar"] { display: none !important; }

/* ─── Main content container ─────────────────────────────────────────────── */
.main .block-container {
    max-width: 680px !important;
    padding: 0 1.5rem 6rem !important;
    margin: 0 auto !important;
}

/* ─── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 2px; }

/* ════════════════════════════════════════════════════════════════════════════
   HERO
   ════════════════════════════════════════════════════════════════════════════ */
.hero {
    padding: 5rem 0 3.5rem;
    text-align: center;
    animation: heroFadeUp 0.7s cubic-bezier(0.16,1,0.3,1) both;
}
.hero-wordmark {
    display: inline-flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 1.75rem;
}
.hero-dot {
    width: 8px; height: 8px;
    background: #fff;
    border-radius: 50%;
    animation: dotPulse 3s ease-in-out infinite;
}
.hero-name {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #555;
}
.hero-title {
    font-size: clamp(2.6rem, 6vw, 3.4rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.08;
    color: #fff;
    margin-bottom: 1rem;
}
.hero-sub {
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.06em;
    color: #444;
    text-transform: uppercase;
}

/* ════════════════════════════════════════════════════════════════════════════
   SEARCH BAR  (form + input + button fused into one pill)
   ════════════════════════════════════════════════════════════════════════════ */

/* Wrapper div we inject around the form */
.search-wrap {
    position: relative;
    width: 100%;
    animation: heroFadeUp 0.7s 0.12s cubic-bezier(0.16,1,0.3,1) both;
}

/* The form itself becomes the pill */
[data-testid="stForm"] {
    background: #111 !important;
    border: 1px solid #1c1c1c !important;
    border-radius: 50px !important;
    display: flex !important;
    align-items: center !important;
    padding: 6px 6px 6px 22px !important;
    gap: 0 !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
    box-shadow: none !important;
}
[data-testid="stForm"]:focus-within {
    border-color: rgba(255,255,255,0.12) !important;
    box-shadow: 0 0 0 4px rgba(255,255,255,0.04),
                0 8px 40px rgba(0,0,0,0.6) !important;
}

/* Input inside the form */
[data-testid="stForm"] .stTextInput {
    flex: 1 !important;
    min-width: 0 !important;
}
[data-testid="stForm"] .stTextInput > div,
[data-testid="stForm"] .stTextInput > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
[data-testid="stForm"] .stTextInput input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.975rem !important;
    font-weight: 400 !important;
    padding: 0.55rem 0 !important;
    caret-color: #fff;
}
[data-testid="stForm"] .stTextInput input::placeholder {
    color: #333 !important;
    font-weight: 300 !important;
}
[data-testid="stForm"] .stTextInput input:focus {
    outline: none !important;
    box-shadow: none !important;
}

/* Submit button — white circle */
[data-testid="stFormSubmitButton"] {
    flex-shrink: 0 !important;
}
[data-testid="stFormSubmitButton"] button {
    width: 38px !important;
    height: 38px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: #fff !important;
    border: none !important;
    color: #000 !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: background 0.15s, transform 0.12s !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    animation: btnPulse 3s ease-in-out infinite !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: #e8e8e8 !important;
    transform: scale(1.06) !important;
    animation: none !important;
}
[data-testid="stFormSubmitButton"] button:active {
    transform: scale(0.95) !important;
}
[data-testid="stFormSubmitButton"] button:disabled {
    background: #1a1a1a !important;
    color: #333 !important;
    animation: none !important;
    cursor: not-allowed !important;
}
/* Remove default focus ring Streamlit adds */
[data-testid="stFormSubmitButton"] button:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* ════════════════════════════════════════════════════════════════════════════
   PROGRESS STAGES
   ════════════════════════════════════════════════════════════════════════════ */
.stages {
    display: flex;
    flex-direction: column;
    gap: 1px;
    margin: 2rem 0;
}
.stage-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 0;
    border-bottom: 1px solid #111;
    animation: stageFadeIn 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
.stage-row:last-child { border-bottom: none; }
.stage-row:nth-child(1) { animation-delay: 0.05s; }
.stage-row:nth-child(2) { animation-delay: 0.18s; }
.stage-row:nth-child(3) { animation-delay: 0.31s; }

.stage-icon {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    flex-shrink: 0;
}
.stage-icon.waiting  { background: #111; color: #333; border: 1px solid #1c1c1c; }
.stage-icon.active   { background: #fff; color: #000; }
.stage-icon.done     { background: #1a1a1a; color: #fff; border: 1px solid #222; }

.stage-body { flex: 1; min-width: 0; }
.stage-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #fff;
    margin-bottom: 1px;
}
.stage-label.muted { color: #333; }
.stage-detail {
    font-size: 0.75rem;
    color: #444;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.stage-status {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    flex-shrink: 0;
}
.stage-status.waiting { color: #2a2a2a; }
.stage-status.active  { color: #fff; }
.stage-status.done    { color: #3a3a3a; }

/* Spinning indicator for active stage */
.stage-spinner {
    width: 14px; height: 14px;
    border: 1.5px solid #222;
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    flex-shrink: 0;
}

/* TTS sub-progress */
.tts-bar-wrap {
    height: 1px;
    background: #111;
    border-radius: 1px;
    margin-top: 8px;
    overflow: hidden;
}
.tts-bar-fill {
    height: 100%;
    background: #fff;
    border-radius: 1px;
    transition: width 0.3s ease;
}

/* ════════════════════════════════════════════════════════════════════════════
   AUDIO PLAYER
   ════════════════════════════════════════════════════════════════════════════ */
/* The player is rendered as a custom HTML component — no CSS needed here.    */
/* Its wrapper animates in when inserted into the DOM.                        */
.player-reveal {
    animation: slideUp 0.5s cubic-bezier(0.16,1,0.3,1) both;
}

/* ════════════════════════════════════════════════════════════════════════════
   EPISODE HEADER (shown above player)
   ════════════════════════════════════════════════════════════════════════════ */
.ep-header {
    margin: 2.5rem 0 1rem;
    animation: stageFadeIn 0.4s ease both;
}
.ep-topic {
    font-size: 1.3rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #fff;
    margin-bottom: 0.4rem;
}
.ep-meta {
    font-size: 0.78rem;
    color: #333;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

/* ════════════════════════════════════════════════════════════════════════════
   EXPANDERS (transcript + research)
   ════════════════════════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: transparent !important;
    border: none !important;
    border-top: 1px solid #111 !important;
    border-radius: 0 !important;
    color: #333 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    padding: 1rem 0 !important;
    transition: color 0.15s !important;
}
.streamlit-expanderHeader:hover { color: #888 !important; }
.streamlit-expanderHeader svg { color: #222 !important; }
.streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 1.5rem !important;
}

/* ════════════════════════════════════════════════════════════════════════════
   TRANSCRIPT TURNS
   ════════════════════════════════════════════════════════════════════════════ */
.turns { display: flex; flex-direction: column; gap: 0; }
.turn {
    display: flex;
    gap: 14px;
    padding: 1rem 0;
    border-bottom: 1px solid #0f0f0f;
    align-items: flex-start;
}
.turn:last-child { border-bottom: none; }
.turn-init {
    width: 26px; height: 26px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    flex-shrink: 0;
    margin-top: 2px;
}
.ryan-init  { background: #111; color: #4a9eff; border: 1px solid #1a2a3a; }
.jenny-init { background: #111; color: #ff9144; border: 1px solid #2a1a0a; }
.turn-text  { flex: 1; }
.turn-name  {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 5px;
}
.ryan-name  { color: #4a9eff; }
.jenny-name { color: #ff9144; }
.turn-line  {
    font-size: 0.875rem;
    line-height: 1.65;
    color: #666;
    font-weight: 300;
}

/* ════════════════════════════════════════════════════════════════════════════
   RESEARCH SOURCES
   ════════════════════════════════════════════════════════════════════════════ */
.source-item {
    padding: 0.85rem 0;
    border-bottom: 1px solid #0f0f0f;
}
.source-item:last-child { border-bottom: none; }
.source-title {
    font-size: 0.85rem;
    font-weight: 500;
    color: #555;
    margin-bottom: 3px;
}
.source-snippet {
    font-size: 0.78rem;
    color: #2a2a2a;
    line-height: 1.5;
    margin-bottom: 5px;
}
.source-url {
    font-size: 0.72rem;
    color: #333;
    text-decoration: none;
}
.source-url:hover { color: #666; }

/* ════════════════════════════════════════════════════════════════════════════
   RECENT EPISODES
   ════════════════════════════════════════════════════════════════════════════ */
.recent-heading {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #222;
    margin-bottom: 0.75rem;
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid #0f0f0f;
}
.recent-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.7rem 0;
    border-bottom: 1px solid #0f0f0f;
    cursor: pointer;
    transition: all 0.15s;
}
.recent-item:last-child { border-bottom: none; }
.recent-topic {
    font-size: 0.85rem;
    color: #333;
    font-weight: 400;
    transition: color 0.15s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 420px;
}
.recent-dur {
    font-size: 0.72rem;
    color: #222;
    flex-shrink: 0;
    margin-left: 12px;
}

/* ════════════════════════════════════════════════════════════════════════════
   EMPTY STATE
   ════════════════════════════════════════════════════════════════════════════ */
.empty {
    text-align: center;
    padding: 3.5rem 0 2rem;
    animation: stageFadeIn 0.5s ease both;
}
.empty-ring {
    width: 56px; height: 56px;
    border: 1px solid #1a1a1a;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    margin: 0 auto 1.25rem;
    color: #222;
}
.empty-text { font-size: 0.875rem; color: #222; font-weight: 300; }

/* ════════════════════════════════════════════════════════════════════════════
   ERROR
   ════════════════════════════════════════════════════════════════════════════ */
.pp-error {
    border: 1px solid #2a1010;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    font-size: 0.82rem;
    color: #8b3333;
    background: #0f0808;
    margin: 1rem 0;
    line-height: 1.5;
}

/* ════════════════════════════════════════════════════════════════════════════
   LOAD BUTTON (recent episodes)
   ════════════════════════════════════════════════════════════════════════════ */
.stButton > button {
    background: transparent !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 6px !important;
    color: #333 !important;
    font-size: 0.75rem !important;
    font-weight: 400 !important;
    padding: 4px 14px !important;
    height: auto !important;
    transition: border-color 0.15s, color 0.15s !important;
    letter-spacing: 0.03em !important;
}
.stButton > button:hover {
    border-color: #333 !important;
    color: #888 !important;
    background: transparent !important;
}

/* ════════════════════════════════════════════════════════════════════════════
   KEYFRAMES
   ════════════════════════════════════════════════════════════════════════════ */
@keyframes heroFadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes stageFadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes spin {
    to { transform: rotate(360deg); }
}
@keyframes dotPulse {
    0%, 100% { opacity: 0.4; transform: scale(1); }
    50%       { opacity: 1;   transform: scale(1.3); }
}
@keyframes btnPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,255,255,0); }
    50%       { box-shadow: 0 0 0 6px rgba(255,255,255,0.05); }
}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "generating":    False,
    "script":        None,
    "research_data": None,
    "output_path":   None,
    "episode_meta":  None,
    "error":         None,
    "stage":         0,
}.items():
    st.session_state.setdefault(k, v)


# ── Helpers ────────────────────────────────────────────────────────────────────
def _run(coro):
    return asyncio.run(coro)

def _fmt(s):
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
    json.dump(meta, open(meta["mp3_path"].replace(".mp3", ".json"), "w"), indent=2)

def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ── Stage renderer ─────────────────────────────────────────────────────────────
def render_stages(active: int, detail: str = "", tts_done: int = 0, tts_total: int = 0):
    """active: 1=research 2=script 3=audio 4=done"""

    def row(n, icon_done, icon_active, icon_wait, label):
        if active > n:
            icon_cls, lbl_cls, status_cls, status = "done", "", "done", "✓"
            spinner = ""
        elif active == n:
            icon_cls, lbl_cls, status_cls, status = "active", "", "active", "Running"
            spinner = '<div class="stage-spinner"></div>'
        else:
            icon_cls, lbl_cls, status_cls, status = "waiting", "muted", "waiting", ""
            spinner = ""

        sub = ""
        if n == 3 and active == 3 and tts_total > 0:
            pct = int(tts_done / tts_total * 100)
            sub = f"""<div class="tts-bar-wrap">
                        <div class="tts-bar-fill" style="width:{pct}%"></div>
                      </div>"""

        detail_html = ""
        if active == n and detail:
            detail_html = f'<div class="stage-detail">{detail}</div>'

        icon = icon_done if active > n else (icon_active if active == n else icon_wait)

        return f"""
        <div class="stage-row">
          <div class="stage-icon {icon_cls}">{icon}</div>
          <div class="stage-body">
            <div class="stage-label {lbl_cls}">{label}</div>
            {detail_html}{sub}
          </div>
          {spinner}
          <div class="stage-status {status_cls}">{status}</div>
        </div>"""

    return f"""
    <div class="stages">
      {row(1, "✓", "↗", "↗", "Research")}
      {row(2, "✓", "✎", "✎", "Script")}
      {row(3, "✓", "◎", "◎", "Audio")}
    </div>"""


# ── Custom audio player ────────────────────────────────────────────────────────
def render_player(mp3_path: str, meta: dict):
    topic    = meta.get("topic", "Episode")
    dur_s    = meta.get("duration_s", 0)
    dur_str  = _fmt(dur_s)
    turns    = meta.get("turns", "?")
    words    = f"{meta.get('words', 0):,}" if meta.get("words") else "—"
    a64      = _b64(mp3_path)

    # Static waveform bar heights for decoration
    bars = [28,42,61,38,72,55,80,46,65,38,90,52,74,41,60,
            35,78,50,66,44,85,57,70,39,58,48,76,62,43,68]
    bar_html = "".join(
        f'<div class="wb" style="height:{h}%"></div>' for h in bars
    )

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#0a0a0a; font-family:-apple-system,'Inter',sans-serif; padding:1px 0; }}

  .player {{
    background: #0f0f0f;
    border: 1px solid #161616;
    border-radius: 14px;
    padding: 18px 20px 16px;
  }}
  .top {{
    display:flex; align-items:flex-start;
    justify-content:space-between;
    margin-bottom:14px; gap:12px;
  }}
  .info {{ flex:1; min-width:0; }}
  .title {{
    font-size:13px; font-weight:600; color:#e8e8e8;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    margin-bottom:4px; letter-spacing:-0.01em;
  }}
  .meta {{ font-size:11px; color:#2a2a2a; display:flex; gap:12px; }}
  .meta span {{ color:#2a2a2a; }}

  /* Waveform */
  .waveform {{
    display:flex; align-items:center; gap:2px;
    height:28px; flex-shrink:0;
  }}
  .wb {{
    width:2px; min-height:4px;
    background:#1c1c1c;
    border-radius:1px;
    transition: background 0.2s;
  }}
  .playing .wb {{
    animation: wavePulse 1.4s ease-in-out infinite;
  }}
  .wb:nth-child(odd)  {{ animation-delay:0s !important; }}
  .wb:nth-child(3n)   {{ animation-delay:0.2s !important; }}
  .wb:nth-child(5n)   {{ animation-delay:0.4s !important; }}
  @keyframes wavePulse {{
    0%,100% {{ background:#2a2a2a; transform:scaleY(0.5); }}
    50%      {{ background:#555;   transform:scaleY(1); }}
  }}

  /* Controls */
  .controls {{ display:flex; align-items:center; gap:12px; }}
  .play-btn {{
    width:36px; height:36px; flex-shrink:0;
    background:#fff; border:none; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    cursor:pointer; transition:background .12s, transform .1s;
    outline:none;
  }}
  .play-btn:hover  {{ background:#ddd; transform:scale(1.06); }}
  .play-btn:active {{ transform:scale(0.94); }}
  .play-btn svg {{ width:13px; height:13px; fill:#000; margin-left:2px; }}
  .play-btn.on svg {{ margin-left:0; }}

  .time {{ font-size:11px; color:#2a2a2a; flex-shrink:0; min-width:30px; }}
  .time.end {{ text-align:right; }}

  .track {{
    flex:1; height:2px; background:#161616;
    border-radius:1px; cursor:pointer; position:relative;
    transition:height .15s;
  }}
  .track:hover {{ height:3px; }}
  .fill {{
    height:100%; width:0%; background:#fff;
    border-radius:1px; pointer-events:none;
    transition: width .1s linear;
  }}

  .vol {{ display:flex; align-items:center; gap:6px; flex-shrink:0; }}
  .vol-icon {{ font-size:11px; color:#2a2a2a; cursor:pointer; user-select:none; }}
  .vol-range {{
    -webkit-appearance:none; width:52px; height:2px;
    background:#161616; border-radius:1px; outline:none; cursor:pointer;
  }}
  .vol-range::-webkit-slider-thumb {{
    -webkit-appearance:none; width:8px; height:8px;
    background:#fff; border-radius:50%; cursor:pointer;
  }}
</style>
</head><body>
<div class="player">
  <div class="top">
    <div class="info">
      <div class="title">{topic}</div>
      <div class="meta">
        <span>{turns} turns</span>
        <span>{words} words</span>
        <span>{dur_str}</span>
      </div>
    </div>
    <div class="waveform" id="wv">{bar_html}</div>
  </div>
  <div class="controls">
    <button class="play-btn" id="pb" onclick="toggle()">
      <svg id="pi" viewBox="0 0 24 24"><path id="pp" d="M8 5v14l11-7z"/></svg>
    </button>
    <span class="time" id="ct">0:00</span>
    <div class="track" id="tr" onclick="seek(event)">
      <div class="fill" id="fi"></div>
    </div>
    <span class="time end">{dur_str}</span>
    <div class="vol">
      <span class="vol-icon" onclick="mute()">♪</span>
      <input class="vol-range" type="range" min="0" max="1" step="0.02"
             value="1" oninput="au.volume=this.value">
    </div>
  </div>
</div>
<audio id="au" src="data:audio/mp3;base64,{a64}"
       ontimeupdate="tick()" onended="end()"></audio>
<script>
  const au=document.getElementById('au'),
        pb=document.getElementById('pb'),
        pp=document.getElementById('pp'),
        ct=document.getElementById('ct'),
        fi=document.getElementById('fi'),
        wv=document.getElementById('wv');
  const P='M8 5v14l11-7z', PA='M6 19h4V5H6v14zm8-14v14h4V5h-4z';
  function fmt(s){{return Math.floor(s/60)+':'+(Math.floor(s%60)+'').padStart(2,'0');}}
  function toggle(){{
    if(au.paused){{au.play();pp.setAttribute('d',PA);pb.classList.add('on');wv.classList.add('playing');}}
    else{{au.pause();pp.setAttribute('d',P);pb.classList.remove('on');wv.classList.remove('playing');}}
  }}
  function tick(){{
    if(!au.duration)return;
    const p=au.currentTime/au.duration;
    fi.style.width=(p*100)+'%';
    ct.textContent=fmt(au.currentTime);
  }}
  function seek(e){{
    const r=e.currentTarget.getBoundingClientRect();
    au.currentTime=((e.clientX-r.left)/r.width)*au.duration;
  }}
  function end(){{pp.setAttribute('d',P);pb.classList.remove('on');wv.classList.remove('playing');}}
  function mute(){{au.muted=!au.muted;}}
</script>
</body></html>"""

    st.markdown('<div class="player-reveal">', unsafe_allow_html=True)
    components.html(html, height=140)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Pipeline ───────────────────────────────────────────────────────────────────
def run_pipeline(topic: str, stage_slot):
    from research.scraper import search_and_scrape
    from script.writer    import generate_script
    from audio.tts        import synthesise_turn
    from audio.assembler  import assemble_episode

    voice_map = {config.HOST_A_NAME: config.HOST_A_VOICE,
                 config.HOST_B_NAME: config.HOST_B_VOICE}

    # ── Research ───────────────────────────────────────────────────────────────
    st.session_state.stage = 1
    stage_slot.markdown(render_stages(1, detail="Searching the web…"), unsafe_allow_html=True)

    research_data = _run(search_and_scrape(topic))
    n_sources = len(research_data.get("sources", []))

    # ── Script ─────────────────────────────────────────────────────────────────
    st.session_state.stage = 2
    stage_slot.markdown(render_stages(2, detail=f"Found {n_sources} sources · Writing with Groq…"), unsafe_allow_html=True)

    script  = _run(generate_script(research_data))
    n_turns = len(script)
    n_words = sum(len(t["line"].split()) for t in script)

    # ── Audio ──────────────────────────────────────────────────────────────────
    st.session_state.stage = 3
    os.makedirs(config.TEMP_DIR,   exist_ok=True)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    for old in glob.glob(os.path.join(config.TEMP_DIR, "turn_*.mp3")):
        os.remove(old)

    segment_paths = []
    for i, turn in enumerate(script):
        stage_slot.markdown(render_stages(3,
                detail=f"{turn['host']} · turn {i+1}/{n_turns}",
                tts_done=i, tts_total=n_turns), unsafe_allow_html=True)

        path = os.path.join(config.TEMP_DIR, f"turn_{i:03d}_{turn['host'].lower()}.mp3")
        _run(synthesise_turn(turn["line"], voice_map[turn["host"]], path))
        segment_paths.append(path)

    # ── Assemble ───────────────────────────────────────────────────────────────
    stage_slot.markdown(render_stages(3, detail="Assembling MP3…", tts_done=n_turns, tts_total=n_turns), unsafe_allow_html=True)

    output_path = assemble_episode(segment_paths)

    from pydub import AudioSegment as _AS
    dur_s   = len(_AS.from_mp3(output_path)) / 1000
    size_mb = os.path.getsize(output_path) / (1024 * 1024)

    st.session_state.stage = 4
    stage_slot.markdown(render_stages(4), unsafe_allow_html=True)

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
<div class="hero">
  <div class="hero-wordmark">
    <div class="hero-dot"></div>
    <span class="hero-name">Parsepod</span>
  </div>
  <h1 class="hero-title">Turn any topic<br>into a podcast</h1>
  <p class="hero-sub">Research · Script · Audio</p>
</div>
""", unsafe_allow_html=True)

# ── Search form ────────────────────────────────────────────────────────────────
with st.form("search", clear_on_submit=False):
    topic = st.text_input(
        "topic", label_visibility="collapsed",
        placeholder="Ask about any topic…",
        disabled=st.session_state.generating,
    )
    submitted = st.form_submit_button(
        "→",
        disabled=st.session_state.generating,
    )

# ── Trigger pipeline ───────────────────────────────────────────────────────────
if submitted and (topic or "").strip():
    for k in ("script", "research_data", "output_path", "episode_meta", "error"):
        st.session_state[k] = None
    st.session_state.generating = True

    stage_slot = st.empty()

    try:
        config.validate()
        script, rd, out, meta = run_pipeline(topic.strip(), stage_slot)
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
    st.markdown(
        f'<div class="pp-error">⚠ {st.session_state.error}</div>',
        unsafe_allow_html=True)

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.output_path and os.path.exists(st.session_state.output_path):
    meta = st.session_state.episode_meta or {}

    ts_str = (datetime.fromisoformat(meta["timestamp"]).strftime("%b %d, %Y · %H:%M")
              if meta.get("timestamp") else "")

    # Episode header
    st.markdown(f"""
    <div class="ep-header">
      <div class="ep-topic">{meta.get('topic','Episode')}</div>
      <div class="ep-meta">
        <span>{ts_str}</span>
        <span>{_fmt(meta.get('duration_s',0))}</span>
        <span>{meta.get('turns','?')} turns</span>
        <span>{meta.get('words',0):,} words</span>
        <span>{meta.get('size_mb',0):.1f} MB</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    render_player(st.session_state.output_path, meta)

    # Transcript
    with st.expander("Transcript"):
        if st.session_state.script:
            turns_html = '<div class="turns">'
            for turn in st.session_state.script:
                is_ryan   = turn["host"] == config.HOST_A_NAME
                init_cls  = "ryan-init"  if is_ryan else "jenny-init"
                name_cls  = "ryan-name"  if is_ryan else "jenny-name"
                initials  = turn["host"][:2].upper()
                turns_html += f"""
                <div class="turn">
                  <div class="turn-init {init_cls}">{initials}</div>
                  <div class="turn-text">
                    <div class="turn-name {name_cls}">{turn['host']}</div>
                    <div class="turn-line">{turn['line']}</div>
                  </div>
                </div>"""
            turns_html += '</div>'
            st.markdown(turns_html, unsafe_allow_html=True)
        else:
            st.markdown('<p class="empty-text">Transcript not available for loaded episodes.</p>',
                        unsafe_allow_html=True)

    # Research brief
    sources = (
        (st.session_state.research_data or {}).get("sources", [])
        or [{"url": u, "title": u, "snippet": "", "score": 0}
            for u in meta.get("sources", [])]
    )
    if sources:
        with st.expander("Sources"):
            html = '<div>'
            for src in sources:
                title   = src.get("title") or src.get("url", "")
                snippet = src.get("snippet", "")
                url     = src.get("url", "")
                snippet_html = f'<div class="source-snippet">{snippet}</div>' if snippet else ""
                html += f"""
                <div class="source-item">
                  <div class="source-title">{title}</div>
                  {snippet_html}
                  <a class="source-url" href="{url}" target="_blank">↗ {url}</a>
                </div>"""
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)

# ── Empty state ────────────────────────────────────────────────────────────────
elif not st.session_state.generating and not st.session_state.error:
    st.markdown("""
    <div class="empty">
      <div class="empty-ring">◎</div>
      <p class="empty-text">Your episode will appear here</p>
    </div>
    """, unsafe_allow_html=True)

# ── Recent episodes ────────────────────────────────────────────────────────────
history = _load_history()
if history:
    st.markdown('<div class="recent-heading">Recent Episodes</div>',
                unsafe_allow_html=True)

    for ep in history[:6]:
        col1, col2 = st.columns([1, 5], vertical_alignment="center")
        with col2:
            st.markdown(f"""
            <div class="recent-item">
              <span class="recent-topic">{ep['topic']}</span>
              <span class="recent-dur">{_fmt(ep.get('duration_s',0))}</span>
            </div>""", unsafe_allow_html=True)
        with col1:
            if st.button("Load", key=f"load_{ep['timestamp']}"):
                st.session_state.output_path   = ep["mp3_path"]
                st.session_state.episode_meta  = ep
                st.session_state.script        = None
                st.session_state.research_data = None
                st.rerun()
