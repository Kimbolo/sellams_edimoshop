import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_line_chart(df, x, y, title, color=None, labels=None, height=400):
    """Créer un graphique en ligne"""
    if df is None or df.empty:
        return None
    try:
        fig = px.line(
            df, x=x, y=y, color=color,
            title=title, labels=labels,
            markers=True, height=height
        )
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig
    except Exception as e:
        return None

def create_bar_chart(df, x, y, title, color=None, orientation='v', height=400):
    """Créer un graphique en barres"""
    if df is None or df.empty:
        return None
    try:
        fig = px.bar(
            df, x=x, y=y, color=color,
            title=title, orientation=orientation,
            height=height
        )
        fig.update_layout(
            template='plotly_white',
            margin=dict(l=20, r=20, t=50, b=20)
        )
        if orientation == 'h':
            fig.update_yaxes(categoryorder='total ascending')
        return fig
    except Exception as e:
        return None

def create_pie_chart(df, values, names, title, hole=0.3, height=400):
    """Créer un graphique en camembert"""
    if df is None or df.empty:
        return None
    try:
        fig = px.pie(
            df, values=values, names=names,
            title=title, hole=hole, height=height
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12
        )
        fig.update_layout(
            template='plotly_white',
            margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig
    except Exception as e:
        return None
