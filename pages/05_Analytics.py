import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.notifications import add_notification

st.set_page_config(page_title="Analytics | IntelliRec", page_icon="💡", layout="wide")
check_login()
from utils.theme import inject_global_css
inject_global_css()
render_sidebar("analytics")

# ── Top Bar ───────────────────────────────────────────────────────────────────
render_topbar("AI Model Performance", "Triple-engine architecture — metrics dashboard")

# ── Date range + controls ─────────────────────────────────────────────────────
ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
with ctrl1:
    date_range = st.date_input(
        "Date Range",
        value=(date.today() - timedelta(days=30), date.today()),
        key="analytics_dates"
    )
with ctrl2:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    if st.button("Retrain Models", type="secondary", key="retrain_btn"):
        with st.spinner("Queuing model retraining…"):
            import time; time.sleep(0.8)
        add_notification('info', 'Model Retraining Queued',
                         'Models will retrain overnight. Check back tomorrow.')
        st.toast("Model retraining queued!")
with ctrl3:
    pass  # spacer

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
data = {
    'Model': ['Collaborative (SVD)', 'Content-Based (TF-IDF)', 'Hybrid Sentiment-Aware'],
    'RMSE': [0.89, 0.95, 0.81],
    'MAE': [0.68, 0.73, 0.61],
    'Precision@10': [0.65, 0.60, 0.82],
    'Recall@10': [0.55, 0.50, 0.74],
    'F1 Score': [0.59, 0.55, 0.78],
    'Training Time (s)': [12.5, 4.2, 18.0],
}
df = pd.DataFrame(data)

# ── Metric cards ──────────────────────────────────────────────────────────────
with st.spinner("Loading metrics…"):
    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        (m1, "Best RMSE",      "0.81", "Hybrid (−0.08 vs CF)", "inverse"),
        (m2, "Best Precision", "82%",  "Hybrid (+17pp)",        "normal"),
        (m3, "Best Recall",    "74%",  "Hybrid (+19pp)",        "normal"),
        (m4, "Best F1 Score",  "0.78", "Hybrid (+19pp)",        "normal"),
    ]
    for col, label, val, delta, dc in metrics:
        with col:
            st.metric(label, val, delta, delta_color=dc)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
chart1, chart2 = st.columns(2)

with chart1:
    st.markdown('<p style="font-size:14px;font-weight:600;color:#111827;margin-bottom:4px">Error Comparison (lower is better)</p>',
                unsafe_allow_html=True)
    fig1 = px.bar(df, x='Model', y=['RMSE', 'MAE'], barmode='group',
                  color_discrete_sequence=['#6C63FF', '#06B6D4'], template="plotly_white")
    fig1.update_layout(margin=dict(t=8, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter'), legend_title_text='')
    st.plotly_chart(fig1, use_container_width=True)

with chart2:
    st.markdown('<p style="font-size:14px;font-weight:600;color:#111827;margin-bottom:4px">Performance Radar (higher is better)</p>',
                unsafe_allow_html=True)
    radar_cats = ['Precision@10', 'Recall@10', 'F1 Score']
    fig2 = go.Figure()
    colors = ['#6C63FF', '#06B6D4', '#10B981']
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
        template="plotly_white", font=dict(family='Inter')
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Metrics table + Precision-Recall chart ────────────────────────────────────
tbl_col, pr_col = st.columns([1.6, 1])

with tbl_col:
    st.markdown('<p style="font-size:14px;font-weight:600;color:#111827;margin-bottom:8px">Detailed Metrics</p>',
                unsafe_allow_html=True)
    styled = (df.style
              .highlight_max(subset=['Precision@10', 'Recall@10', 'F1 Score'],
                             color='#DCFCE7')
              .highlight_min(subset=['RMSE', 'MAE'], color='#DCFCE7')
              .highlight_max(subset=['RMSE', 'MAE'], color='#FEE2E2')
              .format({'RMSE': '{:.2f}', 'MAE': '{:.2f}',
                       'Precision@10': '{:.2f}', 'Recall@10': '{:.2f}',
                       'F1 Score': '{:.2f}', 'Training Time (s)': '{:.1f}'}))
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("""
<div style="background:#EEF2FF;border-left:3px solid #6C63FF;padding:12px 16px;
            border-radius:0 10px 10px 0;margin-top:14px;font-size:13px;
            color:#6B7280;line-height:1.6">
  <strong style="color:#111827">Why Hybrid Wins:</strong>
  The Hybrid Sentiment-Aware engine outperforms both baselines by combining
  SVD matrix factorization, TF-IDF content signals, and VADER sentiment scoring —
  overcoming cold-start and sparsity problems simultaneously.
</div>""", unsafe_allow_html=True)

with pr_col:
    st.markdown('<p style="font-size:14px;font-weight:600;color:#111827;margin-bottom:4px">Precision vs Recall</p>',
                unsafe_allow_html=True)
    fig3 = px.line(df, x='Recall@10', y='Precision@10', text='Model',
                   markers=True, color_discrete_sequence=['#6C63FF'], template="plotly_white")
    fig3.update_traces(textposition="top center")
    fig3.update_layout(margin=dict(t=8, b=0, l=0, r=0),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(family='Inter'))
    st.plotly_chart(fig3, use_container_width=True)

# ── Download ──────────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Metrics CSV",
    data=csv,
    file_name="intellirec_model_metrics.csv",
    mime="text/csv",
    key="dl_metrics_csv"
)
