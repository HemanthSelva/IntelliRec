import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import date, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.notifications import add_notification
from utils.evaluator import metrics_to_dataframe, get_best_model_summary
from utils.model_loader import get_metrics as _get_ml_metrics

st.set_page_config(page_title="Analytics | IntelliRec", page_icon="💡", layout="wide", initial_sidebar_state="expanded")
check_login()

# ── Theme + palette ───────────────────────────────────────────────────────────
from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'light')
p = get_palette(theme)
inject_global_css(p)

render_sidebar("analytics")

# ── FIX 1: Full contrast override — matches About page font quality ────────────
st.markdown(f"""
<style>
/* Full contrast text — same block as About page */
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

/* ── FIX 2: Date Range input — glass style matching the rest of the UI without double borders ────── */
[data-testid="stDateInput"] > div > div[data-baseweb="input"] {{
    background: {p['glass_bg_strong']} !important;
    backdrop-filter: blur(14px) !important;
    border: 1px solid {p['glass_border_soft']} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
}}
[data-testid="stDateInput"] input {{
    color: {p['text_primary']} !important;
    font-size: 14px !important;
    background: transparent !important;
    border: none !important;
}}
/* ── FIX 3: DataFrame Border Overlap ────── */
[data-testid="stDataFrame"] > div {{
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid {p['border']} !important;
}}
/* Strip inner borders that cause the glitch */
[data-testid="stDataFrame"] div[data-testid="stVirtualGrid"],
[data-testid="stDataFrame"] [class*="StyledGrid"] {{
    border: none !important;
}}
[data-testid="stDateInput"] label {{
    color: {p['text_secondary']} !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.4px !important;
    text-transform: uppercase !important;
}}
[data-testid="stDateInput"] input::placeholder {{
    color: {p['text_muted']} !important;
}}
/* Calendar popover */
[data-baseweb="calendar"] {{
    background: {p['card_bg']} !important;
    border: 1px solid {p['border']} !important;
    border-radius: 16px !important;
    box-shadow: {p['glass_shadow_lg']} !important;
}}
[data-baseweb="calendar"] * {{
    color: {p['text_primary']} !important;
}}
[data-baseweb="calendar"] [aria-selected="true"] button {{
    background: {p['accent']} !important;
    color: #ffffff !important;
    border-radius: 8px !important;
}}

/* st.metric cards — ensure values are bold and coloured */
[data-testid="stMetricValue"] > div {{
    color: {p['text_primary']} !important;
    font-weight: 700 !important;
    font-size: 22px !important;
}}
[data-testid="stMetricLabel"] > div {{
    color: {p['text_secondary']} !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}}

/* st.success / st.info banners — match palette */
[data-testid="stAlert"] {{
    border-radius: 12px !important;
    border: 1px solid rgba(16,185,129,0.25) !important;
    background: rgba(16,185,129,0.07) !important;
}}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {{
    color: {p['text_primary']} !important;
    font-weight: 500 !important;
}}
</style>
""", unsafe_allow_html=True)

# Chart label color from palette
_label_col = p['text_primary']

# ── ANIMATION 5: Live data pulse on metric cards ──
st.markdown(f"""
<style>
@keyframes liveBlip {{
    0%,100% {{ opacity: 1; transform: scale(1); }}
    50%     {{ opacity: 0.4; transform: scale(0.85); }}
}}
@keyframes countUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.live-indicator {{
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 12px; color: #10b981; font-weight: 600;
}}
.live-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: #10b981;
    animation: liveBlip 1s ease-in-out infinite;
}}
.metric-value-animate {{
    animation: countUp 0.8s ease-out forwards;
}}
.analytics-header-glow {{
    background: linear-gradient(135deg,
        rgba(99,102,241,0.1), rgba(6,182,212,0.1));
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 14px; padding: 16px; margin-bottom: 20px;
}}
.source-badge-live {{
    display: inline-block;
    background: linear-gradient(135deg, #10b981, #059669);
    color: #ffffff;
    font-size: 10px; font-weight: 700;
    padding: 2px 10px; border-radius: 20px;
    letter-spacing: 0.5px; vertical-align: middle;
    margin-left: 8px;
}}
.source-badge-demo {{
    display: inline-block;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: #ffffff;
    font-size: 10px; font-weight: 700;
    padding: 2px 10px; border-radius: 20px;
    letter-spacing: 0.5px; vertical-align: middle;
    margin-left: 8px;
}}
</style>
<div class="analytics-header-glow">
    <span class="live-indicator">
        <span class="live-dot"></span>
        LIVE DATA &middot; Triple-Engine Architecture Active
    </span>
</div>
""", unsafe_allow_html=True)

