import pandas as pd
import streamlit as st
import sqlite3
import os
from datetime import datetime

# Configuration - détection automatique de l'environnement
IS_CLOUD = os.environ.get('STREAMLIT_CLOUD', False)

def get_connection():
    """Obtenir une connexion à la base de données"""
    if IS_CLOUD:
        # Utiliser SQLite en Cloud
        try:
            # Créer une base SQLite avec les données de démonstration
            return get_sqlite_connection()
        except Exception as e:
            st.error(f"❌ Erreur SQLite : {e}")
            return None
    else:
        # Utiliser MySQL en local
        try:
            import mysql.connector
            return mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='sellams_edimoshop',
                charset='utf8mb4'
            )
        except ImportError:
            # Fallback SQLite si mysql-connector n'est pas installé
            return get_sqlite_connection()
        except Exception as e:
            st.error(f"❌ Erreur MySQL : {e}")
            return None

@st.cache_resource
def get_sqlite_connection():
    """Créer une connexion SQLite avec données de démonstration"""
    conn = sqlite3.connect('sellams_demo.db')
    create_demo_data(conn)
    return conn

def create_demo_data(conn):
    """Créer des données de démonstration pour le Cloud"""
    cursor = conn.cursor()
    
    # Créer les tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS facturec (
        id_facturec INTEGER PRIMARY KEY,
        client_id INTEGER,
        date_facture DATE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ligne_facturec (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facturec_id INTEGER,
        produit_id INTEGER,
        quantite INTEGER,
        prix_unitaire REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produit (
        id_produit INTEGER PRIMARY KEY,
        nom_produit TEXT,
        code_produit TEXT,
        categorie_id INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorie_produit (
        id_categorie INTEGER PRIMARY KEY,
        nom_categorie TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id_client INTEGER PRIMARY KEY,
        nom_client TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fournisseur (
        id_fournisseur INTEGER PRIMARY KEY,
        nom_fournisseur TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS magasin (
        id_magasin INTEGER PRIMARY KEY,
        nom_magasin TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock (
        id_stock INTEGER PRIMARY KEY AUTOINCREMENT,
        produit_id INTEGER,
        magasin_id INTEGER,
        quantite_physique INTEGER,
        quantite_theorique INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reception (
        id_reception INTEGER PRIMARY KEY,
        fournisseur_id INTEGER,
        date_reception DATE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ligne_reception (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reception_id INTEGER,
        produit_id INTEGER,
        quantite INTEGER,
        prix_unitaire REAL
    )
    ''')
    
    # Vérifier si des données existent déjà
    cursor.execute("SELECT COUNT(*) FROM facturec")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Données de démonstration
        categories = ['Football', 'Basketball', 'Athlétisme', 'Natation', 'Tennis']
        for i, cat in enumerate(categories, 1):
            cursor.execute("INSERT INTO categorie_produit VALUES (?, ?)", (i, cat))
        
        produits = [
            (1, 'Ballon de Football', 'BF001', 1),
            (2, 'Ballon de Basketball', 'BB001', 2),
            (3, 'Chaussures de Running', 'CR001', 3),
            (4, 'Lunettes de Natation', 'LN001', 4),
            (5, 'Raquette de Tennis', 'RT001', 5),
            (6, 'Maillot de Football', 'MF001', 1),
            (7, 'Chaussures de Basketball', 'CB001', 2),
            (8, 'Short de Sport', 'SS001', 3),
            (9, 'Bonnet de Bain', 'BB001', 4),
            (10, 'Balle de Tennis', 'BT001', 5)
        ]
        cursor.executemany("INSERT INTO produit VALUES (?, ?, ?, ?)", produits)
        
        clients = [
            (1, 'Jean Dupont'),
            (2, 'Marie Claire'),
            (3, 'Paul Ngono'),
            (4, 'Sarah Essomba'),
            (5, 'Michel Ekwalla')
        ]
        cursor.executemany("INSERT INTO clients VALUES (?, ?)", clients)
        
        fournisseurs = [
            (1, 'Sport Import SARL'),
            (2, 'Equipement Plus'),
            (3, 'Global Sports'),
            (4, 'Africa Sport SA'),
            (5, 'Euro Sport Distribution')
        ]
        cursor.executemany("INSERT INTO fournisseur VALUES (?, ?)", fournisseurs)
        
        magasins = [
            (1, 'Boutique Douala'),
            (2, 'Boutique Yaoundé'),
            (3, 'Boutique Garoua'),
            (4, 'Boutique Bafoussam')
        ]
        cursor.executemany("INSERT INTO magasin VALUES (?, ?)", magasins)
        
        stocks = []
        for i in range(1, 11):
            for j in range(1, 5):
                stocks.append((i, j, 50 + (i * 10) + (j * 5), 45 + (i * 8) + (j * 3)))
        cursor.executemany("INSERT INTO stock (produit_id, magasin_id, quantite_physique, quantite_theorique) VALUES (?, ?, ?, ?)", stocks)
        
        # Générer des factures
        import random
        from datetime import datetime, timedelta
        
        factures = []
        lignes = []
        for year in range(2022, 2025):
            for month in range(1, 13):
                for _ in range(random.randint(10, 20)):
                    facture_id = len(factures) + 1
                    client_id = random.randint(1, 5)
                    date_facture = datetime(year, month, random.randint(1, 28)).strftime('%Y-%m-%d')
                    factures.append((facture_id, client_id, date_facture))
                    
                    # Lignes de facture
                    for _ in range(random.randint(1, 4)):
                        produit_id = random.randint(1, 10)
                        quantite = random.randint(1, 5)
                        prix = random.randint(500, 50000)
                        lignes.append((facture_id, produit_id, quantite, prix))
        
        cursor.executemany("INSERT INTO facturec VALUES (?, ?, ?)", factures)
        cursor.executemany("INSERT INTO ligne_facturec (facturec_id, produit_id, quantite, prix_unitaire) VALUES (?, ?, ?, ?)", lignes)
        
        # Réceptions
        receptions = []
        lignes_reception = []
        for year in range(2022, 2025):
            for month in range(1, 13):
                for _ in range(random.randint(2, 5)):
                    reception_id = len(receptions) + 1
                    fournisseur_id = random.randint(1, 5)
                    date_reception = datetime(year, month, random.randint(1, 28)).strftime('%Y-%m-%d')
                    receptions.append((reception_id, fournisseur_id, date_reception))
                    
                    for _ in range(random.randint(1, 3)):
                        produit_id = random.randint(1, 10)
                        quantite = random.randint(10, 100)
                        prix = random.randint(300, 30000)
                        lignes_reception.append((reception_id, produit_id, quantite, prix))
        
        cursor.executemany("INSERT INTO reception VALUES (?, ?, ?)", receptions)
        cursor.executemany("INSERT INTO ligne_reception (reception_id, produit_id, quantite, prix_unitaire) VALUES (?, ?, ?, ?)", lignes_reception)
        
        conn.commit()
    
    return conn

@st.cache_data(ttl=3600, show_spinner=False)
def load_data(query):
    """Charger des données avec mise en cache"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        if isinstance(conn, sqlite3.Connection):
            # SQLite
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        else:
            # MySQL
            df = pd.read_sql(query, conn)
            conn.close()
            return df
    except Exception as e:
        st.warning(f"⚠️ Erreur de chargement : {e}")
        return pd.DataFrame()

def test_connection():
    """Tester la connexion"""
    try:
        conn = get_connection()
        if conn is None:
            return False
        if isinstance(conn, sqlite3.Connection):
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True
    except:
        return False

def get_years():
    query = "SELECT DISTINCT strftime('%Y', date_facture) as annee FROM facturec ORDER BY annee DESC"
    df = load_data(query)
    if df.empty:
        return [2024, 2023, 2022]
    return df['annee'].astype(int).tolist()

def get_stats_globales():
    query = """
    SELECT 
        (SELECT COUNT(DISTINCT client_id) FROM facturec) as total_clients,
        (SELECT COUNT(*) FROM produit) as total_produits,
        (SELECT COUNT(*) FROM fournisseur) as total_fournisseurs,
        (SELECT COUNT(*) FROM magasin) as total_magasins,
        COALESCE(SUM(quantite * prix_unitaire), 0) as ca_total,
        COALESCE(COUNT(DISTINCT facturec_id), 0) as nb_factures
    FROM ligne_facturec
    """
    df = load_data(query)
    if df.empty:
        return {'total_clients': 0, 'total_produits': 0, 'total_fournisseurs': 0, 
                'total_magasins': 0, 'ca_total': 0, 'nb_factures': 0}
    return df.iloc[0].to_dict()

def get_ventes_annuelles():
    query = """
    SELECT 
        CAST(strftime('%Y', f.date_facture) AS INTEGER) as annee,
        CAST(strftime('%m', f.date_facture) AS INTEGER) as mois,
        SUM(l.quantite * l.prix_unitaire) as ca,
        COUNT(DISTINCT f.client_id) as nb_clients,
        COUNT(DISTINCT f.id_facturec) as nb_factures,
        SUM(l.quantite) as quantite_vendue
    FROM facturec f
    JOIN ligne_facturec l ON f.id_facturec = l.facturec_id
    WHERE f.date_facture IS NOT NULL
    GROUP BY strftime('%Y', f.date_facture), strftime('%m', f.date_facture)
    ORDER BY annee DESC, mois DESC
    """
    return load_data(query)

def get_top_produits(annee=None, limite=10):
    where = f"AND strftime('%Y', f.date_facture) = '{annee}'" if annee else ""
    query = f"""
    SELECT 
        p.nom_produit,
        p.code_produit,
        c.nom_categorie,
        SUM(l.quantite) as quantite_vendue,
        SUM(l.quantite * l.prix_unitaire) as ca_produit,
        AVG(l.prix_unitaire) as prix_moyen
    FROM ligne_facturec l
    JOIN facturec f ON l.facturec_id = f.id_facturec
    JOIN produit p ON l.produit_id = p.id_produit
    LEFT JOIN categorie_produit c ON p.categorie_id = c.id_categorie
    WHERE f.date_facture IS NOT NULL {where}
    GROUP BY p.id_produit, p.nom_produit, p.code_produit, c.nom_categorie
    ORDER BY ca_produit DESC
    LIMIT {limite}
    """
    return load_data(query)

def get_ventes_par_categorie(annee=None):
    where = f"AND strftime('%Y', f.date_facture) = '{annee}'" if annee else ""
    query = f"""
    SELECT 
        COALESCE(c.nom_categorie, 'Sans catégorie') as nom_categorie,
        SUM(l.quantite * l.prix_unitaire) as ca_categorie,
        SUM(l.quantite) as quantite_vendue
    FROM ligne_facturec l
    JOIN facturec f ON l.facturec_id = f.id_facturec
    JOIN produit p ON l.produit_id = p.id_produit
    LEFT JOIN categorie_produit c ON p.categorie_id = c.id_categorie
    WHERE f.date_facture IS NOT NULL {where}
    GROUP BY c.nom_categorie
    ORDER BY ca_categorie DESC
    """
    return load_data(query)

def get_stocks_actuels():
    query = """
    SELECT 
        p.nom_produit,
        p.code_produit,
        COALESCE(c.nom_categorie, 'Sans catégorie') as nom_categorie,
        s.quantite_physique,
        s.quantite_theorique,
        m.nom_magasin,
        (s.quantite_physique - s.quantite_theorique) as ecart
    FROM stock s
    JOIN produit p ON s.produit_id = p.id_produit
    LEFT JOIN categorie_produit c ON p.categorie_id = c.id_categorie
    JOIN magasin m ON s.magasin_id = m.id_magasin
    WHERE s.quantite_physique > 0
    ORDER BY s.quantite_physique DESC
    """
    return load_data(query)

def get_approvisionnements():
    query = """
    SELECT 
        r.id_reception,
        r.date_reception,
        f.nom_fournisseur,
        p.nom_produit,
        l.quantite,
        l.prix_unitaire,
        (l.quantite * l.prix_unitaire) as montant_total,
        CAST(strftime('%Y', r.date_reception) AS INTEGER) as annee,
        CAST(strftime('%m', r.date_reception) AS INTEGER) as mois
    FROM reception r
    JOIN fournisseur f ON r.fournisseur_id = f.id_fournisseur
    JOIN ligne_reception l ON r.id_reception = l.reception_id
    JOIN produit p ON l.produit_id = p.id_produit
    WHERE r.date_reception IS NOT NULL
    ORDER BY r.date_reception DESC
    """
    return load_data(query)

def get_top_clients(annee=None, limite=10):
    where = f"AND strftime('%Y', f.date_facture) = '{annee}'" if annee else ""
    query = f"""
    SELECT 
        c.nom_client,
        COUNT(DISTINCT f.id_facturec) as nb_achats,
        SUM(l.quantite * l.prix_unitaire) as total_achats
    FROM facturec f
    JOIN clients c ON f.client_id = c.id_client
    JOIN ligne_facturec l ON f.id_facturec = l.facturec_id
    WHERE f.date_facture IS NOT NULL {where}
    GROUP BY c.id_client, c.nom_client
    ORDER BY total_achats DESC
    LIMIT {limite}
    """
    return load_data(query)
