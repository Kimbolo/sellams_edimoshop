import streamlit as st
import pandas as pd
from utils.database import *
from utils.charts import *

st.set_page_config(page_title="Accueil", page_icon="🏠", layout="wide")

st.title("🏪 Sellams Edimo Sports - Tableau de Bord")
st.markdown("---")

# Sidebar - Filtres
st.sidebar.image("https://via.placeholder.com/150x50?text=Sellams", use_column_width=True)
st.sidebar.title("🏪 Sellams Edimo Sports")
st.sidebar.markdown("---")

# Filtres
years = get_years()
annee_selection = st.sidebar.selectbox(
    "📅 Année",
    options=years,
    index=0 if years else 0
)

st.sidebar.markdown("---")
st.sidebar.info("📊 Prototype Dashboard - v1.0")

# Chargement des données
stats = get_stats_globales()
ventes_annuelles = get_ventes_annuelles()
ventes_annee = ventes_annuelles[ventes_annuelles['annee'] == annee_selection] if not ventes_annuelles.empty else pd.DataFrame()

# KPI
col1, col2, col3, col4 = st.columns(4)

with col1:
    ca_annee = ventes_annee['ca'].sum() if not ventes_annee.empty else 0
    display_kpi("💰 Chiffre d'Affaires", ca_annee)

with col2:
    clients = stats.get('total_clients', 0)
    display_kpi("👥 Clients", clients)

with col3:
    factures = stats.get('nb_factures', 0)
    display_kpi("📄 Factures", factures)

with col4:
    panier_moyen = ca_annee / factures if factures > 0 else 0
    display_kpi("🛒 Panier Moyen", panier_moyen)

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
        st.info("Aucune donnée pour cette année")

with col2:
    st.subheader("🏆 Top 10 Produits")
    top_produits = get_top_produits(annee_selection, 10)
    if not top_produits.empty:
        fig = create_bar_chart(
            top_produits,
            x='ca_produit', y='nom_produit',
            title='Top 10 des Produits',
            orientation='h',
            height=400
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
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
        st.info("Aucune donnée de catégorie")

with col4:
    st.subheader("📦 Top Clients")
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
            orientation='h',
            height=350
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun client cette année")

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
