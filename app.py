import streamlit as st
import pandas as pd
from utils.database import *
from utils.charts import *

st.set_page_config(
    page_title="Sellams Edimo Sports",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🏪 Sellams Edimo Sports")
st.sidebar.markdown("---")

# Test de connexion
if not test_connection():
    st.sidebar.error("⚠️ Mode démo - données simulées")
    st.warning("""
    ### ℹ️ Mode Démo Activé
    
    Les données affichées sont des données de démonstration.
    En local, connectez-vous à MySQL pour les données réelles.
    """)
else:
    st.sidebar.success("✅ Base de données connectée")

# Filtres
try:
    years = get_years()
    annee_selection = st.sidebar.selectbox(
        "📅 Année",
        options=years if years else [2024, 2023, 2022],
        index=0 if years else 0
    )
except:
    annee_selection = 2024

st.sidebar.markdown("---")
st.sidebar.info("📊 Dashboard v1.0")
st.sidebar.markdown("---")

# Titre
st.title("🏪 Sellams Edimo Sports - Tableau de Bord")
st.markdown(f"### 📅 Analyse pour l'année **{annee_selection}**")
st.markdown("---")

# Chargement des données
stats = get_stats_globales()
ventes_annuelles = get_ventes_annuelles()
ventes_annee = ventes_annuelles[ventes_annuelles['annee'] == annee_selection] if not ventes_annuelles.empty else pd.DataFrame()

# KPI
col1, col2, col3, col4 = st.columns(4)

with col1:
    ca_annee = ventes_annee['ca'].sum() if not ventes_annee.empty else 0
    st.metric("💰 CA", f"{ca_annee:,.0f} FCFA")

with col2:
    clients = stats.get('total_clients', 0)
    st.metric("👥 Clients", f"{clients:,}")

with col3:
    factures = stats.get('nb_factures', 0)
    st.metric("📄 Factures", f"{factures:,}")

with col4:
    panier_moyen = ca_annee / factures if factures > 0 else 0
    st.metric("🛒 Panier Moyen", f"{panier_moyen:,.0f} FCFA")

st.markdown("---")

# Graphiques
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Évolution Mensuelle")
    if not ventes_annee.empty:
        fig = create_line_chart(
            ventes_annee, x='mois', y='ca',
            title=f'CA Mensuel - {annee_selection}',
            labels={'mois': 'Mois', 'ca': 'CA (FCFA)'}
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏆 Top Produits")
    top = get_top_produits(annee_selection, 10)
    if not top.empty:
        fig = create_bar_chart(
            top, x='ca_produit', y='nom_produit',
            title='Top 10 Produits', orientation='h'
        )
        if fig:
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption(f"🔄 {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
