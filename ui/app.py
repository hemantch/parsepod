"""
ui/app.py — Parsepod · Premium broadcast studio UI.

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
    page_title="Parsepod · AI Podcast Studio",
    page_icon="🎙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif !important; }

/* ── Canvas ─────────────────────────────────────────────────────────────── */
.stApp {
background:
  radial-gradient(ellipse 80% 50% at 50% 0%, rgba(168,85,247,0.1) 0%, transparent 55%),
  radial-gradient(ellipse 50% 40% at 85% 75%, rgba(34,211,238,0.06) 0%, transparent 60%),
  #0a0a0f !important;
}
.stApp > * { background: transparent !important; }

/* ── Kill chrome ─────────────────────────────────────────────────────────── */
#MainMenu, footer, header,
.stDeployButton, .stDecoration,
[data-testid="collapsedControl"],
[data-testid="stToolbar"],
[data-testid="manage-app-button"],
section[data-testid="stSidebar"] { display: none !important; }

/* ── Container ───────────────────────────────────────────────────────────── */
.main .block-container {
max-width: 1100px !important;
padding: 80px 2.5rem 6rem !important;
margin: 0 auto !important;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1e1b2e; border-radius: 2px; }

/* ════════════════════════════════════════════════════════════════════════════
   NAVBAR
   ════════════════════════════════════════════════════════════════════════════ */
.pp-nav {
position: fixed;
top: 0; left: 0; right: 0;
z-index: 9999;
height: 62px;
display: flex;
align-items: center;
justify-content: space-between;
padding: 0 2.5rem;
background: rgba(10,10,15,0.75);
backdrop-filter: blur(24px) saturate(160%);
-webkit-backdrop-filter: blur(24px) saturate(160%);
border-bottom: 1px solid rgba(255,255,255,0.05);
}
.pp-nav-logo {
display: flex;
align-items: center;
gap: 9px;
text-decoration: none;
}
.pp-nav-logo-icon {
width: 30px; height: 30px;
background: linear-gradient(135deg, #7c3aed, #a855f7);
border-radius: 8px;
display: flex;
align-items: center;
justify-content: center;
font-size: 0.9rem;
box-shadow: 0 0 16px rgba(168,85,247,0.45);
}
.pp-nav-logo-text {
font-size: 1.05rem;
font-weight: 800;
letter-spacing: -0.03em;
background: linear-gradient(135deg, #a855f7, #22d3ee);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
}
.pp-nav-links {
display: flex;
align-items: center;
gap: 2rem;
}
.pp-nav-link {
font-size: 0.82rem;
font-weight: 500;
color: #475569;
text-decoration: none;
transition: color 0.2s;
}
.pp-nav-link:hover { color: #94a3b8; }
.pp-nav-cta {
display: inline-flex;
align-items: center;
gap: 6px;
padding: 7px 18px;
background: linear-gradient(135deg, #7c3aed, #a855f7);
border-radius: 50px;
font-size: 0.8rem;
font-weight: 600;
color: #fff !important;
text-decoration: none;
box-shadow: 0 0 22px rgba(168,85,247,0.4);
transition: opacity 0.2s, transform 0.15s;
}
.pp-nav-cta:hover { opacity: 0.88; transform: translateY(-1px); }

/* ════════════════════════════════════════════════════════════════════════════
   HERO  (single centered column)
   ════════════════════════════════════════════════════════════════════════════ */
.pp-hero {
text-align: center;
padding: 4rem 0 1.5rem;
animation: fadeUp 0.7s cubic-bezier(0.16,1,0.3,1) both;
}
.pp-eyebrow {
display: inline-flex;
align-items: center;
gap: 7px;
background: rgba(168,85,247,0.1);
border: 1px solid rgba(168,85,247,0.22);
border-radius: 20px;
padding: 5px 14px;
font-size: 0.67rem;
font-weight: 700;
letter-spacing: 0.14em;
text-transform: uppercase;
color: #c084fc;
margin-bottom: 1.6rem;
}
.pp-eyebrow-dot {
width: 5px; height: 5px;
background: #a855f7;
border-radius: 50%;
animation: dotBlink 2s ease-in-out infinite;
}
.pp-h1 {
font-size: clamp(2.6rem, 5vw, 4.2rem);
font-weight: 900;
letter-spacing: -0.045em;
line-height: 1.04;
background: linear-gradient(140deg, #f8fafc 0%, #c084fc 45%, #22d3ee 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
margin-bottom: 1.2rem;
}
.pp-sub {
font-size: 1rem !important;
font-weight: 300 !important;
color: #475569 !important;
line-height: 1.75 !important;
width: 100% !important;
max-width: 520px !important;
margin: 0 auto 2.5rem !important;
text-align: center !important;
}
/* ── Centered input area ─────────────────────────────────────────────────── */
.pp-input-area {
max-width: 600px;
margin: 0 auto;
}
.pp-card-label {
font-size: 0.65rem !important;
font-weight: 700 !important;
letter-spacing: 0.12em !important;
text-transform: uppercase !important;
color: #334155 !important;
width: 100% !important;
max-width: 600px !important;
margin: 0 auto 0.65rem !important;
text-align: center !important;
display: block !important;
}
.pp-host-chips {
display: flex;
gap: 10px;
margin-top: 1rem;
flex-wrap: wrap;
justify-content: center;
}
.pp-host-chip {
display: flex;
align-items: center;
gap: 7px;
background: rgba(255,255,255,0.03);
border: 1px solid rgba(255,255,255,0.06);
border-radius: 20px;
padding: 5px 12px 5px 7px;
font-size: 0.73rem;
font-weight: 500;
color: #475569;
}
.pp-chip-avatar {
width: 20px; height: 20px;
border-radius: 50%;
display: flex;
align-items: center;
justify-content: center;
font-size: 0.5rem;
font-weight: 800;
letter-spacing: 0.04em;
}
.pp-chip-a { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.2); }
.pp-chip-b { background: rgba(249,115,22,0.12); color: #fb923c; border: 1px solid rgba(249,115,22,0.2); }
/* ── CTA row ─────────────────────────────────────────────────────────────── */
.pp-cta-row {
display: flex;
align-items: center;
justify-content: center;
gap: 1.25rem;
flex-wrap: wrap;
margin-top: 1.75rem;
margin-bottom: 2.5rem;
}
.pp-hero-btn {
display: inline-flex;
align-items: center;
gap: 8px;
padding: 13px 26px;
background: linear-gradient(135deg, #7c3aed, #a855f7);
border-radius: 50px;
font-size: 0.9rem;
font-weight: 700;
color: #fff;
text-decoration: none;
cursor: pointer;
box-shadow: 0 4px 24px rgba(168,85,247,0.45), 0 0 50px rgba(168,85,247,0.12);
transition: opacity 0.2s, transform 0.15s;
animation: btnPulse 3s ease-in-out infinite;
}
.pp-hero-btn:hover { opacity: 0.88; transform: translateY(-2px); animation: none; }
.pp-text-link {
font-size: 0.86rem;
font-weight: 500;
color: #334155;
text-decoration: none;
transition: color 0.2s;
}
.pp-text-link:hover { color: #64748b; }
/* ── Soundwave ───────────────────────────────────────────────────────────── */
.pp-soundwave {
display: flex;
align-items: center;
justify-content: center;
gap: 3px;
height: 26px;
margin: 0 auto;
}
.sw-bar {
width: 3px;
border-radius: 2px;
background: linear-gradient(180deg, rgba(168,85,247,0.65), rgba(34,211,238,0.4));
animation: swPulse 1.8s ease-in-out infinite;
transform-origin: bottom center;
}

/* ════════════════════════════════════════════════════════════════════════════
   FORM OVERRIDES
   ════════════════════════════════════════════════════════════════════════════ */
[data-testid="stForm"] {
max-width: 600px !important;
margin: 0 auto !important;
background: rgba(255,255,255,0.035) !important;
border: 1px solid rgba(255,255,255,0.08) !important;
border-radius: 50px !important;
display: flex !important;
align-items: center !important;
padding: 6px 6px 6px 18px !important;
gap: 0 !important;
transition: border-color 0.25s, box-shadow 0.25s !important;
box-shadow: none !important;
}
[data-testid="stForm"]:focus-within {
border-color: rgba(168,85,247,0.45) !important;
box-shadow: 0 0 0 3px rgba(168,85,247,0.09), 0 8px 40px rgba(168,85,247,0.1) !important;
}
[data-testid="stForm"] .stTextInput { flex: 1 !important; min-width: 0 !important; }
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
color: #e2e8f0 !important;
font-family: 'Inter', sans-serif !important;
font-size: 0.88rem !important;
font-weight: 400 !important;
padding: 0.45rem 0 !important;
caret-color: #a855f7;
}
[data-testid="stForm"] .stTextInput input::placeholder { color: #334155 !important; font-weight: 300 !important; }
[data-testid="stForm"] .stTextInput input:focus { outline: none !important; box-shadow: none !important; }
[data-testid="stFormSubmitButton"] { flex-shrink: 0 !important; }
[data-testid="stFormSubmitButton"] button {
height: 36px !important;
padding: 0 16px !important;
border-radius: 50px !important;
background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
border: none !important;
color: #fff !important;
font-size: 0.78rem !important;
font-weight: 600 !important;
letter-spacing: 0.03em !important;
cursor: pointer !important;
transition: opacity 0.15s, transform 0.12s !important;
box-shadow: 0 4px 18px rgba(168,85,247,0.35) !important;
animation: btnPulse 3s ease-in-out infinite !important;
}
[data-testid="stFormSubmitButton"] button:hover {
opacity: 0.9 !important;
transform: scale(1.03) !important;
animation: none !important;
}
[data-testid="stFormSubmitButton"] button:active { transform: scale(0.97) !important; }
[data-testid="stFormSubmitButton"] button:disabled {
background: #1e1b2e !important;
color: #334155 !important;
animation: none !important;
box-shadow: none !important;
cursor: not-allowed !important;
}
[data-testid="stFormSubmitButton"] button:focus { box-shadow: none !important; outline: none !important; }

/* ════════════════════════════════════════════════════════════════════════════
   TRUST BAR
   ════════════════════════════════════════════════════════════════════════════ */
.pp-trust {
display: flex;
align-items: center;
justify-content: center;
gap: 1.75rem;
flex-wrap: wrap;
padding: 2rem 0 1rem;
border-top: 1px solid rgba(255,255,255,0.04);
margin-top: 1rem;
}
.pp-trust-label {
font-size: 0.65rem;
font-weight: 700;
letter-spacing: 0.14em;
text-transform: uppercase;
color: #1e293b;
margin-right: 0.5rem;
}
.pp-trust-item {
display: flex;
align-items: center;
gap: 6px;
font-size: 0.75rem;
font-weight: 500;
color: #1e293b;
letter-spacing: 0.02em;
}
.pp-trust-icon { font-size: 0.85rem; }
.pp-trust-sep { width: 1px; height: 12px; background: rgba(255,255,255,0.06); }

/* ════════════════════════════════════════════════════════════════════════════
   FEATURE GRID
   ════════════════════════════════════════════════════════════════════════════ */
.pp-section { padding: 4.5rem 0 2rem; }
.pp-section-eyebrow {
font-size: 0.65rem;
font-weight: 700;
letter-spacing: 0.16em;
text-transform: uppercase;
color: #a855f7;
text-align: center;
margin-bottom: 0.6rem;
}
.pp-section-title {
font-size: clamp(1.7rem, 2.8vw, 2.2rem);
font-weight: 800;
letter-spacing: -0.03em;
color: #f1f5f9;
text-align: center;
margin-bottom: 0.65rem;
line-height: 1.15;
}
.pp-section-sub {
font-size: 0.9rem;
color: #334155;
text-align: center;
font-weight: 300;
max-width: 480px;
margin: 0 auto 3rem;
line-height: 1.7;
}
.pp-features {
display: grid;
grid-template-columns: repeat(4, 1fr);
gap: 1.1rem;
}
.pp-feat-card {
background: rgba(255,255,255,0.018);
border: 1px solid rgba(255,255,255,0.055);
border-radius: 18px;
padding: 26px 20px;
transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
position: relative;
overflow: hidden;
}
.pp-feat-card::after {
content: '';
position: absolute;
top: 0; left: 0; right: 0;
height: 1px;
background: linear-gradient(90deg, transparent, rgba(168,85,247,0.35), transparent);
opacity: 0;
transition: opacity 0.25s;
}
.pp-feat-card:hover {
border-color: rgba(168,85,247,0.2);
transform: translateY(-4px);
box-shadow: 0 20px 50px rgba(0,0,0,0.45), 0 0 30px rgba(168,85,247,0.07);
}
.pp-feat-card:hover::after { opacity: 1; }
.pp-feat-icon {
width: 42px; height: 42px;
background: rgba(168,85,247,0.1);
border: 1px solid rgba(168,85,247,0.14);
border-radius: 11px;
display: flex;
align-items: center;
justify-content: center;
font-size: 1.15rem;
margin-bottom: 1rem;
}
.pp-feat-title {
font-size: 0.95rem;
font-weight: 700;
color: #e2e8f0;
letter-spacing: -0.02em;
margin-bottom: 0.45rem;
}
.pp-feat-desc {
font-size: 0.8rem;
color: #334155;
line-height: 1.65;
font-weight: 300;
}

/* ════════════════════════════════════════════════════════════════════════════
   HOW IT WORKS — Vertical timeline
   ════════════════════════════════════════════════════════════════════════════ */
.pp-timeline {
max-width: 640px;
margin: 0 auto;
position: relative;
padding-left: 0;
}
.pp-timeline::before {
content: '';
position: absolute;
left: 22px; top: 8px; bottom: 8px;
width: 1px;
background: linear-gradient(180deg, rgba(168,85,247,0.4) 0%, rgba(34,211,238,0.25) 60%, transparent 100%);
}
.pp-step {
display: flex;
gap: 1.5rem;
padding-bottom: 2.25rem;
position: relative;
animation: fadeUp 0.6s ease both;
}
.pp-step:last-child { padding-bottom: 0; }
.pp-step-num {
width: 44px; height: 44px;
flex-shrink: 0;
border-radius: 50%;
background: rgba(168,85,247,0.08);
border: 1px solid rgba(168,85,247,0.22);
display: flex;
align-items: center;
justify-content: center;
font-size: 0.82rem;
font-weight: 800;
color: #a855f7;
box-shadow: 0 0 18px rgba(168,85,247,0.18);
position: relative;
z-index: 1;
}
.pp-step-body { padding-top: 9px; }
.pp-step-title {
font-size: 0.95rem;
font-weight: 700;
color: #e2e8f0;
letter-spacing: -0.02em;
margin-bottom: 0.3rem;
}
.pp-step-desc {
font-size: 0.82rem;
color: #334155;
line-height: 1.65;
font-weight: 300;
}

/* ════════════════════════════════════════════════════════════════════════════
   STUDIO PANEL  (loading state)
   ════════════════════════════════════════════════════════════════════════════ */
.studio-panel {
background: rgba(168,85,247,0.04);
border: 1px solid rgba(168,85,247,0.14);
border-radius: 20px;
padding: 24px;
margin: 2rem auto;
max-width: 680px;
backdrop-filter: blur(20px);
box-shadow: 0 0 60px rgba(168,85,247,0.08), 0 20px 60px rgba(0,0,0,0.5);
animation: panelIn 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
.on-air-row { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.rec-dot { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; flex-shrink: 0; animation: recPulse 1.1s ease-in-out infinite; }
.on-air-badge { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.18em; color: #ef4444; text-transform: uppercase; flex-shrink: 0; }
.studio-current { font-size: 0.82rem; color: #94a3b8; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tts-track { width: 100%; height: 2px; background: rgba(168,85,247,0.15); border-radius: 1px; margin-top: 12px; overflow: hidden; }
.tts-fill { height: 100%; background: linear-gradient(90deg, #7c3aed, #a855f7, #22d3ee); border-radius: 1px; transition: width 0.4s ease; }
.host-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.host-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 16px 14px; display: flex; flex-direction: column; align-items: center; gap: 8px; transition: all 0.35s cubic-bezier(0.16,1,0.3,1); }
.host-card.active { background: rgba(168,85,247,0.08); border-color: rgba(168,85,247,0.3); box-shadow: 0 0 30px rgba(168,85,247,0.12); }
.host-card.done { background: rgba(34,197,94,0.03); border-color: rgba(34,197,94,0.12); }
.host-card.scripting { background: rgba(34,211,238,0.04); border-color: rgba(34,211,238,0.15); }
.host-avatar { width: 46px; height: 46px; border-radius: 50%; background: linear-gradient(135deg, #1e1b4b, #2e1065); border: 2px solid rgba(168,85,247,0.2); display: flex; align-items: center; justify-content: center; font-size: 0.78rem; font-weight: 700; color: #a855f7; letter-spacing: 0.04em; transition: border-color 0.35s; }
.host-card.active .host-avatar { border-color: #a855f7; box-shadow: 0 0 20px rgba(168,85,247,0.3); animation: avatarGlow 2s ease-in-out infinite; }
.host-card.done .host-avatar { background: linear-gradient(135deg, #14532d, #166534); border-color: rgba(34,197,94,0.4); color: #4ade80; }
.host-card.scripting .host-avatar { border-color: rgba(34,211,238,0.4); color: #22d3ee; }
.host-name { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #475569; transition: color 0.35s; }
.host-card.active .host-name { color: #c084fc; }
.host-card.done .host-name { color: #4ade80; }
.host-card.scripting .host-name { color: #67e8f9; }
.host-status { font-size: 0.65rem; color: #334155; letter-spacing: 0.05em; }
.host-card.active .host-status { color: #a855f7; }
.host-card.done .host-status { color: #22c55e; }
.host-card.scripting .host-status { color: #22d3ee; }
.eq-bars { display: flex; align-items: flex-end; gap: 2px; height: 18px; }
.eq-bar { width: 3px; border-radius: 1.5px; background: #1e293b; min-height: 3px; transition: background 0.3s; }
.host-card.active .eq-bar { background: linear-gradient(180deg, #a855f7, #7c3aed); animation: eqBounce 0.7s ease-in-out infinite; }
.host-card.done .eq-bar { background: rgba(34,197,94,0.3); height: 3px !important; }
.host-card.scripting .eq-bar { background: linear-gradient(180deg, #22d3ee, #0891b2); animation: eqBounce 1.2s ease-in-out infinite; }
.studio-stages { display: flex; flex-direction: column; gap: 2px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 16px; }
.studio-stage { display: flex; align-items: center; gap: 10px; padding: 7px 0; font-size: 0.82rem; transition: all 0.25s; }
.stage-dot { width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 0.7rem; }
.studio-stage.waiting .stage-dot { background: #0f172a; border: 1px solid #1e293b; color: #334155; }
.studio-stage.active .stage-dot { background: rgba(168,85,247,0.2); border: 1px solid rgba(168,85,247,0.4); color: #a855f7; }
.studio-stage.done .stage-dot { background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; }
.stage-label-text { flex: 1; }
.studio-stage.waiting .stage-label-text { color: #334155; }
.studio-stage.active .stage-label-text { color: #e2e8f0; font-weight: 500; }
.studio-stage.done .stage-label-text { color: #475569; }
.stage-spin { width: 12px; height: 12px; border: 1.5px solid rgba(168,85,247,0.2); border-top-color: #a855f7; border-radius: 50%; animation: spin 0.8s linear infinite; flex-shrink: 0; }

/* ════════════════════════════════════════════════════════════════════════════
   EPISODE CARD + PLAYER WRAPPER
   ════════════════════════════════════════════════════════════════════════════ */
.pp-result-wrap { max-width: 680px; margin: 0 auto; }
.ep-card {
background: rgba(255,255,255,0.02);
border: 1px solid rgba(255,255,255,0.06);
border-radius: 18px;
padding: 22px 24px 18px;
margin: 2rem 0 1rem;
animation: panelIn 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
.ep-title { font-size: 1.2rem; font-weight: 700; letter-spacing: -0.025em; color: #f1f5f9; margin-bottom: 10px; line-height: 1.3; }
.ep-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.ep-badge { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); border-radius: 20px; padding: 3px 10px; font-size: 0.69rem; color: #64748b; letter-spacing: 0.02em; }

/* ── Download button ─────────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {
background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
border: none !important;
border-radius: 10px !important;
color: #fff !important;
font-size: 0.85rem !important;
font-weight: 600 !important;
padding: 10px 24px !important;
cursor: pointer !important;
box-shadow: 0 4px 20px rgba(168,85,247,0.3) !important;
transition: opacity 0.15s, transform 0.12s !important;
letter-spacing: 0.02em !important;
width: 100% !important;
}
[data-testid="stDownloadButton"] button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
[data-testid="stDownloadButton"] button:active { transform: translateY(0) !important; }

/* ── Expanders ───────────────────────────────────────────────────────────── */
.streamlit-expanderHeader { background: transparent !important; border: none !important; border-top: 1px solid rgba(255,255,255,0.05) !important; border-radius: 0 !important; color: #334155 !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; padding: 1rem 0 !important; transition: color 0.15s !important; }
.streamlit-expanderHeader:hover { color: #64748b !important; }
.streamlit-expanderHeader svg { color: #1e293b !important; }
.streamlit-expanderContent { background: transparent !important; border: none !important; padding: 0.5rem 0 1.5rem !important; }

/* ── Transcript ──────────────────────────────────────────────────────────── */
.turns { display: flex; flex-direction: column; }
.turn { display: flex; gap: 14px; padding: 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); align-items: flex-start; }
.turn:last-child { border-bottom: none; }
.turn-init { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.62rem; font-weight: 700; letter-spacing: 0.04em; flex-shrink: 0; margin-top: 1px; }
.ryan-init  { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.25); }
.jenny-init { background: rgba(249,115,22,0.12); color: #fb923c; border: 1px solid rgba(249,115,22,0.22); }
.turn-text { flex: 1; }
.turn-name { font-size: 0.66rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 5px; }
.ryan-name  { color: #818cf8; }
.jenny-name { color: #fb923c; }
.turn-line  { font-size: 0.875rem; line-height: 1.7; color: #475569; font-weight: 300; }

/* ── Sources ─────────────────────────────────────────────────────────────── */
.source-item { padding: 0.85rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.source-item:last-child { border-bottom: none; }
.source-title { font-size: 0.85rem; font-weight: 500; color: #475569; margin-bottom: 3px; }
.source-snippet { font-size: 0.78rem; color: #1e293b; line-height: 1.5; margin-bottom: 5px; }
.source-url { font-size: 0.72rem; color: #312e81; text-decoration: none; }
.source-url:hover { color: #a855f7; }

/* ── Generic stButton ────────────────────────────────────────────────────── */
.stButton > button { background: transparent !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 8px !important; color: #334155 !important; font-size: 0.74rem !important; padding: 4px 14px !important; height: auto !important; transition: border-color 0.15s, color 0.15s !important; }
.stButton > button:hover { border-color: rgba(168,85,247,0.3) !important; color: #a855f7 !important; background: rgba(168,85,247,0.04) !important; }

/* ════════════════════════════════════════════════════════════════════════════
   FAQ  (uses <details>/<summary> — no JS needed)
   ════════════════════════════════════════════════════════════════════════════ */
.pp-faq { max-width: 680px; margin: 0 auto; }
.pp-faq-item {
border-bottom: 1px solid rgba(255,255,255,0.05);
}
.pp-faq-item summary {
list-style: none;
padding: 1.2rem 0;
cursor: pointer;
display: flex;
align-items: center;
justify-content: space-between;
color: #64748b;
font-family: 'Inter', sans-serif;
font-size: 0.88rem;
font-weight: 600;
letter-spacing: -0.01em;
transition: color 0.2s;
gap: 1rem;
}
.pp-faq-item summary::-webkit-details-marker { display: none; }
.pp-faq-item summary::after {
content: '▾';
font-size: 0.75rem;
color: #1e293b;
flex-shrink: 0;
transition: transform 0.25s, color 0.2s;
}
.pp-faq-item[open] summary { color: #e2e8f0; }
.pp-faq-item[open] summary::after { transform: rotate(180deg); color: #a855f7; }
.pp-faq-item summary:hover { color: #94a3b8; }
.pp-faq-answer {
font-size: 0.83rem;
color: #334155;
line-height: 1.75;
font-weight: 300;
padding-bottom: 1.2rem;
font-family: 'Inter', sans-serif;
}

/* ════════════════════════════════════════════════════════════════════════════
   ERROR + EMPTY STATE
   ════════════════════════════════════════════════════════════════════════════ */
.pp-error { border: 1px solid rgba(239,68,68,0.2); border-radius: 12px; padding: 1rem 1.1rem; font-size: 0.84rem; color: #f87171; background: rgba(239,68,68,0.05); margin: 1rem auto; max-width: 680px; line-height: 1.6; }
.empty-state { text-align: center; padding: 3rem 0 2rem; animation: fadeUp 0.5s ease both; }
.empty-mic { width: 60px; height: 60px; background: rgba(168,85,247,0.07); border: 1px solid rgba(168,85,247,0.14); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin: 0 auto 1.1rem; }
.empty-text { font-size: 0.88rem; color: #1e293b; font-weight: 300; }
.empty-hint { font-size: 0.76rem; color: #0f172a; margin-top: 0.4rem; }

/* ── Recent episodes ─────────────────────────────────────────────────────── */
.recent-heading { font-size: 0.67rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #1e293b; margin-bottom: 0.75rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.04); max-width: 680px; margin-left: auto; margin-right: auto; }
.recent-item { display: flex; align-items: center; justify-content: space-between; padding: 0.65rem 0; border-bottom: 1px solid rgba(255,255,255,0.03); }
.recent-item:last-child { border-bottom: none; }
.recent-topic { font-size: 0.84rem; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 440px; }
.recent-dur { font-size: 0.7rem; color: #1e293b; flex-shrink: 0; margin-left: 12px; }

/* ════════════════════════════════════════════════════════════════════════════
   FOOTER
   ════════════════════════════════════════════════════════════════════════════ */
.pp-footer {
border-top: 1px solid rgba(255,255,255,0.04);
padding: 2.25rem 0;
display: flex;
align-items: center;
justify-content: space-between;
flex-wrap: wrap;
gap: 1rem;
margin-top: 5rem;
}
.pp-footer-left { display: flex; flex-direction: column; gap: 4px; }
.pp-footer-logo { display: flex; align-items: center; gap: 8px; text-decoration: none; }
.pp-footer-logo-icon { width: 24px; height: 24px; background: linear-gradient(135deg, #7c3aed, #a855f7); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; }
.pp-footer-logo-text { font-size: 0.85rem; font-weight: 700; color: #334155; letter-spacing: -0.02em; }
.pp-footer-tagline { font-size: 0.72rem; color: #1e293b; font-weight: 300; padding-left: 32px; }
.pp-footer-links { display: flex; gap: 1.25rem; align-items: center; }
.pp-footer-link { font-size: 0.73rem; color: #1e293b; text-decoration: none; transition: color 0.2s; }
.pp-footer-link:hover { color: #475569; }

/* ════════════════════════════════════════════════════════════════════════════
   DIVIDER
   ════════════════════════════════════════════════════════════════════════════ */
.pp-divider {
height: 1px;
background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
margin: 1rem 0;
}

/* ════════════════════════════════════════════════════════════════════════════
   KEYFRAMES
   ════════════════════════════════════════════════════════════════════════════ */
@keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
@keyframes panelIn { from { opacity: 0; transform: translateY(12px) scale(0.99); } to { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes glowFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-18px); } }
@keyframes swPulse { 0%, 100% { transform: scaleY(0.22); opacity: 0.45; } 50% { transform: scaleY(1); opacity: 1; } }
@keyframes recPulse { 0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(239,68,68,0.5); } 50% { opacity: 0.75; box-shadow: 0 0 0 5px rgba(239,68,68,0); } }
@keyframes eqBounce { 0%, 100% { transform: scaleY(0.25); } 50% { transform: scaleY(1); } }
@keyframes avatarGlow { 0%, 100% { box-shadow: 0 0 10px rgba(168,85,247,0.2); } 50% { box-shadow: 0 0 28px rgba(168,85,247,0.5); } }
@keyframes dotBlink { 0%, 100% { opacity: 0.35; } 50% { opacity: 1; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes btnPulse { 0%, 100% { box-shadow: 0 4px 20px rgba(168,85,247,0.35); } 50% { box-shadow: 0 4px 32px rgba(168,85,247,0.58); } }

/* ── Mobile ──────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
.pp-nav-links { display: none; }
.main .block-container { padding: 70px 1.25rem 4rem !important; }
.pp-features { grid-template-columns: repeat(2, 1fr) !important; }
.pp-footer { flex-direction: column; text-align: center; }
.pp-footer-tagline { padding-left: 0; }
}
@media (max-width: 480px) {
.pp-features { grid-template-columns: 1fr !important; }
}
</style>""", unsafe_allow_html=True)


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


