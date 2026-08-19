import mysql.connector
import pandas as pd
import streamlit as st
from mysql.connector import Error

# Configuration de la base de données - À MODIFIER SELON VOS IDENTIFIANTS
DB_CONFIG = {
    'host': 'localhost',      # ou 127.0.0.1
    'user': 'root',           # votre utilisateur MySQL
    'password': '',           # votre mot de passe (vide par défaut sur XAMPP)
    'database': 'sellams_edimoshop',
    'charset': 'utf8mb4',
    'port': 3306              # port par défaut de MySQL
}

@st.cache_resource
def get_connection():
    """Obtenir une connexion à la base de données MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"""
        ❌ **Erreur de connexion à MySQL**
        
        Détails : {e}
        
        **Vérifiez que :**
        1. XAMPP est démarré avec MySQL
        2. Les identifiants sont corrects
        3. La base 'sellams_edimoshop' existe
        """)
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def load_data(query):
    """Charger des données depuis MySQL avec mise en cache"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Error as e:
        st.error(f"❌ Erreur SQL : {e}")
        st.code(query, language='sql')
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erreur inattendue : {e}")
        return pd.DataFrame()

def test_connection():
    """Tester la connexion à MySQL"""
    try:
        conn = get_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True
    except:
        return False

def get_tables_info():
    """Obtenir la liste des tables et leurs enregistrements"""
    query = """
    SELECT 
        table_name as 'Table',
        table_rows as 'Enregistrements',
        ROUND(data_length / 1024 / 1024, 2) as 'Taille (MB)'
    FROM information_schema.tables
    WHERE table_schema = 'sellams_edimoshop'
    ORDER BY table_rows DESC
    """
    return load_data(query)

def get_years():
    """Récupérer les années disponibles dans les factures"""
    query = """
    SELECT DISTINCT 
        YEAR(date_facture) as annee 
    FROM facturec 
    WHERE date_facture IS NOT NULL 
    ORDER BY annee DESC
    """
    df = load_data(query)
    return df['annee'].tolist() if not df.empty else [2024]

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

def get_ventes_annuelles():
    """Récupérer les ventes par année et mois"""
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
        AVG(lf.prix_unitaire) as prix_moyen,
        COUNT(DISTINCT f.id_facturec) as nb_ventes
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

def get_ventes_par_categorie(annee=None):
    """Ventes par catégorie"""
    where = f"WHERE YEAR(f.date_facture) = {annee}" if annee else ""
    query = f"""
    SELECT 
        COALESCE(cp.nom_categorie, 'Sans catégorie') as nom_categorie,
        SUM(lf.quantite * lf.prix_unitaire) as ca_categorie,
        SUM(lf.quantite) as quantite_vendue,
        COUNT(DISTINCT f.id_facturec) as nb_ventes
    FROM facturec f
    JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
    JOIN produit p ON lf.produit_id = p.id_produit
    LEFT JOIN categorie_produit cp ON p.categorie_id = cp.id_categorie
    {where}
    GROUP BY cp.nom_categorie
    ORDER BY ca_categorie DESC
    """
    return load_data(query)

def get_stocks_actuels():
    """Récupérer les stocks actuels"""
    query = """
    SELECT 
        p.nom_produit,
        p.code_produit,
        COALESCE(cp.nom_categorie, 'Sans catégorie') as nom_categorie,
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

def get_top_clients(annee=None, limite=10):
    """Récupérer les top clients"""
    where = f"WHERE YEAR(f.date_facture) = {annee}" if annee else ""
    query = f"""
    SELECT 
        c.nom_client,
        COUNT(DISTINCT f.id_facturec) as nb_achats,
        SUM(lf.quantite * lf.prix_unitaire) as total_achats,
        AVG(lf.quantite * lf.prix_unitaire) as panier_moyen
    FROM facturec f
    JOIN clients c ON f.client_id = c.id_client
    JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
    {where}
    GROUP BY c.id_client, c.nom_client
    ORDER BY total_achats DESC
    LIMIT {limite}
    """
    return load_data(query)

def get_ventes_detaillees(annee=None, mois_debut=None, mois_fin=None, categorie=None):
    """Récupérer les ventes détaillées avec filtres"""
    conditions = []
    if annee:
        conditions.append(f"YEAR(f.date_facture) = {annee}")
    if mois_debut and mois_fin:
        conditions.append(f"MONTH(f.date_facture) BETWEEN {mois_debut} AND {mois_fin}")
    if categorie and categorie != 'Toutes':
        conditions.append(f"cp.nom_categorie = '{categorie}'")
    
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    query = f"""
    SELECT 
        f.id_facturec,
        f.date_facture,
        c.nom_client,
        p.nom_produit,
        p.code_produit,
        cp.nom_categorie,
        lf.quantite,
        lf.prix_unitaire,
        (lf.quantite * lf.prix_unitaire) as montant
    FROM facturec f
    JOIN clients c ON f.client_id = c.id_client
    JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
    JOIN produit p ON lf.produit_id = p.id_produit
    LEFT JOIN categorie_produit cp ON p.categorie_id = cp.id_categorie
    {where}
    ORDER BY f.date_facture DESC
    LIMIT 10000
    """
    return load_data(query)
