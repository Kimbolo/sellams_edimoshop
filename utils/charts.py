# utils/charts.py - Version simplifiée
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_line_chart(df, x, y, title, color=None, labels=None):
    """Créer un graphique en ligne"""
    fig = px.line(
        df, x=x, y=y, color=color,
        title=title, labels=labels,
        markers=True
    )
    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        height=400
    )
    return fig

def create_bar_chart(df, x, y, title, color=None, orientation='v'):
    """Créer un graphique en barres"""
    fig = px.bar(
        df, x=x, y=y, color=color,
        title=title, orientation=orientation
    )
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    return fig

def create_pie_chart(df, values, names, title, hole=0.3):
    """Créer un graphique en camembert"""
    fig = px.pie(
        df, values=values, names=names,
        title=title, hole=hole
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    return fig

def create_heatmap(df, x, y, z, title):
    """Créer une heatmap"""
    if df.empty:
        return None
    pivot = df.pivot(index=y, columns=x, values=z)
    fig = px.imshow(
        pivot,
        title=title,
        color_continuous_scale='Viridis',
        aspect='auto'
    )
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    return fig

def display_kpi(label, value, delta=None, format='{:,.0f}'):
    """Afficher un KPI formaté"""
    col = st.columns(1)[0]
    col.metric(
        label=label,
        value=format.format(value) if value else '0',
        delta=delta
    )