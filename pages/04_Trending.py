import streamlit as st
import json
import os
import sys
import pandas as pd
import plotly.express as px
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.helpers import get_sentiment_style, get_category_info, maybe_show_product_dialog
from utils.model_loader import MODELS_READY, get_trending

st.set_page_config(page_title="Trending | IntelliRec", page_icon="💡", layout="wide", initial_sidebar_state="expanded")
check_login()

# ── Theme + palette ───────────────────────────────────────────────────────────
from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'light')
p = get_palette(theme)
inject_global_css(p)

render_sidebar("trending")

# Chart label color derived from palette
_label_col = p['text_primary']

# ── ANIMATION 4: Fire/Hot streak effect + Trending Ticker ──
st.markdown("""
<style>
@keyframes rankBounce {
    0%,100% { transform: scale(1); }
    50%      { transform: scale(1.1); }
}
@keyframes scrollTicker {
    from { transform: translateX(100%); }
    to   { transform: translateX(-100%); }
}
.rank-1-badge, .rank-2-badge, .rank-3-badge {
    animation: rankBounce 3s ease-in-out infinite;
    display: inline-block;
}
.rank-1-row {
    border-left: 4px solid #f59e0b !important;
    background: linear-gradient(135deg, rgba(245,158,11,0.08), transparent) !important;
    border-radius: 12px;
    padding-left: 8px;
}
.trending-ticker-wrapper {
    overflow: hidden; white-space: nowrap;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 8px; padding: 8px 0; margin-bottom: 16px;
}
.trending-ticker {
    display: inline-block; padding: 0 40px;
    animation: scrollTicker 20s linear infinite;
    color: white; font-size: 13px; font-weight: 500;
}
</style>
<div class="trending-ticker-wrapper">
  <span class="trending-ticker">
    🔥 TRENDING NOW · Real-time data from 1.4M+ products ·
    Updated every session · Powered by IntelliRec AI ·
    3 engines active · Community-driven recommendations 🚀
  </span>
</div>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_sample_products():
    try:
        with open("assets/sample_products.json", "r") as f:
            return json.load(f)
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=600)
def load_trending_pool(_hour_seed: int = 0) -> pd.DataFrame:
    """Return a large trending pool; _hour_seed busts cache each hour for variation."""
    if MODELS_READY:
        df = get_trending(n=200)
        if not df.empty:
            return df
    # Fallback to JSON sample
    prods = load_sample_products()
    return pd.DataFrame(prods) if prods else pd.DataFrame()


def apply_category_diversity(df: pd.DataFrame, max_per_cat: int = 3, total: int = 10) -> pd.DataFrame:
    """Limit products per category to ensure diversity in the trending list."""
    result = []
    cat_counts = {}
    for _, row in df.iterrows():
        cat = str(row.get('category', 'Electronics'))
        count = cat_counts.get(cat, 0)
        if count < max_per_cat:
            result.append(row)
            cat_counts[cat] = count + 1
        if len(result) >= total:
            break
    if len(result) < total:
        # Fill remaining with best remaining products
        used_indices = {r.name for r in result}
        remaining = df[~df.index.isin(used_indices)]
        for _, row in remaining.iterrows():
            result.append(row)
            if len(result) >= total:
                break
    return pd.DataFrame(result)


products = load_sample_products()  # keep for compatibility
_now = datetime.now()
_hour_seed = _now.hour * 100 + _now.day
df = load_trending_pool(_hour_seed)

if df.empty:
    df = pd.DataFrame(load_sample_products())

# ── Top Bar ───────────────────────────────────────────────────────────────────
render_topbar("What's Hot Right Now", "Discover what the IntelliRec community is loving")
maybe_show_product_dialog()

# ── Time filter ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* High contrast and professional styling for the Time Filter radio buttons */
div.stRadio > div[role="radiogroup"] > label p {{
    color: {p['text_primary']} !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 0.3px !important;
    font-family: 'Inter', sans-serif !important;
}}
/* Make the unselected radio buttons slightly muted but still highly readable */
div.stRadio > div[role="radiogroup"] > label:not([data-checked="true"]) p {{
    color: {p['text_secondary']} !important;
    font-weight: 600 !important;
}}
/* Subtle hover effect */
div.stRadio > div[role="radiogroup"] > label:hover p {{
    color: {p['accent']} !important;
}}
</style>
""", unsafe_allow_html=True)

