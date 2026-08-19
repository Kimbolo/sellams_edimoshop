# app.py - Version COMPLÈTE
import streamlit as st
import pandas as pd
import plotly.express as px
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

# Filtres
try:
    annees = load_data("SELECT DISTINCT YEAR(date_facture) as annee FROM facturec WHERE date_facture IS NOT NULL ORDER BY annee DESC")
    if not annees.empty:
        annee_selection = st.sidebar.selectbox(
            "📅 Année",
            options=annees['annee'].tolist(),
            index=0
        )
    else:
        annee_selection = 2024
        st.warning("⚠️ Aucune donnée de vente trouvée")
except Exception as e:
    annee_selection = 2024
    st.warning(f"⚠️ Erreur de chargement des années : {e}")

st.sidebar.markdown("---")
st.sidebar.info("📊 Prototype Dashboard - v1.0")

# Titre principal
st.title("🏪 Sellams Edimo Sports - Tableau de Bord")
st.markdown(f"### 📅 Analyse pour l'année **{annee_selection}**")
st.markdown("---")

# Chargement des données
try:
    stats = get_stats_globales()
    ventes_annuelles = get_ventes_annuelles()
    ventes_annee = ventes_annuelles[ventes_annuelles['annee'] == annee_selection] if not ventes_annuelles.empty else pd.DataFrame()
except Exception as e:
    stats = {}
    ventes_annee = pd.DataFrame()
    st.error(f"❌ Erreur de chargement des données : {e}")

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
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée pour cette année")

with col2:
    st.subheader("🏆 Top 10 Produits")
    try:
        top_produits = get_top_produits(annee_selection, 10)
        if not top_produits.empty:
            fig = create_bar_chart(
                top_produits,
                x='ca_produit', y='nom_produit',
                title='Top 10 des Produits',
                orientation='h'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun produit vendu cette année")
    except Exception as e:
        st.info(f"Données de produits non disponibles : {str(e)}")

# Graphiques ligne 2
col3, col4 = st.columns(2)

with col3:
    st.subheader("📊 Ventes par Catégorie")
    try:
        ventes_cat = get_ventes_par_categorie(annee_selection)
        if not ventes_cat.empty:
            fig = create_pie_chart(
                ventes_cat,
                values='ca_categorie',
                names='nom_categorie',
                title='Répartition du CA par Catégorie'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée de catégorie")
    except Exception as e:
        st.info(f"Données de catégories non disponibles : {str(e)}")

with col4:
    st.subheader("📦 Top Clients")
    try:
        query = f"""
        SELECT 
            c.nom_client,
            COUNT(DISTINCT f.id_facturec) as nb_achats,
            SUM(lf.quantite * lf.prix_unitaire) as total_achats
        FROM facturec f
        JOIN clients c ON f.client_id = c.id_client
        JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
        WHERE YEAR(f.date_facture) = {annee_selection}
        GROUP BY c.id_client, c.nom_client
        ORDER BY total_achats DESC
        LIMIT 10
        """
        top_clients = load_data(query)
        if not top_clients.empty:
            fig = create_bar_chart(
                top_clients,
                x='total_achats', y='nom_client',
                title='Top 10 Clients',
                orientation='h'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun client cette année")
    except Exception as e:
        st.info(f"Données clients non disponibles : {str(e)}")

st.markdown("---")

# Alertes et informations
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