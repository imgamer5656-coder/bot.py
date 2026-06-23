"""
NeoChat AI — Premium Professional Edition
Features:
  - Text chat (Groq LLM - Llama 3.3 70B)
  - Image generation (Pollinations.ai — free, unlimited, no key)
  - Image upload + analysis (Groq meta-llama/llama-4-scout-17b-16e-instruct)
  - Multi-conversation history with rename & delete
  - Fully premium dark UI with theme switcher

Run locally:
  streamlit run app.py

Deploy:
  Add GROQ_API_KEY to Streamlit Cloud → Settings → Secrets
"""

import streamlit as st
from groq import Groq
import requests
import base64
from datetime import datetime
import os
import uuid

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="NeoChat AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# API KEY
# ─────────────────────────────────────────────
def get_groq_api_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "")

GROQ_API_KEY = get_groq_api_key()
if not GROQ_API_KEY:
    st.error("⚠️ GROQ_API_KEY not found. Add it in Streamlit Secrets or as an environment variable.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

TEXT_MODEL   = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# ─────────────────────────────────────────────
# THEME DEFINITIONS
# ─────────────────────────────────────────────
THEMES = {
    "Midnight": {
        "bg":        "#0a0b0f",
        "sidebar":   "#0f1117",
        "card":      "#13151c",
        "border":    "#1e2130",
        "accent":    "#6c63ff",
        "accent2":   "#a78bfa",
        "user_msg":  "linear-gradient(135deg,#3b2dbf,#6c63ff)",
        "ai_msg":    "#13151c",
        "text":      "#e8eaf6",
        "muted":     "#6b7280",
        "input_bg":  "#1a1d27",
        "btn":       "#6c63ff",
        "btn_hover": "#5549e0",
        "danger":    "#ef4444",
        "success":   "#22c55e",
        "tag_bg":    "#1e1b4b",
    },
    "Obsidian": {
        "bg":        "#0d0d0d",
        "sidebar":   "#111111",
        "card":      "#191919",
        "border":    "#2a2a2a",
        "accent":    "#00d4aa",
        "accent2":   "#00ffcc",
        "user_msg":  "linear-gradient(135deg,#007a5e,#00d4aa)",
        "ai_msg":    "#191919",
        "text":      "#f0f0f0",
        "muted":     "#666666",
        "input_bg":  "#1a1a1a",
        "btn":       "#00d4aa",
        "btn_hover": "#00b891",
        "danger":    "#ff5555",
        "success":   "#00d4aa",
        "tag_bg":    "#0a2e28",
    },
    "Aurora": {
        "bg":        "#07080f",
        "sidebar":   "#0b0d16",
        "card":      "#10121e",
        "border":    "#1c1e30",
        "accent":    "#e040fb",
        "accent2":   "#40c4ff",
        "user_msg":  "linear-gradient(135deg,#6a0dad,#e040fb)",
        "ai_msg":    "#10121e",
        "text":      "#eef2ff",
        "muted":     "#6b7280",
        "input_bg":  "#16182a",
        "btn":       "#e040fb",
        "btn_hover": "#c020e0",
        "danger":    "#f87171",
        "success":   "#34d399",
        "tag_bg":    "#1a0a2e",
    },
}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "theme"        not in st.session_state: st.session_state.theme        = "Midnight"
if "conversations" not in st.session_state: st.session_state.conversations = {}
if "current_chat_id" not in st.session_state:
    _id = str(uuid.uuid4())
    st.session_state.conversations[_id] = {"title": "New Conversation", "messages": []}
    st.session_state.current_chat_id = _id
if "mode"          not in st.session_state: st.session_state.mode          = "Chat"
if "system_prompt" not in st.session_state: st.session_state.system_prompt = "You are NeoChat AI, a brilliant and helpful assistant. Be concise, clear, and insightful."
if "rename_id"     not in st.session_state: st.session_state.rename_id     = None

T = THEMES[st.session_state.theme]

def current_messages():
    return st.session_state.conversations[st.session_state.current_chat_id]["messages"]

def set_chat_title(text):
    chat = st.session_state.conversations[st.session_state.current_chat_id]
    if chat["title"] in ("New Conversation", ""):
        chat["title"] = (text[:38] + "…") if len(text) > 38 else text

def new_chat():
    _id = str(uuid.uuid4())
    st.session_state.conversations[_id] = {"title": "New Conversation", "messages": []}
    st.session_state.current_chat_id = _id

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp {{
    background-color: {T['bg']} !important;
    font-family: 'Inter', sans-serif;
    color: {T['text']};
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {T['sidebar']} !important;
    border-right: 1px solid {T['border']};
    padding: 0 !important;
}}
section[data-testid="stSidebar"] > div {{ padding: 1.2rem 1rem; }}

/* ── Main area ── */
.block-container {{
    max-width: 860px;
    padding: 1.5rem 1.5rem 6rem 1.5rem;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['border']}; border-radius: 99px; }}

