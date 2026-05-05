import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.helpers import render_product_card_html

st.set_page_config(
    page_title="AI Assistant | IntelliRec",
    page_icon="🤖",
    layout="wide", initial_sidebar_state="expanded")
check_login()

from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'light')
p = get_palette(theme)
inject_global_css(p)

render_sidebar("ai_assistant", hide_ai_fab=True)

user_id = st.session_state.get('user_id') or 'guest'

# ── Page header ───────────────────────────────────────────────────────────────
render_topbar("AI Assistant", "Chat with IntelliRec's intelligent recommendation engine")

# ── Chatbot CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Contrast override (matches About page) ──────────────── */
[data-testid="stMain"] p,
[data-testid="stMain"] span:not(.material-icons):not(.material-symbols-rounded):not(.material-symbols-outlined):not(.ir-gemini-icon),
[data-testid="stMain"] label,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span {{
    color: {p['text_primary']} !important;
    opacity: 1 !important;
}}
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3 {{
    color: {p['text_primary']} !important;
    font-weight: 700 !important;
}}





/* Quick Prompt SVG Injection (replaces emojis) */
/* Button 1: Laptops */
button:has(p:contains("Suggest laptops"))::before {{
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="%236366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="2" y1="20" x2="22" y2="20"/></svg>');
    margin-right: 8px; vertical-align: -4px;
}}
/* Button 2: Beauty */
button:has(p:contains("Best beauty"))::before {{
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="%23ec4899" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>');
    margin-right: 8px; vertical-align: -4px;
}}
/* Button 3: Gaming */
button:has(p:contains("gaming"))::before {{
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="%238b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4M8 10v4M15 13h.01M18 11h.01"/></svg>');
    margin-right: 8px; vertical-align: -4px;
}}
/* Button 4: Kitchen */
button:has(p:contains("kitchen"))::before {{
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="%23f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>');
    margin-right: 8px; vertical-align: -4px;
}}
/* Button 5: Filtering */
button:has(p:contains("collaborative"))::before {{
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="%2310b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>');
    margin-right: 8px; vertical-align: -4px;
}}
/* Button 6: Shoes */
button:has(p:contains("shoes"))::before {{
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="%233b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>');
    margin-right: 8px; vertical-align: -4px;
}}

/* ── Chat input toolbar (renders outside stMain — needs separate override) ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div {{
    background: {p['page_bg']} !important;
    border-top: 1px solid {p['border']} !important;
}}
[data-testid="stChatInput"] {{
    background: {p['glass_bg_strong']} !important;
    border: 1.5px solid {p['glass_border_soft']} !important;
    border-radius: 14px !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    overflow: hidden !important;
}}
/* Force ALL internal wrappers transparent — catches every BaseWeb layer */
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] [data-baseweb],
[data-testid="stChatInput"] [data-baseweb] > div {{
    background: transparent !important;
    background-color: transparent !important;
    border-color: transparent !important;
    box-shadow: none !important;
}}
[data-testid="stChatInput"] textarea {{
    background: transparent !important;
    color: {p['text_primary']} !important;
    -webkit-text-fill-color: {p['text_primary']} !important;
    caret-color: {p['accent']} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {p['text_muted']} !important;
    -webkit-text-fill-color: {p['text_muted']} !important;
}}
/* Send button inside chat input */
[data-testid="stChatInput"] button {{
    background: transparent !important;
    color: {p['accent']} !important;
    border: none !important;
}}

/* ── Meta AI style minimal typing indicator ─────────────────── */
.meta-typing-box {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: {p['glass_bg_strong']};
    backdrop-filter: blur(10px);
    border: 1px solid {p['glass_border']};
    border-radius: 18px;
    padding: 12px 18px;
    box-shadow: {p['glass_shadow']};
}}
.meta-dot {{
    width: 6px;
    height: 6px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 50%;
    animation: metaPulse 1.2s infinite ease-in-out both;
}}
.meta-dot:nth-child(1) {{ animation-delay: -0.32s; }}
.meta-dot:nth-child(2) {{ animation-delay: -0.16s; }}
.meta-dot:nth-child(3) {{ animation-delay: 0s; }}

@keyframes metaPulse {{
    0%, 80%, 100% {{ transform: scale(0.4); opacity: 0.3; }}
    40% {{ transform: scale(1.1); opacity: 1; }}
}}
.meta-text {{
    margin-left: 8px;
    font-size: 13px;
    font-weight: 600;
    color: {p['text_secondary']};
}}

