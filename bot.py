"""
NeoChat AI — Premium Professional Edition (Fully Mobile Responsive)
Features:
  - Text chat (Groq LLM - Llama 3.3 70B)
  - Image generation (Pollinations.ai — free, unlimited, no key)
  - Image upload + analysis (Groq meta-llama/llama-4-scout-17b-16e-instruct)
  - Multi-conversation history with rename & delete
  - Fully responsive theme switcher & dynamic mobile view fix
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
    initial_sidebar_state="auto", # Set to auto for native mobile responsive drawer collapse
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
    # Local fallback bypass key standard placement logic if requested
    GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE" 

if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
    st.error("⚠️ GROQ_API_KEY not found. Add it in Streamlit Secrets or configuration matrix.")
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
if "theme"         not in st.session_state: st.session_state.theme        = "Midnight"
if "conversations" not in st.session_state: st.session_state.conversations = {}
if "current_chat_id" not in st.session_state:
    _id = str(uuid.uuid4())
    st.session_state.conversations[_id] = {"title": "New Conversation", "messages": []}
    st.session_state.current_chat_id = _id
if "mode"          not in st.session_state: st.session_state.mode          = "Chat"
if "system_prompt" not in st.session_state: st.session_state.system_prompt = "You are NeoChat AI, a brilliant and helpful assistant. Be concise, clear, and insightful."

T = THEMES[st.session_state.theme]

def current_messages():
    return st.session_state.conversations[st.session_state.current_chat_id]["messages"]

def set_chat_title(text):
    chat = st.session_state.conversations[st.session_state.current_chat_id]
    if chat["title"] in ("New Conversation", ""):
        chat["title"] = (text[:35] + "…") if len(text) > 35 else text

def new_chat():
    _id = str(uuid.uuid4())
    st.session_state.conversations[_id] = {"title": "New Conversation", "messages": []}
    st.session_state.current_chat_id = _id

# ─────────────────────────────────────────────
# GLOBAL CSS (OPTIMIZED FOR MOBILE ECOSYSTEM)
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

/* ── Main viewport block space padding for input stickiness ── */
.block-container {{
    max-width: 860px;
    padding: 1rem 1rem 7rem 1rem !important;
}}

/* ── Sidebar Framework ── */
section[data-testid="stSidebar"] {{
    background: {T['sidebar']} !important;
    border-right: 1px solid {T['border']};
}}
section[data-testid="stSidebar"] > div {{ padding: 1rem 0.8rem !important; }}

/* ── Mobile Friendly Fluid Chat Bubbles ── */
.bubble-user {{
    background: {T['user_msg']};
    color: #fff;
    padding: 10px 15px;
    border-radius: 16px 16px 4px 16px;
    margin: 6px 0 6px auto;
    max-width: 85%;
    font-size: 0.92rem;
    line-height: 1.5;
    word-break: break-word;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}}
.bubble-ai {{
    background: {T['ai_msg']};
    color: {T['text']};
    padding: 12px 15px;
    border-radius: 16px 16px 16px 4px;
    margin: 6px auto 6px 0;
    max-width: 90%;
    font-size: 0.92rem;
    line-height: 1.6;
    border: 1px solid {T['border']};
    word-break: break-word;
    box-shadow: 0 2px 10px rgba(0,0,0,0.25);
}}

/* ── Dynamic Layout Adaptations for Screens ── */
@media (max-width: 768px) {{
    .bubble-user {{ max-width: 90% !important; font-size: 0.88rem; }}
    .bubble-ai {{ max-width: 95% !important; font-size: 0.88rem; }}
    .neo-title {{ font-size: 1.3rem !important; }}
    div[data-testid="stForm"] {{ padding: 10px !important; }}
}}

/* Header configurations */
.neo-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 0.2rem; }}
.neo-logo {{
    width: 36px; height: 36px; background: {T['accent']}; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
    box-shadow: 0 0 15px {T['accent']}55; color: white;
}}
.neo-title {{
    font-size: 1.5rem; font-weight: 700;
    background: linear-gradient(90deg, {T['accent']}, {T['accent2']});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px;
}}
.neo-subtitle {{ font-size: 0.78rem; color: {T['muted']}; margin-bottom: 1rem; }}

/* Streamlit elements style integration override */
.stButton > button {{
    background: {T['card']} !important; border: 1px solid {T['border']} !important;
    color: {T['text']} !important; border-radius: 8px !important;
    font-size: 0.85rem !important; transition: all 0.15s ease !important;
    text-align: left !important; padding: 6px 12px !important;
}}
.stButton > button:hover {{ border-color: {T['accent']} !important; background: {T['tag_bg']} !important; }}

div[data-testid="stButton"] button[kind="primary"] {{
    background: {T['accent']} !important; border-color: {T['accent']} !important; color: #fff !important;
}}

/* Fixed Mobile Responsive Sticky Chat Field Alignment Override */
div[data-testid="stChatInput"] {{
    background-color: {T['bg']} !important;
    padding: 8px 0px !important;
}}

.model-badge {{
    display: inline-flex; align-items: center; gap: 5px; background: {T['tag_bg']};
    border: 1px solid {T['accent']}33; color: {T['text']}; font-size: 0.7rem;
    padding: 3px 10px; border-radius: 99px; font-family: 'JetBrains Mono', monospace; margin-bottom: 0.6rem;
}}

.section-label {{
    font-size: 0.68rem; font-weight: 600; letter-spacing: 1px;
    text-transform: uppercase; color: {T['muted']}; margin: 0.8rem 0 0.3rem 0;
}}

.chat-row {{ display: flex; align-items: flex-start; gap: 8px; margin: 6px 0; }}
.chat-row.user-row {{ flex-direction: row-reverse; }}
.avatar {{
    width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; margin-top: 4px;
}}
.avatar-user {{ background: {T['accent']}; color: #fff; }}
.avatar-ai   {{ background: {T['card']}; color: {T['accent2']}; border: 1px solid {T['border']}; }}

.img-card {{ background: {T['card']}; border: 1px solid {T['border']}; border-radius: 12px; overflow: hidden; margin: 8px 0; }}
.img-card-footer {{ padding: 8px 12px; font-size: 0.78rem; color: {T['muted']}; border-top: 1px solid {T['border']}; }}
.tag {{ display: inline-block; background: {T['tag_bg']}; color: {T['accent2']}; font-size: 0.68rem; padding: 2px 8px; border-radius: 99px; margin-right: 4px; }}

/* Native Streamlit Sidebar Chevron Controller Optimization for Mobile Touch Interfaces */
[data-testid="collapsedControl"] {{
    background: {T['accent']} !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 15px {T['accent']}66 !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: flex !important;
}}

/* Clean header mutes */
#MainMenu, footer, header {{ display: none !important; }}
</style>
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
    st.markdown(f"""
    <div class="neo-header">
        <div class="neo-logo">✦</div>
        <div><div class="neo-title" style="font-size:1.3rem;">NeoChat AI</div></div>
    </div>
    <div class="neo-subtitle">Powered by Groq & Pollinations</div>
    """, unsafe_allow_html=True)

    if st.button("＋  New Conversation", use_container_width=True, type="primary"):
        new_chat()
        st.rerun()

    st.markdown('<div class="section-label">Mode Workspace</div>', unsafe_allow_html=True)
    selected_mode = st.radio(
        "mode", ["Chat", "Image Generation"], label_visibility="collapsed"
    )
    st.session_state.mode = selected_mode

    st.markdown('<div class="section-label">Interface Theme</div>', unsafe_allow_html=True)
    chosen_theme = st.selectbox("theme", list(THEMES.keys()), label_visibility="collapsed")
    if chosen_theme != st.session_state.theme:
        st.session_state.theme = chosen_theme
        st.rerun()

    st.markdown('<div class="section-label">Active History threads</div>', unsafe_allow_html=True)
    for cid in reversed(list(st.session_state.conversations.keys())):
        conv  = st.session_state.conversations[cid]
        label = conv["title"] or "New Conversation"
        is_active = (cid == st.session_state.current_chat_id)
        
        cols = st.columns([5, 1])
        with cols[0]:
            btn_label = f"{'▶ ' if is_active else '💬 '}{label[:22]}"
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

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="neo-header">
    <div class="neo-logo" style="width:30px;height:30px;font-size:0.9rem;">✦</div>
    <div class="neo-title" style="font-size:1.2rem;">NeoChat AI Dashboard</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.mode == "Chat":
    st.markdown(f'<div class="model-badge">● LLM Active: {TEXT_MODEL}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="model-badge">● Engine: Pollinations Free HD</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MODE: IMAGE GENERATION
# ─────────────────────────────────────────────
if st.session_state.mode == "Image Generation":
    st.markdown(f'<div style="color:{T["muted"]};font-size:0.8rem;margin-bottom:0.5rem;">Describe an artwork or view previously generated renders:</div>', unsafe_allow_html=True)

    img_prompt = st.text_input("prompt", placeholder="e.g. cinematic post-apocalyptic base setup, 8k", label_visibility="collapsed")
    
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        aspect = st.selectbox("Aspect Ratio Options", ["Square 1:1", "Portrait 3:4", "Landscape 4:3", "Wide 16:9"])
    with col_opt2:
        style  = st.selectbox("Style Settings", ["Default", "Photorealistic", "Anime", "Oil Painting", "Sketch"])

    size_map = {"Square 1:1": (1024, 1024), "Portrait 3:4": (768, 1024), "Landscape 4:3": (1024, 768), "Wide 16:9": (1280, 720)}
    style_suffix = {"Default": "", "Photorealistic": ", ultra realistic, DSLR, 8k", "Anime": ", anime art style, vivid sketch, artwork style", "Oil Painting": ", oil painting texturized brush canvas", "Sketch": ", pencil draft hand-drawn sketch lines"}

    if st.button("✦  Compile HD Frame", type="primary"):
        if img_prompt.strip():
            final_prompt = img_prompt + style_suffix.get(style, "")
            with st.spinner("Processing structural textures..."):
                try:
                    w, h = size_map[aspect]
                    img_bytes = generate_image(final_prompt, w, h)

                    st.markdown(f'<div class="img-card">', unsafe_allow_html=True)
                    st.image(img_bytes, use_container_width=True)
                    st.markdown(f'<div class="img-card-footer">🖼️ Master Render: {img_prompt}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.download_button("⬇️ Download Master Asset", data=img_bytes, file_name="neochat_render.png", mime="image/png")

                    current_messages().append({"role": "user", "content": f"🖼️ Generated: {img_prompt}"})
                    current_messages().append({"role": "assistant", "content": "[Image generated]", "image": img_bytes})
                    set_chat_title(img_prompt)
                except Exception as e:
                    st.error(f"Render engine delay error: {e}")

# ─────────────────────────────────────────────
# MODE: CHAT (FULLY OPTIMIZED INPUT ENGINE)
# ─────────────────────────────────────────────
else:
    msgs = current_messages()

    if not msgs:
        st.markdown(f"""
        <div style="text-align:center; padding: 2rem 1rem; color:{T['muted']};">
            <div style="font-size:2rem; margin-bottom:0.5rem;">✦</div>
            <div style="font-size:1rem; font-weight:600; color:{T['text']};">Workspace Ready</div>
            <div style="font-size:0.8rem; margin-top:4px;">Open the menu container on the top-left to configure custom parameters.</div>
        </div>
        """, unsafe_allow_html=True)

    # Message rendering pipelines
    for msg in msgs:
        if msg.get("image"): continue
        role = msg["role"]
        row_cls = "user-row" if role == "user" else ""
        bubble_cls = "bubble-user" if role == "user" else "bubble-ai"
        avatar_icon = "U" if role == "user" else "✦"
        avatar_cls = "avatar-user" if role == "user" else "avatar-ai"

        img_html = ""
        if "uploaded_image" in msg:
            b64 = base64.b64encode(msg["uploaded_image"]).decode()
            img_html = f'<img src="data:image/png;base64,{b64}" style="max-width:180px; width:100%; border-radius:8px; margin-bottom:6px; display:block;">'

        st.markdown(f"""
        <div class="chat-row {row_cls}">
            <div class="avatar {avatar_cls}">{avatar_icon}</div>
            <div class="{bubble_cls}">{img_html}{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Attachments
    with st.expander("📎  Image Attachment Terminal"):
        uploaded_file = st.file_uploader("upload", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
        if uploaded_file:
            st.image(uploaded_file, width=140, caption="Buffered matrix payload")

    # Native input deployment
    user_input = st.chat_input("Message NeoChat AI…")

    if user_input:
        set_chat_title(user_input)

        if uploaded_file is not None:
            image_bytes = uploaded_file.getvalue()
            mime_type = uploaded_file.type or "image/png"

            current_messages().append({"role": "user", "content": user_input, "uploaded_image": image_bytes})
            st.rerun()
        else:
            current_messages().append({"role": "user", "content": user_input})
            
            # Streaming engine display execution blocks
            st.markdown(f"""
            <div class="chat-row">
                <div class="avatar avatar-ai">✦</div>
                <div class="bubble-ai">
            """, unsafe_allow_html=True)

            history = [{"role": m["role"], "content": m["content"]} for m in current_messages() if "uploaded_image" not in m and "image" not in m]
            
            placeholder = st.empty()
            full_resp = ""
            try:
                for chunk in stream_chat(history):
                    full_resp += chunk
                    placeholder.markdown(f'<div class="chat-row"><div class="avatar avatar-ai">✦</div><div class="bubble-ai">{full_resp}▌</div></div>', unsafe_allow_html=True)
            except Exception as e:
                full_resp = f"⚠️ Inference network delay alert: {e}"
            
            placeholder.markdown(f'<div class="chat-row"><div class="avatar avatar-ai">✦</div><div class="bubble-ai">{full_resp}</div></div>', unsafe_allow_html=True)
            current_messages().append({"role": "assistant", "content": full_resp})
            st.rerun()
