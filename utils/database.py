import mysql.connector
import pandas as pd
import streamlit as st

@st.cache_resource
def get_connection():
    """Obtenir la connexion à la base de données"""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sellams_edimoshop'
        port=3307
    )

@st.cache_data(ttl=3600)
def load_data(query):
    """Charger des données avec mise en cache"""
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_ventes_annuelles():
    """Récupérer les ventes par année"""
    query = """
    SELECT 
        YEAR(f.date_facture) as annee,
        MONTH(f.date_facture) as mois,
        SUM(lf.quantite * lf.prix_unitaire) as ca,
        COUNT(DISTINCT f.client_id) as nb_clients,
        COUNT(DISTINCT f.id_facturec) as nb_factures,
        SUM(lf.quantite) as quantite_vendue
    FROM facturec f
    JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
    WHERE f.date_facture IS NOT NULL
    GROUP BY YEAR(f.date_facture), MONTH(f.date_facture)
    ORDER BY annee DESC, mois DESC
    """
    return load_data(query)

def get_top_produits(annee=None, limite=10):
    """Récupérer les top produits"""
    where = f"WHERE YEAR(f.date_facture) = {annee}" if annee else ""
    query = f"""
    SELECT 
        p.nom_produit,
        p.code_produit,
        cp.nom_categorie,
        SUM(lf.quantite) as quantite_vendue,
        SUM(lf.quantite * lf.prix_unitaire) as ca_produit,
        AVG(lf.prix_unitaire) as prix_moyen
    FROM facturec f
    JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
    JOIN produit p ON lf.produit_id = p.id_produit
    LEFT JOIN categorie_produit cp ON p.categorie_id = cp.id_categorie
    {where}
    GROUP BY p.id_produit, p.nom_produit, p.code_produit, cp.nom_categorie
    ORDER BY ca_produit DESC
    LIMIT {limite}
    """
    return load_data(query)

def get_stats_globales():
    """Obtenir les statistiques globales"""
    query = """
    SELECT 
        (SELECT COUNT(DISTINCT client_id) FROM facturec) as total_clients,
        (SELECT COUNT(*) FROM produit) as total_produits,
        (SELECT COUNT(*) FROM fournisseur) as total_fournisseurs,
        (SELECT COUNT(*) FROM magasin) as total_magasins,
        COALESCE(SUM(lf.quantite * lf.prix_unitaire), 0) as ca_total,
        COALESCE(COUNT(DISTINCT f.id_facturec), 0) as nb_factures
    FROM facturec f
    LEFT JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
    """
    df = load_data(query)
    return df.iloc[0].to_dict() if not df.empty else {}

def get_stocks_actuels():
    """Récupérer les stocks actuels"""
    query = """
    SELECT 
        p.nom_produit,
        p.code_produit,
        cp.nom_categorie,
        s.quantite_physique,
        s.quantite_theorique,
        m.nom_magasin,
        (s.quantite_physique - s.quantite_theorique) as ecart
    FROM stock s
    JOIN produit p ON s.produit_id = p.id_produit
    LEFT JOIN categorie_produit cp ON p.categorie_id = cp.id_categorie
    JOIN magasin m ON s.magasin_id = m.id_magasin
    WHERE s.quantite_physique > 0
    ORDER BY s.quantite_physique DESC
    """
    return load_data(query)

def get_approvisionnements():
    """Récupérer les approvisionnements"""
    query = """
    SELECT 
        r.id_reception,
        r.date_reception,
        f.nom_fournisseur,
        p.nom_produit,
        lr.quantite,
        lr.prix_unitaire,
        (lr.quantite * lr.prix_unitaire) as montant_total,
        YEAR(r.date_reception) as annee,
        MONTH(r.date_reception) as mois
    FROM reception r
    JOIN fournisseur f ON r.fournisseur_id = f.id_fournisseur
    JOIN ligne_reception lr ON r.id_reception = lr.reception_id
    JOIN produit p ON lr.produit_id = p.id_produit
    WHERE r.date_reception IS NOT NULL
    ORDER BY r.date_reception DESC
    """
    return load_data(query)

def get_ventes_par_categorie(annee=None):
    """Ventes par catégorie"""
    where = f"WHERE YEAR(f.date_facture) = {annee}" if annee else ""
    query = f"""
    SELECT 
        cp.nom_categorie,
        SUM(lf.quantite * lf.prix_unitaire) as ca_categorie,
        SUM(lf.quantite) as quantite_vendue
    FROM facturec f
    JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
    JOIN produit p ON lf.produit_id = p.id_produit
    LEFT JOIN categorie_produit cp ON p.categorie_id = cp.id_categorie
    {where}
    GROUP BY cp.nom_categorie
    ORDER BY ca_categorie DESC
    """
    return load_data(query)