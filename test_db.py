# test_db.py
import mysql.connector
import pandas as pd

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sellams_edimoshop'
    )
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print("✅ Connexion réussie !")
    print(f"📊 {len(tables)} tables trouvées")
    
    # Compter les enregistrements
    cursor.execute("SELECT COUNT(*) FROM facturec")
    count = cursor.fetchone()[0]
    print(f"📄 Factures : {count} enregistrements")
    
    cursor.execute("SELECT COUNT(*) FROM clients")
    count = cursor.fetchone()[0]
    print(f"👥 Clients : {count} enregistrements")
    
    cursor.execute("SELECT COUNT(*) FROM produit")
    count = cursor.fetchone()[0]
    print(f"📦 Produits : {count} enregistrements")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur : {e}")