/* ── Chat bubbles ── */
.bubble-user {{
    background: {T['user_msg']};
    color: #fff;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 6px 0 6px auto;
    max-width: 78%;
    font-size: 0.93rem;
    line-height: 1.6;
    word-break: break-word;
    box-shadow: 0 4px 16px rgba(0,0,0,0.35);
}}
.bubble-ai {{
    background: {T['ai_msg']};
    color: {T['text']};
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 6px auto 6px 0;
    max-width: 82%;
    font-size: 0.93rem;
    line-height: 1.7;
    border: 1px solid {T['border']};
    word-break: break-word;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}}
.bubble-ai code {{
    background: rgba(255,255,255,0.07);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85em;
}}
.bubble-ai pre {{
    background: rgba(0,0,0,0.4);
    border: 1px solid {T['border']};
    border-radius: 10px;
    padding: 12px 14px;
    overflow-x: auto;
    margin: 10px 0;
}}

/* ── Header ── */
.neo-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0.3rem;
}}
.neo-logo {{
    width: 40px; height: 40px;
    background: {T['accent']};
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 0 20px {T['accent']}55;
}}
.neo-title {{
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, {T['accent']}, {T['accent2']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}}
.neo-subtitle {{
    font-size: 0.8rem;
    color: {T['muted']};
    letter-spacing: 0.3px;
    margin-top: 2px;
    margin-bottom: 1.2rem;
}}

/* ── Sidebar nav btn ── */
.stButton > button {{
    background: transparent !important;
    border: 1px solid {T['border']} !important;
    color: {T['text']} !important;
    border-radius: 10px !important;
    font-size: 0.83rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.18s ease !important;
    text-align: left !important;
    padding: 8px 12px !important;
}}
.stButton > button:hover {{
    border-color: {T['accent']} !important;
    background: {T['tag_bg']} !important;
    color: {T['accent2']} !important;
}}

/* ── Primary accent button ── */
div[data-testid="stButton"] button[kind="primary"],
.stButton > button[kind="primary"] {{
    background: {T['accent']} !important;
    border-color: {T['accent']} !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 0 14px {T['accent']}44 !important;
}}
div[data-testid="stButton"] button[kind="primary"]:hover {{
    background: {T['btn_hover']} !important;
}}

/* ── Chat input ── */
div[data-testid="stChatInput"] textarea {{
    background: {T['input_bg']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 14px !important;
    color: {T['text']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 12px 16px !important;
    transition: border 0.2s;
}}
div[data-testid="stChatInput"] textarea:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 2px {T['accent']}22 !important;
}}

/* ── Selectbox / radio / text input ── */
.stSelectbox div[data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {T['input_bg']} !important;
    border-color: {T['border']} !important;
    color: {T['text']} !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Radio ── */
.stRadio label {{ color: {T['muted']} !important; font-size: 0.85rem !important; }}
.stRadio [data-testid="stMarkdownContainer"] p {{ color: {T['text']} !important; }}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background: {T['card']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 10px !important;
    color: {T['muted']} !important;
    font-size: 0.83rem !important;
}}

/* ── Divider ── */
hr {{ border-color: {T['border']} !important; margin: 0.8rem 0 !important; }}

/* ── Tag pill ── */
.tag {{
    display: inline-block;
    background: {T['tag_bg']};
    color: {T['accent2']};
    font-size: 0.7rem;
    padding: 2px 9px;
    border-radius: 99px;
    border: 1px solid {T['accent']}44;
    margin-right: 4px;
    font-weight: 500;
    letter-spacing: 0.3px;
}}

/* ── Model badge ── */
.model-badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: {T['tag_bg']};
    border: 1px solid {T['accent']}33;
    color: {T['muted']};
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 99px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 0.5rem;
}}

