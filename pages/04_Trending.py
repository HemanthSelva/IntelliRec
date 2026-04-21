import streamlit as st
import json
import pandas as pd
import plotly.express as px
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.helpers import get_sentiment_style, get_category_info

st.set_page_config(page_title="Trending | IntelliRec", page_icon="💡", layout="wide")
check_login()
from utils.theme import inject_global_css
inject_global_css()
render_sidebar("trending")

@st.cache_data
def load_products():
    with open("assets/sample_products.json", "r") as f:
        return json.load(f)

products = load_products()
df = pd.DataFrame(products)

# ── Top Bar ───────────────────────────────────────────────────────────────────
render_topbar("What's Hot Right Now", "Discover what the IntelliRec community is loving")

# ── Time filter ───────────────────────────────────────────────────────────────
tf_col, _ = st.columns([2, 5])
with tf_col:
    time_filter = st.radio("Time", ["Today", "This Week", "This Month"],
                           horizontal=True, label_visibility="collapsed",
                           key="trend_time")

# Simulate different trending sets per time filter
if time_filter == "Today":
    trend_df = df[df['is_trending'] == True]
elif time_filter == "This Week":
    trend_df = df[df['rating'] >= 3.5].head(15)
else:
    trend_df = df[df['rating'] >= 3.0].head(20)

if trend_df.empty:
    trend_df = df.head(10)

# ── Stats bar ─────────────────────────────────────────────────────────────────
top_cat = trend_df['category'].value_counts().idxmax() if not trend_df.empty else "—"
avg_rating = round(trend_df['rating'].mean(), 1) if not trend_df.empty else 0

# SVG icons
_SVG_TREND = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
  viewBox="0 0 24 24" stroke="#6C63FF" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
  <polyline points="17 6 23 6 23 12"/></svg>"""

_SVG_STAR_STAT = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="#F59E0B"
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
for col, icon_svg, val, label, bg, border in [
    (sc1, _SVG_TREND,    len(trend_df), "Trending Products", "#EEF2FF", "#6C63FF"),
    (sc2, _SVG_STAR_STAT, avg_rating,   "Avg Rating",        "#FFFBEB", "#F59E0B"),
    (sc3, _SVG_AWARD,    top_cat,       "Top Category",      "#ECFDF5", "#10B981"),
]:
    with col:
        st.markdown(f"""
<div style="background:var(--stat-card-bg,rgba(255,255,255,0.9));backdrop-filter:blur(20px);
            -webkit-backdrop-filter:blur(20px);
            border:1px solid var(--border-color,rgba(108,99,255,0.12));border-left:3px solid {border};
            border-radius:14px;padding:16px 20px;
            display:flex;align-items:center;gap:14px;margin-bottom:24px;
            box-shadow:0 2px 8px rgba(108,99,255,0.08);">
  <div style="width:48px;height:48px;border-radius:12px;background:{bg};
              display:flex;align-items:center;justify-content:center;flex-shrink:0;">
    {icon_svg}
  </div>
  <div>
    <div style="font-size:20px;font-weight:700;color:var(--text-primary,#111827)">{val}</div>
    <div style="font-size:12px;color:var(--text-secondary,#9CA3AF)">{label}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<p style="font-size:13px;font-weight:600;color:#374151;margin-bottom:4px">Category Split</p>',
                unsafe_allow_html=True)
    cat_counts = trend_df['category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    fig1 = px.pie(cat_counts, values='Count', names='Category', hole=0.45,
                  color_discrete_sequence=['#6C63FF', '#06B6D4', '#10B981', '#F59E0B'],
                  template="plotly_white")
    fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter'), showlegend=True,
                       legend=dict(font=dict(size=11)))
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown('<p style="font-size:13px;font-weight:600;color:#374151;margin-bottom:4px">Sentiment</p>',
                unsafe_allow_html=True)
    sent_counts = trend_df['sentiment_label'].value_counts().reset_index()
    sent_counts.columns = ['Sentiment', 'Count']
    fig2 = px.bar(sent_counts, x='Sentiment', y='Count', color='Sentiment',
                  color_discrete_map={
                      'Positive': '#10B981', 'Mixed': '#F59E0B', 'Critical': '#EF4444'
                  }, template="plotly_white")
    fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False,
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter'))
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    st.markdown('<p style="font-size:13px;font-weight:600;color:#374151;margin-bottom:4px">Price Range</p>',
                unsafe_allow_html=True)
    fig3 = px.histogram(trend_df, x='price', nbins=8,
                        color_discrete_sequence=['#6C63FF'], template="plotly_white")
    fig3.update_layout(margin=dict(t=0, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter'),
                       xaxis_title='Price ($)', yaxis_title='Count')
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown('<p style="font-size:13px;font-weight:600;color:#374151;margin-bottom:4px">Rating Distribution</p>',
                unsafe_allow_html=True)
    fig4 = px.histogram(trend_df, x='rating', nbins=8,
                        color_discrete_sequence=['#06B6D4'], template="plotly_white")
    fig4.update_layout(margin=dict(t=0, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter'),
                       xaxis_title='Rating', yaxis_title='Count')
    st.plotly_chart(fig4, use_container_width=True)

# ── Top 10 list ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<h2 style="font-size:20px;font-weight:700;color:#111827;margin-bottom:16px">Top 10 Trending</h2>',
            unsafe_allow_html=True)

top_10 = (trend_df
          .sort_values(by=['rating', 'sentiment_score'], ascending=[False, False])
          .head(10)
          .reset_index(drop=True))

for i, row in top_10.iterrows():
    sent = get_sentiment_style(row.get('sentiment_label', ''))
    cat = get_category_info(row.get('category', ''))
    rank_color = ['#FFD700', '#C0C0C0', '#CD7F32']
    badge_bg = rank_color[i] if i < 3 else '#EEF2FF'
    badge_color = '#111827' if i < 3 else '#6C63FF'

    col_rank, col_info, col_btn = st.columns([0.6, 5, 1.5])

    with col_rank:
        st.markdown(f"""
<div style="width:36px;height:36px;border-radius:50%;background:{badge_bg};
            display:flex;align-items:center;justify-content:center;
            font-size:15px;font-weight:700;color:{badge_color};margin-top:6px">
  #{i + 1}
</div>""", unsafe_allow_html=True)

    with col_info:
        trend_arrow = "arrow_upward" if i < 5 else "arrow_forward"
        st.markdown(f"""
<div class="trending-item">
  <p class="product-title">
    {row['title'][:70]}{'…' if len(row['title']) > 70 else ''}
    <span class="material-icons" style="font-size:16px;color:#10B981;margin-left:6px;vertical-align:middle;">{trend_arrow}</span>
  </p>
  <p class="product-price">
    <strong style="color:#F59E0B">&#9733; {row['rating']}</strong>
    ({int(row['review_count']):,} reviews) &middot;
    <strong>${row['price']:.2f}</strong> &middot;
    <span style="background:{cat['badge_bg']};color:{cat['badge_text']};
                 font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px">
      {row['category']}
    </span>
    <span style="background:{sent['bg']};color:{sent['color']};
                 font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px;
                 margin-left:4px">
      {row['sentiment_label']}
    </span>
  </p>
</div>""", unsafe_allow_html=True)

    with col_btn:
        with st.expander("Why trending?"):
            st.write(f"High rating of {row['rating']} with {int(row['review_count']):,} "
                     f"reviews and {row['sentiment_label'].lower()} community sentiment "
                     f"in {row['category']}.")

    st.markdown('<hr style="margin:6px 0;border:none;border-top:1px solid rgba(108,99,255,0.08)">',
                unsafe_allow_html=True)