# ── Studio panel (loading state) ───────────────────────────────────────────────
def render_studio(active: int, detail: str = "", tts_done: int = 0,
                  tts_total: int = 0, current_host: str = "", assembling: bool = False):
    """Render the animated On Air studio panel.

    active: 1=research  2=script  3=audio/tts  4=done
    current_host: name of host being recorded (stage 3)
    assembling: True when mixing final MP3 (still stage 3 in pipeline)
    """
    host_a = config.HOST_A_NAME
    host_b = config.HOST_B_NAME

    # ── Host card state ──────────────────────────────────────────────────────
    def host_cls(name):
        if active == 4:
            return "done"
        if assembling:
            return "done"
        if active == 3:
            return "active" if name == current_host else "waiting"
        if active == 2:
            return "scripting"
        return "waiting"

    def host_status_text(name):
        cls = host_cls(name)
        if cls == "active":
            return "Recording"
        if cls == "done":
            return "Done \u2713"
        if cls == "scripting":
            return "Scripting"
        return "Standby"

    eq_delays = [0, 0.10, 0.20, 0.15, 0.05, 0.25, 0.12]

    def eq_bars():
        return '<div class="eq-bars">' + ''.join(
            f'<div class="eq-bar" style="height:{h}px;animation-delay:{d}s"></div>'
            for h, d in zip([6,12,17,14,18,10,15], eq_delays)
        ) + '</div>'

    def host_card(name):
        init = name[:2].upper()
        cls = host_cls(name)
        status = host_status_text(name)
        return (
            f'<div class="host-card {cls}">'
            f'<div class="host-avatar">{init}</div>'
            f'<div class="host-name">{name}</div>'
            f'<div class="host-status">{status}</div>'
            + eq_bars() +
            '</div>'
        )

    # ── Stage rows ───────────────────────────────────────────────────────────
    if active == 4:
        studio_active = 5  # all done
    elif assembling:
        studio_active = 4  # mixing
    else:
        studio_active = active  # 1, 2, or 3

    stage_defs = [
        (1, "Researching the web"),
        (2, "Writing the script"),
        (3, "Recording voices"),
        (4, "Mixing audio"),
    ]

    def stage_row(n, label):
        if studio_active > n:
            cls, dot, extra = "done", "\u2713", ""
        elif studio_active == n:
            cls, dot, extra = "active", "\u25c9", '<div class="stage-spin"></div>'
        else:
            cls, dot, extra = "waiting", "\u25cb", ""
        return (
            f'<div class="studio-stage {cls}">'
            f'<div class="stage-dot">{dot}</div>'
            f'<span class="stage-label-text">{label}</span>'
            f'{extra}'
            f'</div>'
        )

    # ── Detail / current label ───────────────────────────────────────────────
    if detail:
        current_label = detail
    elif active == 1:
        current_label = "Searching the web\u2026"
    elif active == 2:
        current_label = "Writing with Groq\u2026"
    elif active == 3 and not assembling:
        current_label = f"Recording {current_host}\u2026" if current_host else "Recording\u2026"
    elif assembling:
        current_label = "Mixing final audio\u2026"
    elif active == 4:
        current_label = "Episode ready!"
    else:
        current_label = ""

    # ── TTS progress bar ─────────────────────────────────────────────────────
    tts_bar = ""
    if active == 3 and not assembling and tts_total > 0:
        pct = int(tts_done / tts_total * 100)
        tts_bar = f'<div class="tts-track"><div class="tts-fill" style="width:{pct}%"></div></div>'

    return (
        '<div class="studio-panel">'
        '<div class="on-air-row">'
        '<div class="rec-dot"></div>'
        '<span class="on-air-badge">ON AIR</span>'
        f'<span class="studio-current">{current_label}</span>'
        '</div>'
        + tts_bar +
        '<div class="host-grid">'
        + host_card(host_a)
        + host_card(host_b)
        + '</div>'
        '<div class="studio-stages">'
        + ''.join(stage_row(n, lbl) for n, lbl in stage_defs)
        + '</div>'
        '</div>'
    )