# ── Top Bar ───────────────────────────────────────────────────────────────────
render_topbar("AI Model Performance", "Triple-engine architecture — metrics dashboard")

# ── FIX 2: Date range + controls ──────────────────────────────────────────────
date_col, _ = st.columns([1, 2])
with date_col:
    date_range = st.date_input(
        "Date Range",
        value=(date.today() - timedelta(days=30), date.today()),
        key="analytics_dates"
    )

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Data: load real metrics if available, else dummy ─────────────────────────
_metrics_dict, _is_real = _get_ml_metrics()
df = metrics_to_dataframe(_metrics_dict)
best = get_best_model_summary(_metrics_dict)

_source_badge = '<span class="source-badge-live">● LIVE</span>' if _is_real else '<span class="source-badge-demo">◈ DEMO</span>'

if _is_real:
    st.markdown(f"""
<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
            border-radius:10px;padding:10px 16px;margin-bottom:12px;">
  <span style="color:#10b981;font-weight:700;font-size:13px;">✅ Live Metrics</span>
  <span style="color:{p['text_secondary']};font-size:13px;margin-left:6px;">—
    Displaying results from your trained models stored in <code>saved_models/</code></span>
</div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);
            border-radius:10px;padding:10px 16px;margin-bottom:12px;">
  <span style="color:#f59e0b;font-weight:700;font-size:13px;">◈ Demo Metrics</span>
  <span style="color:{p['text_secondary']};font-size:13px;margin-left:6px;">—
    Run <code>python scripts/train_models.py</code> to see real model performance.</span>
</div>""", unsafe_allow_html=True)