tf_col, _ = st.columns([3, 5])
with tf_col:
    time_filter = st.radio("Time", ["Today", "This Week", "This Month"],
                           horizontal=True, label_visibility="collapsed",
                           key="trend_time")

# ── Build time-filtered trending set ────────────────────────────────────────
# Different time filters use different scoring formulas and pool sizes
# to produce genuinely distinct product lists.

if time_filter == "Today":
    n_products = 10
    # Smaller pool, review_count-heavy scoring (highest momentum)
    df_pool = df.head(min(200, len(df))).copy()
    if not df_pool.empty:
        max_rc = df_pool['review_count'].max() or 1
        df_pool['time_score'] = (
            df_pool['review_count'] / max_rc * 0.7 +
            df_pool['rating'] / 5.0 * 0.3
        )
        trend_df = df_pool.nlargest(n_products * 3, 'time_score')
    else:
        trend_df = df_pool

elif time_filter == "This Week":
    n_products = 15
    # Medium pool, balanced scoring
    df_pool = df.head(min(200, len(df))).copy()
    if not df_pool.empty:
        max_rc = df_pool['review_count'].max() or 1
        df_pool['time_score'] = (
            df_pool['review_count'] / max_rc * 0.5 +
            df_pool['rating'] / 5.0 * 0.5
        )
        trend_df = df_pool.nlargest(n_products * 3, 'time_score')
    else:
        trend_df = df_pool

else:  # This Month
    n_products = 20
    # Large pool, rating-heavy scoring (more diverse / quality-focused)
    df_pool = df.copy()
    if not df_pool.empty:
        max_rc = df_pool['review_count'].max() or 1
        df_pool['time_score'] = (
            df_pool['review_count'] / max_rc * 0.3 +
            df_pool['rating'] / 5.0 * 0.7
        )
        trend_df = df_pool.nlargest(n_products * 3, 'time_score')
    else:
        trend_df = df_pool

# Apply category diversity: max 3 products per category
if not trend_df.empty:
    trend_df = apply_category_diversity(trend_df, max_per_cat=3, total=n_products)
    # Shuffle top candidates slightly so each session feels fresh
    _shuffle_seed = _hour_seed + ({"Today": 0, "This Week": 7, "This Month": 31}.get(time_filter, 0))
    trend_df = trend_df.sample(frac=1, random_state=_shuffle_seed % 999).reset_index(drop=True)

if trend_df.empty:
    trend_df = df.head(10)

# ── Stats bar ─────────────────────────────────────────────────────────────────
top_cat = trend_df['category'].value_counts().idxmax() if not trend_df.empty else "—"
avg_rating = round(trend_df['rating'].mean(), 1) if not trend_df.empty else 0

_SVG_TREND = f"""<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
  viewBox="0 0 24 24" stroke="{p['accent']}" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
  <polyline points="17 6 23 6 23 12"/></svg>"""

_SVG_STAR_STAT = f"""<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="{p['star_color']}"
  viewBox="0 0 24 24">
  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
</svg>"""

_SVG_AWARD = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
  viewBox="0 0 24 24" stroke="#10B981" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="8" r="6"/>
  <path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/>
</svg>"""

sc1, sc2, sc3 = st.columns(3)
for col, icon_svg, val, label, icon_bg, border_color in [
    (sc1, _SVG_TREND,     len(trend_df), "Trending Products", p['icon_bg_purple'], p['accent']),
    (sc2, _SVG_STAR_STAT, avg_rating,    "Avg Rating",        p['icon_bg_amber'],  p['star_color']),
    (sc3, _SVG_AWARD,     top_cat,       "Top Category",      p['icon_bg_green'],  "#10b981"),
]:
    with col:
        st.markdown(f"""
