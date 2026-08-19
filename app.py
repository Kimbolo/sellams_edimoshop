import streamlit as st
import pandas as pd
from utils.database import *
from utils.charts import *

# Configuration de la page
st.set_page_config(
    page_title="Sellams Edimo Sports",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("🏪 Sellams Edimo Sports")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard")
st.sidebar.markdown("---")

# Test de connexion
if not test_connection():
    st.sidebar.error("⚠️ Base de données non accessible")
    st.error("""
    ### ❌ Erreur de connexion à la base de données
    
    Vérifiez que :
    1. XAMPP/WAMP est en cours d'exécution
    2. MySQL est démarré
    3. La base de données 'sellams_edimoshop' existe
    4. Les identifiants sont corrects
    """)
    st.stop()

# Filtres
years = get_years()
annee_selection = st.sidebar.selectbox(
    "📅 Année",
    options=years,
    index=0 if years else 0
)

st.sidebar.markdown("---")
st.sidebar.info("📊 Prototype Dashboard - v1.0")
st.sidebar.markdown("---")
st.sidebar.caption("📈 Données en temps réel")

# Titre principal
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
    st.metric("💰 Chiffre d'Affaires", f"{ca_annee:,.0f} FCFA")

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

# Graphiques ligne 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Évolution Mensuelle des Ventes")
    if not ventes_annee.empty:
        fig = create_line_chart(
            ventes_annee,
            x='mois', y='ca',
            title=f'CA Mensuel - {annee_selection}',
            labels={'mois': 'Mois', 'ca': 'CA (FCFA)'}
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Graphique non disponible")
    else:
        st.info("Aucune donnée pour cette année")

with col2:
    st.subheader("🏆 Top 10 Produits")
    top_produits = get_top_produits(annee_selection, 10)
    if not top_produits.empty:
        fig = create_bar_chart(
            top_produits,
            x='ca_produit', y='nom_produit',
            title='Top 10 des Produits',
            orientation='h'
        )
        if fig:
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Graphique non disponible")
    else:
        st.info("Aucun produit vendu cette année")

# Graphiques ligne 2
col3, col4 = st.columns(2)

with col3:
    st.subheader("📊 Ventes par Catégorie")
    ventes_cat = get_ventes_par_categorie(annee_selection)
    if not ventes_cat.empty:
        fig = create_pie_chart(
            ventes_cat,
            values='ca_categorie',
            names='nom_categorie',
            title='Répartition du CA par Catégorie'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Graphique non disponible")
    else:
        st.info("Aucune donnée de catégorie")

with col4:
    st.subheader("📦 Top Clients")
    top_clients = get_top_clients(annee_selection, 10)
    if not top_clients.empty:
        fig = create_bar_chart(
            top_clients,
            x='total_achats', y='nom_client',
            title='Top 10 Clients',
            orientation='h'
        )
        if fig:
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Graphique non disponible")
    else:
        st.info("Aucun client cette année")

st.markdown("---")

# Informations système
with st.expander("ℹ️ Informations sur la base de données"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏪 Magasins", stats.get('total_magasins', 0))
    with col2:
        st.metric("📦 Produits", stats.get('total_produits', 0))
    with col3:
        st.metric("🏢 Fournisseurs", stats.get('total_fournisseurs', 0))

# Footer
st.markdown("---")
st.caption(f"🔄 Dernière mise à jour : {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