/* ── Section label ── */
.section-label {{
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: {T['muted']};
    margin: 1rem 0 0.4rem 0;
}}

/* ── Chat avatar row ── */
.chat-row {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin: 4px 0;
}}
.chat-row.user-row {{ flex-direction: row-reverse; }}
.avatar {{
    width: 30px; height: 30px; min-width: 30px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 4px;
}}
.avatar-user {{ background: {T['accent']}; color: #fff; }}
.avatar-ai   {{ background: {T['card']}; color: {T['accent2']}; border: 1px solid {T['border']}; }}

/* ── Stats row ── */
.stats-row {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 1.2rem;
}}
.stat-card {{
    background: {T['card']};
    border: 1px solid {T['border']};
    border-radius: 12px;
    padding: 10px 16px;
    flex: 1;
    min-width: 90px;
    text-align: center;
}}
.stat-val {{
    font-size: 1.3rem;
    font-weight: 700;
    color: {T['accent']};
}}
.stat-lbl {{
    font-size: 0.68rem;
    color: {T['muted']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}}

/* ── Image card ── */
.img-card {{
    background: {T['card']};
    border: 1px solid {T['border']};
    border-radius: 14px;
    overflow: hidden;
    margin: 8px 0;
}}
.img-card-footer {{
    padding: 10px 14px;
    font-size: 0.8rem;
    color: {T['muted']};
    border-top: 1px solid {T['border']};
}}

/* ── Spinner override ── */
.stSpinner > div {{ border-top-color: {T['accent']} !important; }}

/* ── Sidebar history item ── */
.history-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 7px 10px;
    border-radius: 9px;
    cursor: pointer;
    transition: background 0.15s;
    border: 1px solid transparent;
    margin-bottom: 3px;
}}
.history-item:hover {{ background: {T['card']}; border-color: {T['border']}; }}
.history-item.active {{ background: {T['tag_bg']}; border-color: {T['accent']}33; }}
.history-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: {T['accent']};
    flex-shrink: 0;
}}