<div style="background-color:{p['stat_card_bg']};
            border:1px solid {p['border']};border-left:3px solid {border_color};
            border-radius:14px;padding:16px 20px;
            display:flex;align-items:center;gap:14px;margin-bottom:24px;
            box-shadow:{p['shadow']};">
  <div style="width:48px;height:48px;border-radius:12px;background-color:{icon_bg};
              display:flex;align-items:center;justify-content:center;flex-shrink:0;">
    {icon_svg}
  </div>
  <div>
    <div style="font-size:20px;font-weight:700;color:{p['text_primary']}">{val}</div>
    <div style="font-size:12px;color:{p['text_secondary']}">{label}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<p style="font-size:13px;font-weight:600;color:{p["text_primary"]};margin-bottom:4px">Category Split</p>',
                unsafe_allow_html=True)
    cat_counts = trend_df['category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    fig1 = px.pie(cat_counts, values='Count', names='Category', hole=0.45,
                  color_discrete_sequence=['#6366f1', '#06B6D4', '#10B981', '#F59E0B'],
                  template="plotly_white")
    fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter', color=_label_col), showlegend=True,
                       legend=dict(font=dict(size=11, color=_label_col)))
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown(f'<p style="font-size:13px;font-weight:600;color:{p["text_primary"]};margin-bottom:4px">Sentiment</p>',
                unsafe_allow_html=True)
    sent_counts = trend_df['sentiment_label'].value_counts().reset_index()
    sent_counts.columns = ['Sentiment', 'Count']
    fig2 = px.bar(sent_counts, x='Sentiment', y='Count', color='Sentiment',
                  color_discrete_map={
                      'Positive': '#10B981', 'Mixed': '#F59E0B', 'Critical': '#EF4444'
                  }, template="plotly_white")
    fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False,
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter', color=_label_col))
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    st.markdown(f'<p style="font-size:13px;font-weight:600;color:{p["text_primary"]};margin-bottom:4px">Price Range</p>',
                unsafe_allow_html=True)
    fig3 = px.histogram(trend_df, x='price', nbins=8,
                        color_discrete_sequence=['#6366f1'], template="plotly_white")
    fig3.update_layout(margin=dict(t=0, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter', color=_label_col),
                       xaxis_title='Price ($)', yaxis_title='Count')
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown(f'<p style="font-size:13px;font-weight:600;color:{p["text_primary"]};margin-bottom:4px">Rating Distribution</p>',
                unsafe_allow_html=True)
    fig4 = px.histogram(trend_df, x='rating', nbins=8,
                        color_discrete_sequence=['#06B6D4'], template="plotly_white")
    fig4.update_layout(margin=dict(t=0, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter', color=_label_col),
                       xaxis_title='Rating', yaxis_title='Count')
    st.plotly_chart(fig4, use_container_width=True)

# ── Top Trending list ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f'<h2 style="font-size:20px;font-weight:700;color:{p["text_primary"]};margin-bottom:16px">Top {len(trend_df)} Trending</h2>',
            unsafe_allow_html=True)

# Rank column — always use time_score which was computed for the active filter
_rank_col = 'time_score' if 'time_score' in trend_df.columns else 'trend_score'

top_list = (
    trend_df
    .sort_values(by=_rank_col, ascending=False)
    .head(n_products)
    .reset_index(drop=True)
)

for i, row in top_list.iterrows():
    sent = get_sentiment_style(row.get('sentiment_label', ''))
    cat = get_category_info(row.get('category', ''))
    rank_color = ['#FFD700', '#C0C0C0', '#CD7F32']
    badge_bg = rank_color[i] if i < 3 else p['accent_soft']
    badge_color = p['text_primary'] if i < 3 else p['accent']

    col_rank, col_info, col_btn = st.columns([0.6, 5, 1.5])

    with col_rank:
        st.markdown(f"""
<div style="width:36px;height:36px;border-radius:50%;background-color:{badge_bg};
            display:flex;align-items:center;justify-content:center;
            font-size:15px;font-weight:700;color:{badge_color};margin-top:6px">
  #{i + 1}
</div>""", unsafe_allow_html=True)

    with col_info:
        if i < 5:
            dir_html = '<span style="color:#10b981;font-size:13px;font-weight:700;margin-left:6px;">▲</span>'
        else:
            dir_html = '<span style="color:#6b7280;font-size:13px;margin-left:6px;">→</span>'
        _ellipsis = "…" if len(row['title']) > 70 else ""
        _title_short = row['title'][:70] + _ellipsis
        _row_class = "trending-item rank-1-row" if i == 0 else "trending-item"
        st.markdown(f"""
<div class="{_row_class}">
  <p class="product-title">
    {_title_short}
    {dir_html}
  </p>
  <p class="product-price">
    <strong style="color:{p['star_color']}">★ {row['rating']}</strong>
    ({int(row['review_count']):,} reviews) &middot;
    <strong style="color:{p['text_primary']}">{f"${float(row['price']):.2f}" if float(row.get('price') or 0) > 0 else 'Price unavailable'}</strong> &middot;
    <span style="background-color:{cat['badge_bg']};color:{cat['badge_text']};
                 font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px">
      {row['category']}
    </span>
    <span style="background-color:{sent['bg']};color:{sent['color']};
                 font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px;
                 margin-left:4px">
      {row['sentiment_label']}
    </span>
  </p>
</div>""", unsafe_allow_html=True)

    with col_btn:
        # ── Trend Insight badge (replaces plain expander) ────────────────
        _ts   = float(row.get('trend_score', row.get('_week_score', row.get('_month_score', 0))) or 0)
        _pct  = min(100, max(4, int(round(_ts * 100))))
        _sent_color = {
            'Positive': '#10b981', 'Mixed': '#f59e0b', 'Critical': '#ef4444'
        }.get(str(row.get('sentiment_label', 'Mixed')), '#f59e0b')
        st.markdown(f"""
<div style="
    background: linear-gradient(135deg, rgba(99,102,241,0.07), rgba(139,92,246,0.05));
    border: 1px solid rgba(99,102,241,0.18);
    border-left: 3px solid {_sent_color};
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 11px;
    color: {p['text_secondary']};
    line-height: 1.7;
">
  <div style="font-size:10px;font-weight:700;color:{p['accent']};letter-spacing:0.6px;margin-bottom:5px;">
    🔥 TREND SCORE
  </div>
  <div style="width:100%;height:5px;background:rgba(99,102,241,0.12);border-radius:99px;margin-bottom:6px;">
    <div style="width:{_pct}%;height:5px;background:linear-gradient(90deg,#6366f1,#f59e0b);border-radius:99px;"></div>
  </div>
  <span style="font-weight:600;color:{p['text_primary']}">#{i+1} ranked</span> &middot;
  <span style="color:{_sent_color};font-weight:600">{row.get('sentiment_label','Mixed')}</span><br>
  <span style="color:{p['text_muted']}">{int(row['review_count']):,} reviews &middot; ★ {row['rating']}</span>
</div>""", unsafe_allow_html=True)
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        _row_dict = row.to_dict() if hasattr(row, 'to_dict') else dict(row)
        if st.button("Details", key=f"tr_det_{i}", type="secondary", use_container_width=True):
            st.session_state["view_product"] = _row_dict
            st.session_state["_view_product_triggered"] = True
            st.rerun()

    st.markdown(f'<hr style="margin:6px 0;border:none;border-top:1px solid {p["border"]}">',
                unsafe_allow_html=True)