/* ── Chat animations ────────────────────────────────────────── */
@keyframes chatPop {{
    from {{ opacity:0; transform:translateY(12px) scale(0.97); }}
    to   {{ opacity:1; transform:translateY(0)   scale(1); }}
}}
.chat-bubble-anim {{ animation: chatPop 0.3s ease-out forwards; }}

/* ── Typing indicator dots ──────────────────────────────────── */
@keyframes ir-dot-bounce {{
    0%, 80%, 100% {{ transform: translateY(0);   opacity: 0.4; }}
    40%           {{ transform: translateY(-6px); opacity: 1;   }}
}}
.ir-typing-dots {{
    display: inline-flex;
    gap: 5px;
    align-items: center;
    padding: 8px 0;
}}
.ir-typing-dots span {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {p['accent']};
    animation: ir-dot-bounce 1.2s ease-in-out infinite;
}}
.ir-typing-dots span:nth-child(2) {{ animation-delay: 0.15s; }}
.ir-typing-dots span:nth-child(3) {{ animation-delay: 0.3s; }}

/* Chat input glow on focus */
[data-testid="stChatInput"] textarea:focus {{
    border-color: {p['accent']} !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}}

/* Product mini-card inside chat */
.chat-product-strip {{
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding: 4px 2px 8px;
    scrollbar-width: thin;
}}
.chat-product-strip::-webkit-scrollbar {{ height: 4px; }}
.chat-product-strip::-webkit-scrollbar-track {{ background: transparent; }}
.chat-product-strip::-webkit-scrollbar-thumb {{
    background: {p['border']}; border-radius: 2px;
}}

/* Hero gradient card */
.assistant-hero {{
    background: {p['glass_bg']};
    border: 1px solid {p['glass_border']};
    border-radius: 20px;
    padding: 24px 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}}

