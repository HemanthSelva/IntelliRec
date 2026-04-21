import streamlit as st
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar

st.set_page_config(page_title="About | IntelliRec", page_icon="💡", layout="wide")
check_login()
from utils.theme import inject_global_css
inject_global_css()
render_sidebar("about")

# ── Top Bar ───────────────────────────────────────────────────────────────────
render_topbar("About IntelliRec", "Discover what powers your AI recommendations")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

st.markdown("""
<div style="background:rgba(255,255,255,0.78);backdrop-filter:blur(20px);
            -webkit-backdrop-filter:blur(20px);
            border:1px solid rgba(255,255,255,0.6);border-radius:20px;
            padding:24px;margin-bottom:24px;box-shadow:0 4px 20px rgba(108,99,255,0.12);">
  <p style="font-size:15px;color:#374151;line-height:1.8;margin:0">
    <strong>IntelliRec</strong> is an intelligent, AI-powered product recommendation platform
    combining multiple cutting-edge ML algorithms, sentiment analysis, explainable AI, and an
    enterprise-grade UI to deliver hyper-personalised shopping recommendations.
    Built as an internship project at <strong>Sourcesys Technologies</strong> using a
    triple-engine architecture similar to what top-tier e-commerce platforms use internally.
  </p>
</div>""", unsafe_allow_html=True)

# ── How It Works ──────────────────────────────────────────────────────────────
st.markdown('<h2 style="font-size:20px;font-weight:700;color:#111827;margin-bottom:16px">How It Works</h2>',
            unsafe_allow_html=True)

# SVG step icons
_SVG_LOCK = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
  viewBox="0 0 24 24" stroke="#6C63FF" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
  <path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>"""

_SVG_SLIDERS = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
  viewBox="0 0 24 24" stroke="#6C63FF" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <line x1="4" y1="21" x2="4" y2="14"/>
  <line x1="4" y1="10" x2="4" y2="3"/>
  <line x1="12" y1="21" x2="12" y2="12"/>
  <line x1="12" y1="8" x2="12" y2="3"/>
  <line x1="20" y1="21" x2="20" y2="16"/>
  <line x1="20" y1="12" x2="20" y2="3"/>
  <line x1="1" y1="14" x2="7" y2="14"/>
  <line x1="9" y1="8" x2="15" y2="8"/>
  <line x1="17" y1="16" x2="23" y2="16"/></svg>"""

_SVG_SPARKLE = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
  viewBox="0 0 24 24" stroke="#6C63FF" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
</svg>"""

steps = [
    ("1", _SVG_LOCK,    "Sign Up",
     "Create a free account in seconds. Tell us who you are — we handle the rest."),
    ("2", _SVG_SLIDERS, "Set Preferences",
     "Pick your favourite categories, price range, and recommendation style during onboarding."),
    ("3", _SVG_SPARKLE, "Get Personalised Picks",
     "Our three AI engines collaborate to serve hyper-relevant recommendations, updated in real-time."),
]

s1, s2, s3 = st.columns(3)
for col, (num, icon_svg, title, desc) in zip([s1, s2, s3], steps):
    with col:
        st.markdown(f"""
<div style="background:rgba(255,255,255,0.78);backdrop-filter:blur(20px);
            -webkit-backdrop-filter:blur(20px);
            border:1px solid rgba(255,255,255,0.6);border-radius:20px;
            padding:24px;text-align:center;height:100%;
            box-shadow:0 4px 20px rgba(108,99,255,0.12);">
  <div style="width:44px;height:44px;border-radius:50%;background:#EEF2FF;
       display:flex;align-items:center;justify-content:center;
       font-size:18px;font-weight:700;color:#6C63FF;margin:0 auto 12px">{num}</div>
  <div style="display:flex;align-items:center;justify-content:center;margin-bottom:10px;">
    {icon_svg}
  </div>
  <p style="font-size:15px;font-weight:700;color:#111827;margin-bottom:8px">{title}</p>
  <p style="font-size:13px;color:#6B7280;line-height:1.6;margin:0">{desc}</p>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Features ──────────────────────────────────────────────────────────────────
st.markdown('<h2 style="font-size:20px;font-weight:700;color:#111827;margin-bottom:16px">Unique Features</h2>',
            unsafe_allow_html=True)

# Feature SVGs
_SVG_SWITCH = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/>
  <polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>
</svg>"""

_SVG_LIGHTBULB = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <line x1="9" y1="18" x2="15" y2="18"/>
  <line x1="10" y1="22" x2="14" y2="22"/>
  <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>
</svg>"""

_SVG_ROCKET = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
  <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>
  <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>
  <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>
</svg>"""

_SVG_SMILE = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <path d="M8 13s1.5 2 4 2 4-2 4-2"/>
  <line x1="9" y1="9" x2="9.01" y2="9"/>
  <line x1="15" y1="9" x2="15.01" y2="9"/>
</svg>"""

_SVG_CHART_BAR = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <line x1="18" y1="20" x2="18" y2="10"/>
  <line x1="12" y1="20" x2="12" y2="4"/>
  <line x1="6" y1="20" x2="6" y2="14"/>
  <line x1="2" y1="20" x2="22" y2="20"/>
</svg>"""

_SVG_GLOBE = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="2" y1="12" x2="22" y2="12"/>
  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
</svg>"""