# ── Audio player ───────────────────────────────────────────────────────────────
def render_player(mp3_path: str, meta: dict):
    dur_s   = meta.get("duration_s", 0)
    dur_str = _fmt(dur_s)
    a64     = _b64(mp3_path)
    topic   = meta.get("topic", "Episode")
    fname   = os.path.basename(mp3_path)

    bars    = [22,38,56,34,68,50,74,42,60,35,84,48,70,38,55,30,72,46,62,40,80,52,66,36,54,44,71,58,40,64]
    bar_html = "".join(f'<div class="wb" style="height:{h}%"></div>' for h in bars)

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:#0a0a0f;font-family:-apple-system,'Inter',sans-serif;padding:2px 0;}}
.player{{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:18px;padding:20px 22px 18px;}}
.top{{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:16px;gap:14px;}}
.info{{flex:1;min-width:0;}}
.title{{font-size:13px;font-weight:700;color:#f1f5f9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:5px;letter-spacing:-0.01em;}}
.dur{{font-size:11px;color:#334155;}}
.waveform{{display:flex;align-items:center;gap:2px;height:30px;flex-shrink:0;}}
.wb{{width:2px;min-height:3px;background:#1e293b;border-radius:1px;transition:background 0.2s;}}
.playing .wb{{animation:wavePulse 1.3s ease-in-out infinite;}}
.wb:nth-child(odd){{animation-delay:0s!important;}}
.wb:nth-child(3n){{animation-delay:0.18s!important;}}
.wb:nth-child(5n){{animation-delay:0.36s!important;}}
@keyframes wavePulse{{0%,100%{{background:rgba(168,85,247,0.3);transform:scaleY(0.4);}}50%{{background:#a855f7;transform:scaleY(1);}}}}
.controls{{display:flex;align-items:center;gap:12px;margin-bottom:14px;}}
.play-btn{{width:38px;height:38px;flex-shrink:0;background:linear-gradient(135deg,#7c3aed,#a855f7);border:none;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:opacity .12s,transform .1s;outline:none;box-shadow:0 4px 16px rgba(168,85,247,0.35);}}
.play-btn:hover{{opacity:0.85;transform:scale(1.07);}}
.play-btn:active{{transform:scale(0.94);}}
.play-btn svg{{width:12px;height:12px;fill:#fff;margin-left:2px;}}
.play-btn.on svg{{margin-left:0;}}
.time{{font-size:11px;color:#334155;flex-shrink:0;min-width:28px;}}
.time.end{{text-align:right;}}
.track{{flex:1;height:2px;background:rgba(255,255,255,0.06);border-radius:1px;cursor:pointer;position:relative;transition:height .15s;}}
.track:hover{{height:3px;}}
.fill{{height:100%;width:0%;background:linear-gradient(90deg,#7c3aed,#a855f7,#22d3ee);border-radius:1px;pointer-events:none;transition:width .1s linear;}}
.vol{{display:flex;align-items:center;gap:6px;flex-shrink:0;}}
.vol-icon{{font-size:11px;color:#334155;cursor:pointer;user-select:none;}}
.vol-range{{-webkit-appearance:none;width:50px;height:2px;background:rgba(255,255,255,0.08);border-radius:1px;outline:none;cursor:pointer;}}
.vol-range::-webkit-slider-thumb{{-webkit-appearance:none;width:8px;height:8px;background:#a855f7;border-radius:50%;cursor:pointer;}}
.dl-btn{{display:flex;align-items:center;justify-content:center;gap:7px;width:100%;padding:10px;background:linear-gradient(135deg,#7c3aed,#a855f7);border:none;border-radius:10px;color:#fff;font-size:13px;font-weight:600;letter-spacing:0.02em;cursor:pointer;text-decoration:none;transition:opacity .15s,transform .1s;box-shadow:0 4px 18px rgba(168,85,247,0.3);}}
.dl-btn:hover{{opacity:0.88;transform:translateY(-1px);}}
.dl-btn:active{{transform:translateY(0);}}
</style></head><body>
<div class="player">
<div class="top">
<div class="info"><div class="title">{topic}</div><div class="dur">{dur_str}</div></div>
<div class="waveform" id="wv">{bar_html}</div>
</div>
<div class="controls">
<button class="play-btn" id="pb" onclick="toggle()">
<svg id="pi" viewBox="0 0 24 24"><path id="pp" d="M8 5v14l11-7z"/></svg>
</button>
<span class="time" id="ct">0:00</span>
<div class="track" id="tr" onclick="seek(event)"><div class="fill" id="fi"></div></div>
<span class="time end">{dur_str}</span>
<div class="vol">
<span class="vol-icon" onclick="mute()">&#9834;</span>
<input class="vol-range" type="range" min="0" max="1" step="0.02" value="1" oninput="au.volume=this.value">
</div>
</div>
<a class="dl-btn" href="data:audio/mpeg;base64,{a64}" download="{fname}">&#8659; Download Episode</a>
</div>
<audio id="au" src="data:audio/mpeg;base64,{a64}" ontimeupdate="tick()" onended="end()"></audio>
<script>
const au=document.getElementById('au'),pb=document.getElementById('pb'),pp=document.getElementById('pp'),ct=document.getElementById('ct'),fi=document.getElementById('fi'),wv=document.getElementById('wv');
const P='M8 5v14l11-7z',PA='M6 19h4V5H6v14zm8-14v14h4V5h-4z';
function fmt(s){{return Math.floor(s/60)+':'+(Math.floor(s%60)+'').padStart(2,'0');}}
function toggle(){{if(au.paused){{au.play();pp.setAttribute('d',PA);pb.classList.add('on');wv.classList.add('playing');}}else{{au.pause();pp.setAttribute('d',P);pb.classList.remove('on');wv.classList.remove('playing');}}}}
function tick(){{if(!au.duration)return;fi.style.width=(au.currentTime/au.duration*100)+'%';ct.textContent=fmt(au.currentTime);}}
function seek(e){{const r=e.currentTarget.getBoundingClientRect();au.currentTime=((e.clientX-r.left)/r.width)*au.duration;}}
function end(){{pp.setAttribute('d',P);pb.classList.remove('on');wv.classList.remove('playing');}}
function mute(){{au.muted=!au.muted;}}
</script>
</body></html>"""

    components.html(html, height=170)


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
    stage_slot.markdown(render_studio(1), unsafe_allow_html=True)
    research_data = _run(search_and_scrape(topic))
    n_sources = len(research_data.get("sources", []))

    # ── Script ─────────────────────────────────────────────────────────────────
    st.session_state.stage = 2
    stage_slot.markdown(
        render_studio(2, detail=f"Found {n_sources} sources \u00b7 Writing with Groq\u2026"),
        unsafe_allow_html=True,
    )
    script  = _run(generate_script(research_data))
    n_turns = len(script)
    n_words = sum(len(t["line"].split()) for t in script)

    # ── Audio / TTS ────────────────────────────────────────────────────────────
    st.session_state.stage = 3
    os.makedirs(config.TEMP_DIR,   exist_ok=True)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    for old in glob.glob(os.path.join(config.TEMP_DIR, "turn_*.mp3")):
        os.remove(old)

    segment_paths = []
    for i, turn in enumerate(script):
        stage_slot.markdown(
            render_studio(3, detail=f"{turn['host']} \u00b7 turn {i+1}/{n_turns}",
                          tts_done=i, tts_total=n_turns, current_host=turn["host"]),
            unsafe_allow_html=True,
        )
        path = os.path.join(config.TEMP_DIR, f"turn_{i:03d}_{turn['host'].lower()}.mp3")
        _run(synthesise_turn(turn["line"], voice_map[turn["host"]], path))
        segment_paths.append(path)

    # ── Assemble ───────────────────────────────────────────────────────────────
    stage_slot.markdown(
        render_studio(3, tts_done=n_turns, tts_total=n_turns, assembling=True),
        unsafe_allow_html=True,
    )
    output_path = assemble_episode(segment_paths)

    from pydub import AudioSegment as _AS
    dur_s   = len(_AS.from_mp3(output_path)) / 1000
    size_mb = os.path.getsize(output_path) / (1024 * 1024)

    st.session_state.stage = 4
    stage_slot.markdown(render_studio(4), unsafe_allow_html=True)

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

# ── Navbar ─────────────────────────────────────────────────────────────────────
st.markdown(
'<nav class="pp-nav">'
'<a class="pp-nav-logo" href="#">'
'<div class="pp-nav-logo-icon">🎙</div>'
'<span class="pp-nav-logo-text">Parsepod</span>'
'</a>'
'<div class="pp-nav-links">'
'<a class="pp-nav-link" href="#">How it works</a>'
'<a class="pp-nav-link" href="#">About</a>'
'<a class="pp-nav-cta" href="#">🎙 Launch Studio</a>'
'</div>'
'</nav>',
unsafe_allow_html=True,
)

# ── Hero — single centered column ─────────────────────────────────────────────
_sw_heights = [4, 7, 12, 18, 14, 22, 10, 18, 26, 20, 22, 15, 20, 10, 16, 8, 12, 6, 9, 14]
_sw_delays  = [0,.08,.16,.24,.12,.20,.04,.32,.08,.28,.16,.36,.24,.40,.20,.44,.12,.28,.36,.20]
_sw_html = ''.join(
    f'<div class="sw-bar" style="height:{h}px;animation-delay:{d:.2f}s"></div>'
    for h, d in zip(_sw_heights, _sw_delays)
)

# 1–3: badge, headline, subheadline
st.markdown(
'<div class="pp-hero">'
'<div class="pp-eyebrow"><div class="pp-eyebrow-dot"></div>AI Podcast Generator</div>'
'<h1 class="pp-h1">Drop a topic.<br>Get a podcast.</h1>'
'<p class="pp-sub">Parsepod researches the web, writes the script, and records two British hosts \u2014 in under a minute.</p>'
'</div>',
unsafe_allow_html=True,
)

# 4–5: "YOUR TOPIC" label + input form (centered, max-width 600px via CSS)
st.markdown('<p class="pp-card-label">🎙 Your topic</p>', unsafe_allow_html=True)
with st.form("search", clear_on_submit=False):
    topic = st.text_input(
        "topic", label_visibility="collapsed",
        placeholder="Try: The future of AI in healthcare\u2026",
        disabled=st.session_state.generating,
    )
    submitted = st.form_submit_button(
        "Generate \u2192",
        disabled=st.session_state.generating,
    )

# 6: host chips — centered side by side
host_a = config.HOST_A_NAME
host_b = config.HOST_B_NAME
st.markdown(
'<div class="pp-host-chips">'
f'<div class="pp-host-chip"><div class="pp-chip-avatar pp-chip-a">{host_a[:2].upper()}</div>{host_a} 🎙</div>'
f'<div class="pp-host-chip"><div class="pp-chip-avatar pp-chip-b">{host_b[:2].upper()}</div>{host_b} 🎙</div>'
'</div>',
unsafe_allow_html=True,
)

# 7: CTA buttons + soundwave
st.markdown(
'<div class="pp-cta-row">'
'<span class="pp-hero-btn">🎙 Generate My Podcast</span>'
'<a class="pp-text-link" href="#">See how it works \u2193</a>'
'</div>'
f'<div class="pp-soundwave">{_sw_html}</div>',
unsafe_allow_html=True,
)

# ── Placeholder cycler ────────────────────────────────────────────────────────
components.html("""<script>
var _pp_topics = [
"Try: The future of sleep science\u2026",
"Try: Why Rome really fell\u2026",
"Try: The rise of open source AI\u2026",
"Try: What makes music emotional\u2026",
"Try: The hidden history of the internet\u2026",
"Try: How CRISPR will change medicine\u2026"
];
var _pp_idx = 0;
function _pp_cycle() {
try {
var inp = window.parent.document.querySelector('[data-testid="stForm"] input[type="text"]');
if (inp && !inp.value) { inp.placeholder = _pp_topics[_pp_idx % _pp_topics.length]; _pp_idx++; }
} catch(e) {}
}
_pp_cycle();
setInterval(_pp_cycle, 3000);
</script>""", height=0)

# ── Stage slot — populated during pipeline run ────────────────────────────────
stage_slot = st.empty()

# ── Trigger pipeline ───────────────────────────────────────────────────────────
if submitted and (topic or "").strip():
    for k in ("script", "research_data", "output_path", "episode_meta", "error"):
        st.session_state[k] = None
    st.session_state.generating = True
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
    f'<div class="pp-error">\u26a0\ufe0f {st.session_state.error}</div>',
    unsafe_allow_html=True,
    )

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.output_path and os.path.exists(st.session_state.output_path):
    meta   = st.session_state.episode_meta or {}
    ts_str = (datetime.fromisoformat(meta["timestamp"]).strftime("%b %d, %Y \u00b7 %H:%M")
              if meta.get("timestamp") else "")

    st.markdown('<div class="pp-result-wrap">', unsafe_allow_html=True)

    st.markdown(
    '<div class="ep-card">'
    f'<div class="ep-title">{meta.get("topic", "Episode")}</div>'
    '<div class="ep-badges">'
    f'<span class="ep-badge">{ts_str}</span>'
    f'<span class="ep-badge">{_fmt(meta.get("duration_s", 0))}</span>'
    f'<span class="ep-badge">{meta.get("turns", "?")} turns</span>'
    f'<span class="ep-badge">{meta.get("words", 0):,} words</span>'
    f'<span class="ep-badge">{meta.get("size_mb", 0):.1f} MB</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
    )

    render_player(st.session_state.output_path, meta)

    # Transcript
    with st.expander("Transcript"):
        if st.session_state.script:
            parts = ['<div class="turns">']
            for turn in st.session_state.script:
                is_a     = turn["host"] == config.HOST_A_NAME
                i_cls    = "ryan-init"  if is_a else "jenny-init"
                n_cls    = "ryan-name"  if is_a else "jenny-name"
                initials = turn["host"][:2].upper()
                parts.append(
                '<div class="turn">'
                f'<div class="turn-init {i_cls}">{initials}</div>'
                '<div class="turn-text">'
                f'<div class="turn-name {n_cls}">{turn["host"]}</div>'
                f'<div class="turn-line">{turn["line"]}</div>'
                '</div>'
                '</div>'
                )
            parts.append('</div>')
            st.markdown(''.join(parts), unsafe_allow_html=True)
        else:
            st.markdown('<p class="empty-text">Transcript not available for loaded episodes.</p>',
                        unsafe_allow_html=True)

    # Sources
    sources = (
        (st.session_state.research_data or {}).get("sources", [])
        or [{"url": u, "title": u, "snippet": "", "score": 0}
            for u in meta.get("sources", [])]
    )
    if sources:
        with st.expander("Sources"):
            parts = ['<div>']
            for src in sources:
                title   = src.get("title") or src.get("url", "")
                snippet = src.get("snippet", "")
                url     = src.get("url", "")
                snip_h  = f'<div class="source-snippet">{snippet}</div>' if snippet else ""
                parts.append(
                '<div class="source-item">'
                f'<div class="source-title">{title}</div>'
                + snip_h +
                f'<a class="source-url" href="{url}" target="_blank">\u2197 {url}</a>'
                '</div>'
                )
            parts.append('</div>')
            st.markdown(''.join(parts), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close pp-result-wrap

# ── Empty state (no result, not generating) ────────────────────────────────────
elif not st.session_state.generating and not st.session_state.error:
    st.markdown(
    '<div class="empty-state">'
    '<div class="empty-mic">🎙</div>'
    '<p class="empty-text">Your episode will appear here</p>'
    '<p class="empty-hint">Type any topic above and hit Generate</p>'
    '</div>',
    unsafe_allow_html=True,
    )

# ── Marketing sections — only shown when idle (no result, not generating) ──────
_show_marketing = (
    not st.session_state.generating
    and not st.session_state.output_path
    and not st.session_state.error
)

if _show_marketing:

    # Trust bar
    st.markdown(
    '<div class="pp-trust">'
    '<span class="pp-trust-label">Powered by</span>'
    '<div class="pp-trust-item"><span class="pp-trust-icon">⚡</span>Groq LLM</div>'
    '<div class="pp-trust-sep"></div>'
    '<div class="pp-trust-item"><span class="pp-trust-icon">🔍</span>Tavily Research</div>'
    '<div class="pp-trust-sep"></div>'
    '<div class="pp-trust-item"><span class="pp-trust-icon">🗣</span>Edge TTS</div>'
    '<div class="pp-trust-sep"></div>'
    '<div class="pp-trust-item"><span class="pp-trust-icon">🎵</span>pydub + ffmpeg</div>'
    '</div>',
    unsafe_allow_html=True,
    )

    # Feature grid
    st.markdown(
    '<div class="pp-section">'
    '<div class="pp-section-eyebrow">What Parsepod does</div>'
    '<div class="pp-section-title">Everything. Automatically.</div>'
    '<div class="pp-section-sub">Drop a topic. Parsepod handles the research, writing, voice recording, and audio mixing.</div>'
    '<div class="pp-features">'
    '<div class="pp-feat-card"><div class="pp-feat-icon">🔍</div><div class="pp-feat-title">Deep Research</div><div class="pp-feat-desc">Searches and scrapes live web sources for up-to-date context on any topic.</div></div>'
    '<div class="pp-feat-card"><div class="pp-feat-icon">✍️</div><div class="pp-feat-title">Smart Scripting</div><div class="pp-feat-desc">Two-host banter and debate written by Groq\u2019s llama-3.3-70b model.</div></div>'
    '<div class="pp-feat-card"><div class="pp-feat-icon">🎙</div><div class="pp-feat-title">British Voices</div><div class="pp-feat-desc">Thomas &amp; Libby \u2014 neural text-to-speech that sounds genuinely broadcast-ready.</div></div>'
    '<div class="pp-feat-card"><div class="pp-feat-icon">🎵</div><div class="pp-feat-title">Instant MP3</div><div class="pp-feat-desc">Mixed, mastered, and ready to share. Download in one click.</div></div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
    )

    # How it works
    st.markdown(
    '<div class="pp-section">'
    '<div class="pp-section-eyebrow">The process</div>'
    '<div class="pp-section-title">Five steps. One minute.</div>'
    '<div class="pp-section-sub">From blank topic to finished podcast, fully automated.</div>'
    '<div class="pp-timeline">'
    '<div class="pp-step"><div class="pp-step-num">1</div><div class="pp-step-body"><div class="pp-step-title">Enter your topic</div><div class="pp-step-desc">Type anything \u2014 a news story, a curiosity, a question. The more specific, the sharper the episode.</div></div></div>'
    '<div class="pp-step"><div class="pp-step-num">2</div><div class="pp-step-body"><div class="pp-step-title">Parsepod searches the web</div><div class="pp-step-desc">Tavily fetches and scrapes up to 8 live sources, pulling raw content up to 5,000 characters per page.</div></div></div>'
    '<div class="pp-step"><div class="pp-step-num">3</div><div class="pp-step-body"><div class="pp-step-title">AI writes the script</div><div class="pp-step-desc">Groq\u2019s LLM turns the research into a two-host back-and-forth script \u2014 no summarisation, just sharp dialogue.</div></div></div>'
    '<div class="pp-step"><div class="pp-step-num">4</div><div class="pp-step-body"><div class="pp-step-title">Thomas &amp; Libby record it</div><div class="pp-step-desc">Microsoft Edge TTS voices each turn sequentially \u2014 British accents, natural cadence, broadcast quality.</div></div></div>'
    '<div class="pp-step"><div class="pp-step-num">5</div><div class="pp-step-body"><div class="pp-step-title">Download your MP3</div><div class="pp-step-desc">pydub assembles and mixes the final episode. Hit download \u2014 it\u2019s yours.</div></div></div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
    )

    # FAQ
    st.markdown(
    '<div class="pp-section">'
    '<div class="pp-section-eyebrow">FAQ</div>'
    '<div class="pp-section-title">Common questions</div>'
    '<div class="pp-faq">'
    '<details class="pp-faq-item"><summary>How long does it take?</summary><p class="pp-faq-answer">Typically 45\u201390 seconds end-to-end. Research and LLM scripting take around 10\u201320 seconds each; TTS synthesis scales with script length but is usually under a minute for a 3-minute episode.</p></details>'
    '<details class="pp-faq-item"><summary>Can I change the hosts or voices?</summary><p class="pp-faq-answer">Yes \u2014 set <code>HOST_A_VOICE</code> and <code>HOST_B_VOICE</code> in your <code>.env</code> file to any Edge TTS voice. Run <code>edge-tts --list-voices</code> to browse all options. Host names are also configurable.</p></details>'
    '<details class="pp-faq-item"><summary>What topics work best?</summary><p class="pp-faq-answer">Anything with a reasonable amount of web coverage works well \u2014 science, technology, history, culture, current events. Very niche or obscure topics may yield fewer sources and a thinner script.</p></details>'
    '<details class="pp-faq-item"><summary>Is the audio downloadable?</summary><p class="pp-faq-answer">Yes. Every episode is saved as an MP3 in the <code>output/</code> directory and available via the in-app download button. Metadata is stored as a paired JSON file.</p></details>'
    '<details class="pp-faq-item"><summary>Does it store my topics or audio?</summary><p class="pp-faq-answer">Everything stays local. Episodes are saved to your <code>output/</code> folder; nothing is sent anywhere beyond the Tavily and Groq API calls needed to generate the episode.</p></details>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
    )

# ── Recent episodes ────────────────────────────────────────────────────────────
history = _load_history()
if history and not st.session_state.generating:
    st.markdown('<div class="recent-heading">Recent Episodes</div>', unsafe_allow_html=True)
    for ep in history[:6]:
        col1, col2 = st.columns([1, 5], vertical_alignment="center")
        with col2:
            st.markdown(
            '<div class="recent-item">'
            f'<span class="recent-topic">{ep["topic"]}</span>'
            f'<span class="recent-dur">{_fmt(ep.get("duration_s", 0))}</span>'
            '</div>',
            unsafe_allow_html=True,
            )
        with col1:
            if st.button("Load", key=f"load_{ep['timestamp']}"):
                st.session_state.output_path  = ep["mp3_path"]
                st.session_state.episode_meta = ep
                st.session_state.script       = None
                st.session_state.research_data = None
                st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
'<div class="pp-footer">'
'<div class="pp-footer-left">'
'<a class="pp-footer-logo" href="#">'
'<div class="pp-footer-logo-icon">🎙</div>'
'<span class="pp-footer-logo-text">Parsepod</span>'
'</a>'
'<span class="pp-footer-tagline">AI-powered podcast generation</span>'
'</div>'
'<div class="pp-footer-links">'
'<a class="pp-footer-link" href="https://github.com" target="_blank">GitHub</a>'
'<a class="pp-footer-link" href="#">Docs</a>'
'<a class="pp-footer-link" href="#">Privacy</a>'
'</div>'
'</div>',
unsafe_allow_html=True,
)