/* Chat message bubbles — glassmorphism polish */
[data-testid="stChatMessage"] {{
    background: {p['glass_bg']} !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid {p['glass_border']} !important;
    border-radius: 16px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
    box-shadow: {p['glass_shadow']} !important;
}}
</style>
""", unsafe_allow_html=True)

# ── SVG AI icon for hero (no emoji) ───────────────────────────────────────────
_HERO_AI_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" '
    'viewBox="0 0 24 24" fill="none" stroke="' + p['accent'] + '" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 2a4 4 0 0 1 4 4v1h1a3 3 0 0 1 3 3v1a3 3 0 0 1-2 2.83'
    'V16a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4v-2.17A3 3 0 0 1 4 11v-1'
    'a3 3 0 0 1 3-3h1V6a4 4 0 0 1 4-4z"/>'
    '<circle cx="9" cy="12" r="0.5" fill="' + p['accent'] + '"/>'
    '<circle cx="15" cy="12" r="0.5" fill="' + p['accent'] + '"/>'
    '<path d="M10 16h4"/>'
    '<path d="M12 2v-1"/>'
    '<path d="M8.5 5L7 3.5"/>'
    '<path d="M15.5 5L17 3.5"/>'
    '</svg>'
)

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="assistant-hero">
  <div style="position:absolute;top:-20px;right:-20px;width:120px;height:120px;
              border-radius:50%;background:rgba(99,102,241,0.06);filter:blur(18px);"></div>
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
    {_HERO_AI_SVG}
    <span style="font-size:26px;font-weight:800;color:{p['text_primary']};">
      IntelliRec AI Assistant
    </span>
  </div>
  <p style="font-size:14px;color:{p['text_secondary']};margin:0;max-width:600px;">
    Ask me to recommend products, explain AI concepts, or answer shopping questions.
    I use <strong>3 live AI engines</strong> to find your perfect match.
  </p>
  <div style="display:flex;gap:8px;margin-top:14px;flex-wrap:wrap;">
    <span style="background:{p['accent_soft']};color:{p['accent']};padding:4px 12px;
                 border-radius:100px;font-size:12px;font-weight:600;">
      Hybrid SVD + TF-IDF
    </span>
    <span style="background:rgba(16,185,129,0.08);color:#10b981;padding:4px 12px;
                 border-radius:100px;font-size:12px;font-weight:600;">
      VADER Sentiment
    </span>
    <span style="background:rgba(245,158,11,0.08);color:#f59e0b;padding:4px 12px;
                 border-radius:100px;font-size:12px;font-weight:600;">
      Context-Aware
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Example prompts ───────────────────────────────────────────────────────────
EXAMPLE_PROMPTS = [
    "Suggest laptops under ₹50,000",
    "Best beauty products",
    "Recommend for gaming",
    "Top kitchen appliances under $100",
    "What is collaborative filtering?",
    "Affordable running shoes",
]

st.markdown(f'<p style="font-size:13px;font-weight:600;color:{p["text_secondary"]};margin-bottom:10px;">Try a quick prompt:</p>',
            unsafe_allow_html=True)
st.markdown('<div class="ai-prompts-clean">', unsafe_allow_html=True)
prompt_cols = st.columns(3)
_quick_send = None
for idx, prompt in enumerate(EXAMPLE_PROMPTS):
    with prompt_cols[idx % 3]:
        if st.button(prompt, key=f"quick_{idx}"):
            _quick_send = prompt
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Session state: chat history ───────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ── Load chatbot engine (cached in session) ───────────────────────────────────
@st.cache_resource(show_spinner=False)
def _get_chatbot():
    try:
        from utils.chatbot_engine import ChatbotEngine
        return ChatbotEngine()
    except Exception:
        return None

chatbot = _get_chatbot()


def _render_product_strip(products: list, palette: dict, strip_key: str = "strip"):
    """Render a grid of mini product cards inside a chat bubble."""
    if not products:
        return

    # Render up to 8 products in a 4-column grid (wraps to 2 rows natively)
    products_to_show = products[:8]
    num_cols = min(len(products_to_show), 4)
    cols = st.columns(num_cols)
    for i, prod in enumerate(products_to_show):
        with cols[i % num_cols]:
            st.markdown(render_product_card_html(prod, i, show_match=True),
                        unsafe_allow_html=True)
            pid = prod.get("product_id") or prod.get("asin", "")
            in_wish = pid in st.session_state.get("wishlist_ids", set())
            lbl = "\u2713 Saved" if in_wish else "+ Save"
            if st.button(lbl, key=f"chat_save_{strip_key}_{pid}_{i}", type="secondary",
                         use_container_width=True):
                try:
                    if not isinstance(st.session_state.get("wishlist_ids"), set):
                        st.session_state["wishlist_ids"] = set()
                    if in_wish:
                        from database.db_operations import remove_from_wishlist
                        remove_from_wishlist(user_id, pid)
                        st.session_state["wishlist_ids"].discard(pid)
                        st.toast("Removed from wishlist", icon="\u2705")
                    else:
                        from database.db_operations import add_to_wishlist
                        add_to_wishlist(user_id, pid,
                                        prod.get("title", ""),
                                        prod.get("price", 0),
                                        prod.get("category", ""))
                        st.session_state["wishlist_ids"].add(pid)
                        st.toast("\u2705 Saved to wishlist!", icon="\U0001f4be")
                    st.rerun()
                except Exception as _e:
                    st.toast(f"Error: {_e}", icon="\u274c")


# ── Premium SVG avatars for chat (no emojis) ─────────────────────────────────
_USER_AVATAR_SVG = (
    'data:image/svg+xml;utf8,'
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">'
    '<defs><linearGradient id="ug" x1="0%25" y1="0%25" x2="100%25" y2="100%25">'
    '<stop offset="0%25" stop-color="%236366f1"/>'
    '<stop offset="100%25" stop-color="%2306B6D4"/>'
    '</linearGradient></defs>'
    '<rect width="40" height="40" rx="12" fill="url(%23ug)"/>'
    '<circle cx="20" cy="15" r="6" fill="white" opacity="0.9"/>'
    '<path d="M10 33 a10 8 0 0 1 20 0" fill="white" opacity="0.9"/>'
    '</svg>'
)
_BOT_AVATAR_SVG = (
    'data:image/svg+xml;utf8,'
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">'
    '<defs><linearGradient id="bg" x1="0%25" y1="0%25" x2="100%25" y2="100%25">'
    '<stop offset="0%25" stop-color="%238b5cf6"/>'
    '<stop offset="100%25" stop-color="%236366f1"/>'
    '</linearGradient></defs>'
    '<rect width="40" height="40" rx="12" fill="url(%23bg)"/>'
    '<rect x="11" y="12" width="18" height="14" rx="4" fill="white" opacity="0.9"/>'
    '<circle cx="16" cy="18" r="2" fill="%236366f1"/>'
    '<circle cx="24" cy="18" r="2" fill="%236366f1"/>'
    '<rect x="15" y="22" width="10" height="2" rx="1" fill="%236366f1" opacity="0.5"/>'
    '<line x1="20" y1="8" x2="20" y2="12" stroke="white" stroke-width="2" stroke-linecap="round"/>'
    '<circle cx="20" cy="7" r="2" fill="white" opacity="0.8"/>'
    '</svg>'
)

for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"], avatar=_USER_AVATAR_SVG if msg["role"] == "user" else _BOT_AVATAR_SVG):
        st.markdown(msg["content"])
        if msg.get("products"):
            _render_product_strip(msg["products"], p, msg.get("strip_key", "hist"))


# ── Process quick prompt (clicked before chat input) ─────────────────────────
if _quick_send:
    st.session_state["_pending_prompt"] = _quick_send

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input(
    "Ask me anything — 'suggest laptops under ₹50,000', 'best beauty products'…",
    key="chat_main_input"
)

# Merge quick-send and typed input
if not user_input and st.session_state.get("_pending_prompt"):
    user_input = st.session_state.pop("_pending_prompt")

# ── Process message ───────────────────────────────────────────────────────────
if user_input:
    # Store user message
    st.session_state["chat_history"].append({
        "role": "user",
        "content": user_input,
    })

    with st.chat_message("user", avatar=_USER_AVATAR_SVG):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=_BOT_AVATAR_SVG):
        if chatbot is None:
            st.error("Chatbot engine failed to load. Please restart the app.")
        else:
            # Show minimal Meta AI style typing indicator
            _typing_ph = st.empty()
            _typing_ph.markdown(
                '<div class="meta-typing-box">'
                '<div class="meta-dot"></div><div class="meta-dot"></div><div class="meta-dot"></div>'
                '<span class="meta-text">AI is typing...</span>'
                '</div>',
                unsafe_allow_html=True
            )
            try:
                response = chatbot.respond(user_input, user_id)
            except Exception as e:
                response = {
                    "type": "error",
                    "text": "Something went wrong. Please try again.",
                    "products": [],
                }
            _typing_ph.empty()  # Clear typing indicator

            resp_type = response.get("type", "unknown")
            resp_text = response.get("text", "")
            products  = response.get("products", [])

            # Intent badge
            badge_map = {
                "greeting":       ("👋 Greeting",      "#6366f1", "rgba(99,102,241,0.08)"),
                "recommendation": ("🎯 Recommendation", "#6366f1", "rgba(99,102,241,0.08)"),
                "general":        ("💡 Knowledge",      "#10b981", "rgba(16,185,129,0.08)"),
                "unknown":        ("❓ Clarification",  "#f59e0b", "rgba(245,158,11,0.08)"),
                "error":          ("⚠️ Error",          "#ef4444", "rgba(239,68,68,0.08)"),
            }
            if resp_type in badge_map:
                badge_label, badge_color, badge_bg = badge_map[resp_type]
                st.markdown(
                    f'<span style="background:{badge_bg};color:{badge_color};'
                    f'padding:2px 10px;border-radius:100px;font-size:11px;font-weight:700;">'
                    f'{badge_label}</span>',
                    unsafe_allow_html=True
                )

            st.markdown(resp_text)

            # Render product strip if recommendations returned
            strip_key = f"new_{len(st.session_state['chat_history'])}"
            if products:
                st.markdown(f'<p style="font-size:12px;color:{p["text_muted"]};margin:8px 0 4px;">'
                            f'Top {len(products)} picks for you</p>',
                            unsafe_allow_html=True)
                _render_product_strip(products, p, strip_key)



            # Persist to chat history
            st.session_state["chat_history"].append({
                "role":     "assistant",
                "content":  resp_text,
                "products": products,
                "strip_key": strip_key,
            })

# ── Controls row ──────────────────────────────────────────────────────────────
if st.session_state["chat_history"]:
    st.markdown("---")
    ctrl_c1, ctrl_c2, ctrl_c3, _ = st.columns([1, 1, 1, 3])
    with ctrl_c1:
        if st.button("🗑 Clear Chat", key="chat_clear", type="secondary", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()
    with ctrl_c2:
        msg_count = len(st.session_state["chat_history"])
        st.markdown(
            f'<p style="font-size:12px;color:{p["text_muted"]};padding-top:8px;">'
            f'{msg_count} messages</p>',
            unsafe_allow_html=True
        )
    with ctrl_c3:
        if st.button("💡 For You page →", key="chat_goto_fy", type="secondary", use_container_width=True):
            st.switch_page("pages/02_For_You.py")

# ── Footer info ───────────────────────────────────────────────────────────────
grok_available = bool(os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY"))
engine_note = "Grok AI + IntelliRec engines" if grok_available else "IntelliRec AI engines (add GROK_API_KEY for Grok)"
st.markdown(f"""
<div style="text-align:center;padding:16px 0 6px;
            border-top:1px solid {p['border']};margin-top:16px;">
  <p style="font-size:11px;color:{p['text_muted']};margin:0;">
    Powered by {engine_note} &middot; Sourcesys Technologies
  </p>
</div>""", unsafe_allow_html=True)