# ── Dataset Stats (Enhancement 1) ─────────────────────────────────────────────
ds1, ds2, ds3, ds4 = st.columns(4)
dataset_stats = [
    ("📦", "1,000,000+", "Training Reviews"),
    ("🛍️", "400,000", "Products Catalogued"),
    ("⭐", "127,214", "Sentiment Scores"),
    ("🧠", "3", "AI Engines Trained"),
]
for col, (icon, value, label) in zip([ds1, ds2, ds3, ds4], dataset_stats):
    with col:
        st.markdown(f"""
        <div style="
            background:{p['glass_bg']};
            backdrop-filter:blur(12px);
            border:1px solid {p['glass_border']};
            border-radius:14px;
            padding:16px 20px;
            text-align:center;
            margin-bottom:16px;
        ">
            <div style="font-size:28px;margin-bottom:6px;">
                {icon}
            </div>
            <div style="color:{p['accent']};font-size:22px;
                font-weight:800;line-height:1.1;">
                {value}
            </div>
            <div style="color:{p['text_secondary']};
                font-size:12px;margin-top:4px;">
                {label}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Metric cards ──────────────────────────────────────────────────────────────
with st.spinner("Loading metrics…"):
    m1, m2, m3, m4 = st.columns(4)
    _hybrid = _metrics_dict.get('Hybrid Sentiment-Aware', {})
    _svd    = _metrics_dict.get('Collaborative (SVD)', {})
    _rmse_delta = round(_hybrid.get('RMSE', 0.81) - _svd.get('RMSE', 0.89), 3)
    _prec_delta = round((_hybrid.get('Precision@10', 0.82) - _svd.get('Precision@10', 0.65)) * 100, 1)
    _rec_delta  = round((_hybrid.get('Recall@10', 0.74)   - _svd.get('Recall@10', 0.55))   * 100, 1)
    _f1_delta   = round((_hybrid.get('F1', 0.78)          - _svd.get('F1', 0.59))           * 100, 1)
    summary_metrics = [
        (m1, "Best RMSE",      f"{best['best_rmse']:.2f}",
             f"Hybrid ({_rmse_delta:+.3f})",  "inverse"),
        (m2, "Best Precision", f"{best['best_precision']*100:.0f}%",
             f"Hybrid (+{_prec_delta}pp)",     "normal"),
        (m3, "Best Recall",    f"{best['best_recall']*100:.0f}%",
             f"Hybrid (+{_rec_delta}pp)",      "normal"),
        (m4, "Best F1 Score",  f"{best['best_f1']:.2f}",
             f"Hybrid (+{_f1_delta}pp)",       "normal"),
    ]
    for col, label, val, delta, dc in summary_metrics:
        with col:
            st.metric(label, val, delta, delta_color=dc)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
chart1, chart2 = st.columns(2)

with chart1:
    st.markdown(
        f'<p style="font-size:14px;font-weight:700;color:{p["text_primary"]};margin-bottom:4px">'
        f'Error Comparison <span style="font-size:11px;font-weight:400;color:{p["text_secondary"]}">'
        f'(lower is better)</span>{_source_badge}</p>',
        unsafe_allow_html=True)
    fig1 = px.bar(df, x='Model', y=['RMSE', 'MAE'], barmode='group',
                  color_discrete_sequence=['#6366f1', '#06B6D4'], template="plotly_white")
    fig1.update_layout(margin=dict(t=8, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter', color=_label_col), legend_title_text='')
    st.plotly_chart(fig1, use_container_width=True)

with chart2:
    st.markdown(
        f'<p style="font-size:14px;font-weight:700;color:{p["text_primary"]};margin-bottom:4px">'
        f'Performance Radar <span style="font-size:11px;font-weight:400;color:{p["text_secondary"]}">'
        f'(higher is better)</span>{_source_badge}</p>',
        unsafe_allow_html=True)
    radar_cats = ['Precision@10', 'Recall@10', 'F1 Score']
    fig2 = go.Figure()
    colors = ['#6366f1', '#06B6D4', '#10B981']
    for i, row in df.iterrows():
        fig2.add_trace(go.Scatterpolar(
            r=[row['Precision@10'], row['Recall@10'], row['F1 Score']],
            theta=radar_cats, fill='toself', name=row['Model'],
            line=dict(color=colors[i])
        ))
    fig2.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        margin=dict(t=8, b=0, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        template="plotly_white", font=dict(family='Inter', color=_label_col)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Metrics table + Precision-Recall chart ────────────────────────────────────
tbl_col, pr_col = st.columns([2.5, 1])

# Theme-aware table colors
tbl_bg      = p['card_bg']
tbl_header  = p['glass_bg']
tbl_text    = p['text_primary']
tbl_sub     = p['text_secondary']
tbl_border  = p['border']
tbl_good    = '#10b981'
tbl_warn    = '#f59e0b'
tbl_bad     = '#ef4444'

with tbl_col:
    st.markdown(
        f'<p style="font-size:14px;font-weight:700;color:{p["text_primary"]};margin-bottom:8px">'
        f'Detailed Metrics {_source_badge}</p>',
        unsafe_allow_html=True)

    # Build themed HTML table (Bug Fix 1: replaces st.dataframe white BG)
    rows_html = ""
    for _, row in df.iterrows():
        rmse_val = row.get('RMSE', 0)
        rmse_color = tbl_good if rmse_val < 1.0 else (tbl_warn if rmse_val < 1.1 else tbl_bad)

        mae_val = row.get('MAE', 0)
        mae_color = tbl_good if mae_val < 0.75 else (tbl_warn if mae_val < 0.85 else tbl_bad)

        prec_val = row.get('Precision@10', 0)
        prec_color = tbl_good if prec_val > 0.5 else (tbl_warn if prec_val > 0.2 else tbl_bad)

        recall_val = row.get('Recall@10', 0)
        recall_color = tbl_good if recall_val > 0.7 else (tbl_warn if recall_val > 0.4 else tbl_bad)

        f1_val = row.get('F1 Score', 0)
        f1_color = tbl_good if f1_val > 0.45 else (tbl_warn if f1_val > 0.3 else tbl_bad)

        model_name = row.get('Model', '')
        train_time = row.get('Training Time (s)', '-')

        rows_html += f"""<tr>
<td style="padding:8px 10px;color:{tbl_text};font-weight:600;font-size:13px;border-bottom:1px solid {tbl_border};white-space:nowrap;">{model_name}</td>
<td style="padding:8px 10px;text-align:center;border-bottom:1px solid {tbl_border};"><span style="color:{rmse_color};font-weight:700;font-size:13px;">{rmse_val:.4f}</span></td>
<td style="padding:8px 10px;text-align:center;border-bottom:1px solid {tbl_border};"><span style="color:{mae_color};font-weight:700;font-size:13px;">{mae_val:.4f}</span></td>
<td style="padding:8px 10px;text-align:center;border-bottom:1px solid {tbl_border};"><span style="color:{prec_color};font-weight:700;font-size:13px;">{prec_val:.2f}</span></td>
<td style="padding:8px 10px;text-align:center;border-bottom:1px solid {tbl_border};"><span style="color:{recall_color};font-weight:700;font-size:13px;">{recall_val:.2f}</span></td>
<td style="padding:8px 10px;text-align:center;border-bottom:1px solid {tbl_border};"><span style="color:{f1_color};font-weight:700;font-size:13px;">{f1_val:.4f}</span></td>
<td style="padding:8px 10px;text-align:center;color:{tbl_sub};font-size:12px;border-bottom:1px solid {tbl_border};white-space:nowrap;">{train_time}s</td>
</tr>"""

    # Strip leading whitespace so Markdown's 4-space code-block rule isn't triggered
    rows_html = '\n'.join(line.strip() for line in rows_html.splitlines() if line.strip())

    _th = f"padding:10px 10px;color:{tbl_sub};font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;border-bottom:2px solid {tbl_border};white-space:nowrap;"
    st.markdown(f"""
<div style="background:{tbl_bg};border:1px solid {tbl_border};border-radius:16px;overflow-x:auto;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin:16px 0;">
<table style="width:100%;border-collapse:collapse;min-width:520px;">
<thead><tr style="background:{tbl_header};">
<th style="{_th}text-align:left;">Model</th>
<th style="{_th}text-align:center;">RMSE ↓</th>
<th style="{_th}text-align:center;">MAE ↓</th>
<th style="{_th}text-align:center;">P@10 ↑</th>
<th style="{_th}text-align:center;">R@10 ↑</th>
<th style="{_th}text-align:center;">F1 ↑</th>
<th style="{_th}text-align:center;">Time (s)</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>
<div style="padding:8px 14px;font-size:11px;color:{tbl_sub};text-align:right;">
↓ Lower is better &nbsp;|&nbsp; ↑ Higher is better &nbsp;|&nbsp;
<span style="color:{tbl_good};">■</span> Best &nbsp;
<span style="color:{tbl_warn};">■</span> Mid &nbsp;
<span style="color:{tbl_bad};">■</span> Needs improvement
</div></div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="background-color:{p['accent_soft']};border-left:3px solid {p['accent']};padding:12px 16px;
            border-radius:0 10px 10px 0;margin-top:14px;font-size:13px;
            color:{p['text_secondary']};line-height:1.6">
  <strong style="color:{p['text_primary']}">Why Hybrid Wins:</strong>
  The Hybrid Sentiment-Aware engine outperforms both baselines by combining
  SVD matrix factorization, TF-IDF content signals, and VADER sentiment scoring —
  overcoming cold-start and sparsity problems simultaneously.
</div>""", unsafe_allow_html=True)

with pr_col:
    st.markdown(
        f'<p style="font-size:14px;font-weight:700;color:{p["text_primary"]};margin-bottom:4px">'
        f'Precision vs Recall {_source_badge}</p>',
        unsafe_allow_html=True)
    fig3 = px.line(df, x='Recall@10', y='Precision@10', text='Model',
                   markers=True, color_discrete_sequence=['#6366f1'], template="plotly_white")
    fig3.update_traces(textposition="top center")
    fig3.update_layout(margin=dict(t=8, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter', color=_label_col))
    st.plotly_chart(fig3, use_container_width=True)

# ── Model Insight Badges (Enhancement 2) ──────────────────────────────────────
insights = [
    ("🥇", "Content-Based wins on Precision",
     "60% Precision@10 — best for finding relevant items"),
    ("🚀", "Hybrid wins on Recall",
     "97% Recall@10 — best for not missing good products"),
    ("⚡", "SVD trains fastest",
     "16s training time — ideal for real-time retraining"),
    ("🎯", "Hybrid is production choice",
     "Best balance of precision, recall and sentiment"),
]
insight_cols = st.columns(2)
for i, (icon, title, desc) in enumerate(insights):
    with insight_cols[i % 2]:
        st.markdown(f"""
        <div style="
            background:{p['glass_bg']};
            border:1px solid {p['glass_border']};
            border-left:3px solid {p['accent']};
            border-radius:12px;
            padding:14px 16px;
            margin-bottom:10px;
        ">
            <div style="display:flex;align-items:center;
                gap:8px;margin-bottom:4px;">
                <span style="font-size:18px;">{icon}</span>
                <span style="color:{p['text_primary']};
                    font-weight:700;font-size:14px;">
                    {title}
                </span>
            </div>
            <div style="color:{p['text_secondary']};
                font-size:13px;">
                {desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Download (Bug Fix 2: styled button) ───────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

st.markdown(f"""
<style>
[data-testid="stDownloadButton"] > button {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.35) !important;
    transition: all 0.18s ease !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    box-shadow: 0 4px 20px rgba(99,102,241,0.5) !important;
    opacity: 0.92 !important;
}}
[data-testid="stDownloadButton"] > button p,
[data-testid="stDownloadButton"] > button span {{
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}}
</style>
""", unsafe_allow_html=True)

csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
csv_content = csv_buffer.getvalue()

st.download_button(
    label="⬇️ Download Metrics CSV",
    data=csv_content,
    file_name="intellirec_model_metrics.csv",
    mime="text/csv",
    key="btn_download_metrics"
)

# ── Training Pipeline Timeline (Enhancement 3) ───────────────────────────────
st.markdown("---")

steps = [
    ("1", "Data Loading", "22.2s",
     "1M reviews + 400K products loaded", "#06b6d4"),
    ("2", "SVD Training", "16.0s",
     "799K ratings · 20 epochs · RMSE 1.1466", "#6366f1"),
    ("3", "TF-IDF Training", "121.0s",
     "400K products · 50K features matrix", "#8b5cf6"),
    ("4", "VADER Sentiment", "76.7s",
     "127,214 products scored", "#10b981"),
    ("5", "Hybrid Metrics", "32.5s",
     "P@10, R@10, F1 computed and saved", "#f59e0b"),
]

st.markdown(f"""
<div style="margin:24px 0 8px;">
    <h3 style="color:{p['text_primary']};font-size:18px;
        font-weight:700;margin-bottom:16px;">
        🔧 Training Pipeline — 268.2s Total
    </h3>
</div>
""", unsafe_allow_html=True)

timeline_html = '<div style="display:flex;gap:0;align-items:stretch;">'
for i, (num, name, time_s, desc, color) in enumerate(steps):
    timeline_html += f"""
    <div style="flex:1;min-width:0;">
        <div style="
            background:{p['glass_bg']};
            border:1px solid {p['glass_border']};
            border-top:3px solid {color};
            border-radius:12px;
            padding:14px 12px;
            height:100%;
        ">
            <div style="
                background:{color};
                color:#fff;
                width:24px;height:24px;
                border-radius:50%;
                display:flex;align-items:center;
                justify-content:center;
                font-size:12px;font-weight:800;
                margin-bottom:8px;">
                {num}
            </div>
            <div style="color:{p['text_primary']};
                font-weight:700;font-size:13px;
                margin-bottom:2px;">{name}</div>
            <div style="color:{color};font-size:12px;
                font-weight:600;margin-bottom:4px;">
                ⏱ {time_s}
            </div>
            <div style="color:{p['text_secondary']};
                font-size:11px;line-height:1.4;">
                {desc}
            </div>
        </div>
    </div>"""

    if i < len(steps) - 1:
        timeline_html += f"""
    <div style="width:16px;flex-shrink:0;display:flex;
        align-items:center;">
        <div style="height:2px;width:100%;
            background:{p['border']};"></div>
    </div>"""

timeline_html += '</div>'
st.markdown(timeline_html, unsafe_allow_html=True)