/* ── Mobile Sidebar Toggle Button ── */
.mobile-menu-btn {{
    display: none;
    position: fixed;
    bottom: 90px;
    left: 16px;
    z-index: 99999;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: {T['accent']};
    color: #fff;
    font-size: 1.4rem;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 24px {T['accent']}88;
    align-items: center;
    justify-content: center;
    transition: background 0.2s, transform 0.15s;
}}
.mobile-menu-btn:hover {{
    background: {T['btn_hover']};
    transform: scale(1.08);
}}
@media (max-width: 768px) {{
    .mobile-menu-btn {{ display: flex !important; }}
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MOBILE SIDEBAR TOGGLE BUTTON
# ─────────────────────────────────────────────
st.markdown("""
<button class="mobile-menu-btn" onclick="toggleSidebar()" title="Menu">☰</button>
<script>
function toggleSidebar() {
    var doc = window.parent.document;
    // Try Streamlit's built-in collapsed/open button
    var btn = doc.querySelector('[data-testid="collapsedControl"]');
    if (!btn) {
        btn = doc.querySelector('button[aria-label="Close sidebar"]');
    }
    if (!btn) {
        btn = doc.querySelector('button[aria-label="Open sidebar"]');
    }
    if (btn) {
        btn.click();
        return;
    }
    // Fallback: manually toggle sidebar transform
    var sidebar = doc.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        var rect = sidebar.getBoundingClientRect();
        if (rect.left < 0) {
            sidebar.style.transition = 'transform 0.3s ease';
            sidebar.style.transform = 'translateX(0)';
        } else {
            sidebar.style.transition = 'transform 0.3s ease';
            sidebar.style.transform = 'translateX(-110%)';
        }
    }
}
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def generate_image(prompt: str, width=1024, height=1024):
    safe = requests.utils.quote(prompt)
    url  = f"https://image.pollinations.ai/prompt/{safe}?width={width}&height={height}&nologo=true&enhance=true"
    r = requests.get(url, timeout=90)
    r.raise_for_status()
    return r.content

def analyze_image(image_bytes: bytes, question: str, mime_type: str = "image/jpeg"):
    b64   = base64.b64encode(image_bytes).decode()
    data_url = f"data:{mime_type};base64,{b64}"
    resp = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text",      "text": question or "Describe this image in detail."},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }],
        temperature=0.6,
        max_tokens=1500,
    )
    return resp.choices[0].message.content

def stream_chat(messages):
    system = [{"role": "system", "content": st.session_state.system_prompt}]
    comp = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=system + messages,
        temperature=0.7,
        max_tokens=2048,
        stream=True,
    )
    for chunk in comp:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Logo + brand
    st.markdown(f"""
    <div class="neo-header">
        <div class="neo-logo">✦</div>
        <div>
            <div class="neo-title">NeoChat AI</div>
        </div>
    </div>
    <div class="neo-subtitle">Powered by Groq · Llama 3.3 · Vision AI</div>
    """, unsafe_allow_html=True)

    # New chat button
    if st.button("＋  New Conversation", use_container_width=True, type="primary"):
        new_chat()
        st.rerun()

    # ── Mode ──
    st.markdown('<div class="section-label">Mode</div>', unsafe_allow_html=True)
    mode_icons = {"Chat": "💬  Chat", "Image Generation": "🎨  Image Generation"}
    selected_mode = st.radio(
        "mode",
        list(mode_icons.keys()),
        format_func=lambda x: mode_icons[x],
        label_visibility="collapsed",
        index=list(mode_icons.keys()).index(st.session_state.mode),
    )
    st.session_state.mode = selected_mode

    st.markdown("---")

    # ── Theme ──
    st.markdown('<div class="section-label">Theme</div>', unsafe_allow_html=True)
    chosen_theme = st.selectbox(
        "theme",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme),
        label_visibility="collapsed",
    )
    if chosen_theme != st.session_state.theme:
        st.session_state.theme = chosen_theme
        st.rerun()

    st.markdown("---")

    # ── System prompt ──
    with st.expander("⚙️  System Prompt"):
        new_sp = st.text_area(
            "System prompt",
            value=st.session_state.system_prompt,
            height=100,
            label_visibility="collapsed",
        )
        if st.button("Apply", use_container_width=True):
            st.session_state.system_prompt = new_sp
            st.success("Applied!")

    st.markdown("---")

    # ── History ──
    st.markdown('<div class="section-label">Conversations</div>', unsafe_allow_html=True)
    for cid in reversed(list(st.session_state.conversations.keys())):
        conv  = st.session_state.conversations[cid]
        label = conv["title"] or "New Conversation"
        is_active = (cid == st.session_state.current_chat_id)
        msg_count = len(conv["messages"])

        cols = st.columns([6, 1])
        with cols[0]:
            btn_label = f"{'▶ ' if is_active else ''}{label[:30]}" + (f"  [{msg_count}]" if msg_count else "")
            if st.button(btn_label, key=f"sel_{cid}", use_container_width=True):
                st.session_state.current_chat_id = cid
                st.rerun()
        with cols[1]:
            if st.button("✕", key=f"del_{cid}"):
                del st.session_state.conversations[cid]
                if not st.session_state.conversations:
                    new_chat()
                elif st.session_state.current_chat_id == cid:
                    st.session_state.current_chat_id = list(st.session_state.conversations.keys())[-1]
                st.rerun()

    st.markdown("---")
    total_msgs = sum(len(c["messages"]) for c in st.session_state.conversations.values())
    total_chats = len(st.session_state.conversations)
    st.markdown(f"""
    <div style="font-size:0.72rem; color:{T['muted']}; text-align:center; padding: 4px 0;">
        {total_chats} conversation{"s" if total_chats!=1 else ""} &nbsp;·&nbsp; {total_msgs} message{"s" if total_msgs!=1 else ""}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
# Header
st.markdown(f"""
<div class="neo-header" style="margin-bottom:4px;">
    <div class="neo-logo" style="width:34px;height:34px;font-size:1.1rem;">✦</div>
    <div class="neo-title" style="font-size:1.4rem;">NeoChat AI</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.mode == "Chat":
    st.markdown(f"""
    <div class="model-badge">
        <span style="color:{T['accent']};">●</span> {TEXT_MODEL}
        &nbsp;|&nbsp; Vision: {VISION_MODEL.split('/')[-1]}
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="model-badge">
        <span style="color:{T['accent']};">●</span> Pollinations.ai &nbsp;|&nbsp; Free · Unlimited · No Key
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# IMAGE GENERATION MODE
# ─────────────────────────────────────────────
if st.session_state.mode == "Image Generation":
    st.markdown(f'<div style="color:{T["muted"]};font-size:0.85rem;margin-bottom:1rem;">Describe any image — it will be generated in seconds for free.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([4, 1.5, 1.2])
    with col1:
        img_prompt = st.text_input(
            "prompt",
            placeholder="e.g. a futuristic cyberpunk city at dawn, 8k, cinematic",
            label_visibility="collapsed",
        )
    with col2:
        aspect = st.selectbox("Size", ["Square 1:1", "Portrait 3:4", "Landscape 4:3", "Wide 16:9"], label_visibility="collapsed")
    with col3:
        style  = st.selectbox("Style", ["Default", "Photorealistic", "Anime", "Oil Painting", "Sketch"], label_visibility="collapsed")

    size_map = {
        "Square 1:1":    (1024, 1024),
        "Portrait 3:4":  (768,  1024),
        "Landscape 4:3": (1024, 768),
        "Wide 16:9":     (1280, 720),
    }
    style_suffix = {
        "Default": "",
        "Photorealistic": ", ultra realistic, DSLR, 8k",
        "Anime": ", anime art style, vivid colors, Studio Ghibli",
        "Oil Painting": ", oil painting, impressionist, textured canvas",
        "Sketch": ", pencil sketch, hand drawn, detailed linework",
    }

    gen_btn = st.button("✦  Generate Image", type="primary", use_container_width=False)

    if gen_btn and img_prompt.strip():
        final_prompt = img_prompt + style_suffix.get(style, "")
        with st.spinner("Creating your image…"):
            try:
                w, h = size_map[aspect]
                img_bytes = generate_image(final_prompt, w, h)

                st.markdown(f'<div class="img-card">', unsafe_allow_html=True)
                st.image(img_bytes, use_container_width=True)
                st.markdown(f'<div class="img-card-footer">🖼️ {img_prompt} &nbsp;·&nbsp; <span class="tag">{aspect}</span><span class="tag">{style}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.download_button(
                    "⬇️  Download Image",
                    data=img_bytes,
                    file_name=f"neochat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                )

                current_messages().append({"role": "user",      "content": f"🖼️ {img_prompt}"})
                current_messages().append({"role": "assistant",  "content": "[Image generated]", "image": img_bytes})
                set_chat_title(img_prompt)

            except Exception as e:
                st.error(f"Image generation failed: {e}")

    elif gen_btn:
        st.warning("Enter a description first.")

    # Gallery of previous images
    prev_imgs = [m for m in current_messages() if m.get("image")]
    if prev_imgs:
        st.markdown(f'<div class="section-label" style="margin-top:1.5rem;">Gallery — this session</div>', unsafe_allow_html=True)
        gcols = st.columns(min(len(prev_imgs), 3))
        for i, m in enumerate(prev_imgs):
            with gcols[i % 3]:
                st.image(m["image"], use_container_width=True)

# ─────────────────────────────────────────────
# CHAT MODE
# ─────────────────────────────────────────────
else:
    msgs = current_messages()

    # Welcome screen
    if not msgs:
        st.markdown(f"""
        <div style="text-align:center; padding: 3rem 1rem; color:{T['muted']};">
            <div style="font-size:2.5rem; margin-bottom:0.8rem;">✦</div>
            <div style="font-size:1.1rem; font-weight:600; color:{T['text']}; margin-bottom:0.5rem;">How can I help you today?</div>
            <div style="font-size:0.85rem;">Ask anything, upload an image, or switch to Image Generation mode.</div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:1rem;">
            <span class="tag">💡 Explain concepts</span>
            <span class="tag">📝 Write & edit</span>
            <span class="tag">🔍 Analyze images</span>
            <span class="tag">💻 Debug code</span>
            <span class="tag">🌐 Translate</span>
        </div>
        """, unsafe_allow_html=True)

    # Render messages
    for msg in msgs:
        if msg.get("image"):
            continue  # skip image-generation records in chat view
        role = msg["role"]
        avatar_cls = "avatar-user" if role == "user" else "avatar-ai"
        avatar_icon = "U" if role == "user" else "✦"
        bubble_cls  = "bubble-user" if role == "user" else "bubble-ai"
        row_cls     = "user-row" if role == "user" else ""

        img_html = ""
        if "uploaded_image" in msg:
            b64 = base64.b64encode(msg["uploaded_image"]).decode()
            img_html = f'<img src="data:image/png;base64,{b64}" style="max-width:220px;border-radius:10px;margin-bottom:8px;display:block;">'

        st.markdown(f"""
        <div class="chat-row {row_cls}">
            <div class="avatar {avatar_cls}">{avatar_icon}</div>
            <div class="{bubble_cls}">{img_html}{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Image upload
    with st.expander("📎  Attach an image for analysis"):
        uploaded_file = st.file_uploader(
            "upload",
            type=["png", "jpg", "jpeg", "webp", "gif"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            st.image(uploaded_file, width=180, caption="Ready to analyze")

    # Chat input
    user_input = st.chat_input("Message NeoChat AI…")

    if user_input:
        set_chat_title(user_input)

        # ── Image analysis ──
        if uploaded_file is not None:
            image_bytes = uploaded_file.getvalue()
            mime_type   = uploaded_file.type or "image/png"

            current_messages().append({
                "role": "user",
                "content": user_input,
                "uploaded_image": image_bytes,
            })

            b64 = base64.b64encode(image_bytes).decode()
            st.markdown(f"""
            <div class="chat-row user-row">
                <div class="avatar avatar-user">U</div>
                <div class="bubble-user">
                    <img src="data:image/png;base64,{b64}" style="max-width:200px;border-radius:10px;margin-bottom:8px;display:block;">
                    {user_input}
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Analyzing image…"):
                try:
                    answer = analyze_image(image_bytes, user_input, mime_type)
                except Exception as e:
                    answer = f"⚠️ Error: {e}"

            st.markdown(f"""
            <div class="chat-row">
                <div class="avatar avatar-ai">✦</div>
                <div class="bubble-ai">{answer}</div>
            </div>
            """, unsafe_allow_html=True)
            current_messages().append({"role": "assistant", "content": answer})

        # ── Text chat (streaming) ──
        else:
            current_messages().append({"role": "user", "content": user_input})
            st.markdown(f"""
            <div class="chat-row user-row">
                <div class="avatar avatar-user">U</div>
                <div class="bubble-user">{user_input}</div>
            </div>
            """, unsafe_allow_html=True)

            history = [
                {"role": m["role"], "content": m["content"]}
                for m in current_messages()
                if "uploaded_image" not in m and "image" not in m
            ]

            st.markdown(f"""
            <div class="chat-row" id="ai-response-row">
                <div class="avatar avatar-ai">✦</div>
                <div class="bubble-ai" id="streaming-bubble">
            """, unsafe_allow_html=True)

            placeholder = st.empty()
            full_resp   = ""
            try:
                for chunk in stream_chat(history):
                    full_resp += chunk
                    placeholder.markdown(f"""
                    <div class="chat-row">
                        <div class="avatar avatar-ai">✦</div>
                        <div class="bubble-ai">{full_resp}▌</div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                full_resp = f"⚠️ Error: {e}"
                placeholder.markdown(f"""
                <div class="chat-row">
                    <div class="avatar avatar-ai">✦</div>
                    <div class="bubble-ai">{full_resp}</div>
                </div>
                """, unsafe_allow_html=True)

            placeholder.markdown(f"""
            <div class="chat-row">
                <div class="avatar avatar-ai">✦</div>
                <div class="bubble-ai">{full_resp}</div>
            </div>
            """, unsafe_allow_html=True)

            current_messages().append({"role": "assistant", "content": full_resp})

        st.rerun()
