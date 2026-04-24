"""
utils/evaluator.py
IntelliRec — Model Evaluation & Visualization Utilities
Sourcesys Technologies Internship Project
Team: Hemanthselva AK, Monish Kaarthi RK, Vishal KS, Vishal M
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saved_models')


# ── Metrics loading ────────────────────────────────────────────────────────────
def load_metrics():
    """Load real metrics if available, otherwise return sensible dummy data."""
    path = os.path.join(MODELS_DIR, 'model_metrics.pkl')
    if os.path.exists(path):
        try:
            metrics = joblib.load(path)
            print("[Evaluator] Real metrics loaded from disk.")
            return metrics, True          # (metrics, is_real)
        except Exception as e:
            print(f"[Evaluator] Could not load metrics: {e}")
    return get_dummy_metrics(), False


def get_dummy_metrics():
    """Baseline/placeholder metrics matching expected model performance."""
    return {
        'Collaborative (SVD)': {
            'RMSE': 0.89, 'MAE': 0.68,
            'Precision@10': 0.65, 'Recall@10': 0.55,
            'F1': 0.59, 'Training Time': 12.5
        },
        'Content-Based (TF-IDF)': {
            'RMSE': 0.95, 'MAE': 0.73,
            'Precision@10': 0.60, 'Recall@10': 0.50,
            'F1': 0.55, 'Training Time': 4.2
        },
        'Hybrid Sentiment-Aware': {
            'RMSE': 0.81, 'MAE': 0.61,
            'Precision@10': 0.82, 'Recall@10': 0.74,
            'F1': 0.78, 'Training Time': 18.0
        }
    }


def metrics_to_dataframe(metrics: dict) -> pd.DataFrame:
    """Convert the metrics dict to a tidy DataFrame for display/charting."""
    rows = []
    for model, m in metrics.items():
        rows.append({
            'Model':             model,
            'RMSE':              m.get('RMSE', 0),
            'MAE':               m.get('MAE', 0),
            'Precision@10':      m.get('Precision@10', 0),
            'Recall@10':         m.get('Recall@10', 0),
            'F1 Score':          m.get('F1', 0),
            'Training Time (s)': m.get('Training Time', 0)
        })
    return pd.DataFrame(rows)


# ── Chart builders ─────────────────────────────────────────────────────────────
def create_rmse_chart(metrics: dict,
                      label_color: str = '#111827') -> go.Figure:
    """Grouped bar chart — RMSE vs MAE for all models."""
    models    = list(metrics.keys())
    rmse_vals = [metrics[m].get('RMSE', 0) for m in models]
    mae_vals  = [metrics[m].get('MAE', 0) for m in models]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='RMSE', x=models, y=rmse_vals,
        marker_color='#6C63FF',
        text=[f'{v:.3f}' for v in rmse_vals],
        textposition='outside'
    ))
    fig.add_trace(go.Bar(
        name='MAE', x=models, y=mae_vals,
        marker_color='#06B6D4',
        text=[f'{v:.3f}' for v in mae_vals],
        textposition='outside'
    ))
    fig.update_layout(
        barmode='group',
        title='Error Comparison (lower is better)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color=label_color),
        margin=dict(t=40, b=0, l=0, r=0)
    )
    return fig


def create_radar_chart(metrics: dict,
                       label_color: str = '#111827') -> go.Figure:
    """Radar / Spider chart — Precision@10, Recall@10, F1 per model."""
    categories = ['Precision@10', 'Recall@10', 'F1']
    colors     = ['#6C63FF', '#06B6D4', '#10B981']

    fig = go.Figure()
    for i, (model, m) in enumerate(metrics.items()):
        values = [m.get(c, 0) for c in categories]
        values.append(values[0])   # close the polygon
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=model,
            line_color=colors[i % len(colors)]
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title='Performance Radar (higher is better)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color=label_color),
        margin=dict(t=40, b=0, l=40, r=40)
    )
    return fig


def create_precision_recall_chart(metrics: dict,
                                  label_color: str = '#111827') -> go.Figure:
    """Line chart of Precision@10 vs Recall@10."""
    df = metrics_to_dataframe(metrics)
    fig = px.line(
        df, x='Recall@10', y='Precision@10',
        text='Model', markers=True,
        color_discrete_sequence=['#6366f1'],
        template='plotly_white'
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color=label_color),
        margin=dict(t=8, b=0, l=0, r=0)
    )
    return fig


def create_training_time_chart(metrics: dict,
                                label_color: str = '#111827') -> go.Figure:
    """Horizontal bar chart of training times."""
    models = list(metrics.keys())
    times  = [metrics[m].get('Training Time', 0) for m in models]
    colors = ['#6C63FF', '#06B6D4', '#10B981']

    fig = go.Figure(go.Bar(
        x=times, y=models,
        orientation='h',
        marker_color=colors,
        text=[f'{t:.1f}s' for t in times],
        textposition='outside'
    ))
    fig.update_layout(
        title='Training Time (seconds)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color=label_color),
        margin=dict(t=40, b=0, l=0, r=80)
    )
    return fig


def get_best_model_summary(metrics: dict) -> dict:
    """Return a dict summarising the best values across all models."""
    models = list(metrics.keys())
    return {
        'best_rmse_model':   min(models, key=lambda m: metrics[m].get('RMSE', 99)),
        'best_rmse':         min(metrics[m].get('RMSE', 99) for m in models),
        'best_prec_model':   max(models, key=lambda m: metrics[m].get('Precision@10', 0)),
        'best_precision':    max(metrics[m].get('Precision@10', 0) for m in models),
        'best_recall_model': max(models, key=lambda m: metrics[m].get('Recall@10', 0)),
        'best_recall':       max(metrics[m].get('Recall@10', 0) for m in models),
        'best_f1_model':     max(models, key=lambda m: metrics[m].get('F1', 0)),
        'best_f1':           max(metrics[m].get('F1', 0) for m in models)
    }