fc1, fc2 = st.columns(2)
features_left = [
    (_SVG_SWITCH,    "Triple-Engine Architecture",
     "Seamlessly switching between SVD Collaborative, TF-IDF Content-Based, and Sentiment-Aware Hybrid models."),
    (_SVG_LIGHTBULB, "Explainable AI",
     "Understand exactly why a product was recommended through dynamic transparency hints."),
    (_SVG_ROCKET,    "Smart Cold Start Solver",
     "Interactive onboarding and popularity fallbacks ensure great picks for brand-new users."),
]
features_right = [
    (_SVG_SMILE,     "Sentiment Intelligence",
     "VADER sentiment scoring on reviews prioritises qualitative satisfaction over raw ratings."),
    (_SVG_CHART_BAR, "Dynamic Match Scores",
     "Real-time personalisation percentages updated with every interaction and rating."),
    (_SVG_GLOBE,     "Filter Bubble Prevention",
     "Diversity controllers ensure a healthy breadth of category exposure."),
]

for col, features in [(fc1, features_left), (fc2, features_right)]:
    with col:
        for icon_svg, title, desc in features:
            st.markdown(f"""
<div style="background:rgba(255,255,255,0.78);backdrop-filter:blur(20px);
            -webkit-backdrop-filter:blur(20px);
            border:1px solid rgba(255,255,255,0.6);border-radius:16px;
            padding:16px 18px;margin-bottom:12px;display:flex;gap:14px;
            align-items:flex-start;box-shadow:0 2px 8px rgba(108,99,255,0.08);">
  <div style="color:#6C63FF;flex-shrink:0;margin-top:2px;">{icon_svg}</div>
  <div>
    <p style="font-weight:600;font-size:14px;color:#111827;margin-bottom:4px">{title}</p>
    <p style="font-size:13px;color:#6B7280;line-height:1.6;margin:0">{desc}</p>
  </div>
</div>""", unsafe_allow_html=True)

# ── Tech Stack ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<h2 style="font-size:20px;font-weight:700;color:#111827;margin-bottom:14px">Tech Stack</h2>',
            unsafe_allow_html=True)

tech = [
    ("Python", "#3776AB", "white"),
    ("Streamlit", "#FF4B4B", "white"),
    ("Supabase", "#3ECF8E", "white"),
    ("scikit-learn", "#F7931E", "white"),
    ("VADER Sentiment", "#6C63FF", "white"),
    ("Plotly", "#3F4F75", "white"),
    ("Pandas", "#130754", "white"),
]
badges = " ".join([
    f'<span style="background:{bg};color:{color};font-size:13px;font-weight:600;'
    f'padding:5px 14px;border-radius:20px;display:inline-block;margin:4px 4px 4px 0">'
    f'{name}</span>'
    for name, bg, color in tech
])
st.markdown(f'<div style="margin-bottom:8px">{badges}</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;
            padding:12px 16px;margin-top:12px;font-size:13px;color:#92400E">
  <strong>Dataset:</strong> Amazon Reviews 2023 — McAuley Lab, UCSD &middot;
  1.4M products &middot; 7.8M ratings
</div>""", unsafe_allow_html=True)

# ── Team ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<h2 style="font-size:20px;font-weight:700;color:#111827;margin-bottom:6px">The Team</h2>',
            unsafe_allow_html=True)
st.markdown('<p style="font-size:14px;color:#6B7280;margin-bottom:20px">Engineering quartet at <strong style="color:#111827">Sourcesys Technologies</strong></p>',
            unsafe_allow_html=True)

team = [
    {"name": "Hemanthselva A K", "role": "Team Lead & Full-Stack AI", "init": "HA", "color": "#6C63FF"},
    {"name": "Monish Kaarthi R K", "role": "ML Engineer",             "init": "MK", "color": "#06B6D4"},
    {"name": "Vishal K S",         "role": "Data Scientist",           "init": "VK", "color": "#10B981"},
    {"name": "Vishal M",           "role": "Backend Developer",        "init": "VM", "color": "#F59E0B"},
]

tc = st.columns(4)
for col, m in zip(tc, team):
    with col:
        st.markdown(f"""
<div style="background:rgba(255,255,255,0.78);backdrop-filter:blur(20px);
            -webkit-backdrop-filter:blur(20px);
            border:1px solid rgba(255,255,255,0.6);border-radius:20px;
            padding:24px;text-align:center;
            box-shadow:0 4px 20px rgba(108,99,255,0.12);">
  <div style="width:60px;height:60px;border-radius:50%;
       background:linear-gradient(135deg,{m['color']},#06B6D4);
       color:white;display:flex;align-items:center;justify-content:center;
       font-size:1.3rem;font-weight:700;margin:0 auto 12px">
    {m['init']}
  </div>
  <p style="font-weight:600;font-size:14px;color:#111827;margin-bottom:4px">{m['name']}</p>
  <p style="font-size:12px;color:{m['color']};font-weight:500;margin:0">{m['role']}</p>
</div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:16px 0;border-top:1px solid rgba(108,99,255,0.12)">
  <p style="font-size:13px;color:#9CA3AF">
    Built with care using Streamlit &middot; scikit-learn &middot; Supabase &middot; Plotly
  </p>
</div>""", unsafe_allow_html=True)
