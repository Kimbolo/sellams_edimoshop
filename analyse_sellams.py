import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration de la connexion
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sellams_edimoshop'
}

# Connexion à la base de données
conn = mysql.connector.connect(**config)

# 1. ANALYSE DES APPROVISIONNEMENTS
print("=" * 60)
print("ANALYSE DES APPROVISIONNEMENTS")
print("=" * 60)

# Récupération des réceptions
receptions_query = """
SELECT 
    r.id_reception,
    r.date_reception,
    f.nom_fournisseur,
    lr.quantite,
    lr.prix_unitaire,
    p.nom_produit,
    p.code_produit
FROM reception r
JOIN fournisseur f ON r.fournisseur_id = f.id_fournisseur
JOIN ligne_reception lr ON r.id_reception = lr.reception_id
JOIN produit p ON lr.produit_id = p.id_produit
WHERE r.date_reception >= DATE_SUB(NOW(), INTERVAL 3 YEAR)
ORDER BY r.date_reception DESC
"""

receptions = pd.read_sql(receptions_query, conn)
print(f"Nombre total de réceptions analysées : {len(receptions)}")
print("\nAperçu des 5 premières réceptions :")
print(receptions.head())

# 2. ANALYSE DES STOCKS
print("\n" + "=" * 60)
print("ANALYSE DES STOCKS")
print("=" * 60)

stocks_query = """
SELECT 
    s.id_stock,
    p.nom_produit,
    p.code_produit,
    s.quantite_physique,
    s.quantite_theorique,
    s.date_maj,
    m.nom_magasin
FROM stock s
JOIN produit p ON s.produit_id = p.id_produit
JOIN magasin m ON s.magasin_id = m.id_magasin
WHERE s.quantite_physique > 0
ORDER BY s.quantite_physique DESC
LIMIT 50
"""

stocks = pd.read_sql(stocks_query, conn)
print(f"Nombre de produits en stock : {len(stocks)}")
print("\nTop 10 des produits les plus en stock :")
print(stocks.head(10))

# 3. ANALYSE DES VENTES
print("\n" + "=" * 60)
print("ANALYSE DES VENTES")
print("=" * 60)

ventes_query = """
SELECT 
    f.id_facturec,
    f.date_facture,
    c.nom_client,
    lf.quantite,
    lf.prix_unitaire,
    (lf.quantite * lf.prix_unitaire) as montant_ligne,
    p.nom_produit
FROM facturec f
JOIN clients c ON f.client_id = c.id_client
JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
JOIN produit p ON lf.produit_id = p.id_produit
WHERE f.date_facture >= DATE_SUB(NOW(), INTERVAL 3 YEAR)
ORDER BY f.date_facture DESC
"""

ventes = pd.read_sql(ventes_query, conn)
print(f"Nombre de lignes de vente : {len(ventes)}")
print(f"Chiffre d'affaires total : {ventes['montant_ligne'].sum():,.2f} FCFA")

# 4. ANALYSE PAR ANNÉE
ventes['annee'] = pd.to_datetime(ventes['date_facture']).dt.year
ventes['mois'] = pd.to_datetime(ventes['date_facture']).dt.month

ventes_annuelles = ventes.groupby('annee').agg({
    'montant_ligne': 'sum',
    'quantite': 'sum'
}).reset_index()

print("\nÉvolution des ventes par année :")
print(ventes_annuelles)

# 5. CRÉATION DES VISUALISATIONS
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Graphique 1 : Évolution des ventes
ventes_par_mois = ventes.groupby(['annee', 'mois'])['montant_ligne'].sum().unstack().T
ventes_par_mois.plot(ax=axes[0, 0], marker='o')
axes[0, 0].set_title('Évolution mensuelle des ventes')
axes[0, 0].set_xlabel('Mois')
axes[0, 0].set_ylabel('CA (FCFA)')
axes[0, 0].legend(title='Année')

# Graphique 2 : Top 10 produits
top_produits = ventes.groupby('nom_produit')['quantite'].sum().sort_values(ascending=False).head(10)
top_produits.plot(kind='bar', ax=axes[0, 1])
axes[0, 1].set_title('Top 10 des produits les plus vendus')
axes[0, 1].set_xlabel('Produit')
axes[0, 1].set_ylabel('Quantité vendue')
axes[0, 1].tick_params(axis='x', rotation=45)

# Graphique 3 : Distribution des montants
axes[1, 0].hist(ventes['montant_ligne'], bins=50, edgecolor='black')
axes[1, 0].set_title('Distribution des montants de vente')
axes[1, 0].set_xlabel('Montant (FCFA)')
axes[1, 0].set_ylabel('Fréquence')

# Graphique 4 : Analyse des réceptions par fournisseur
fournisseurs_achats = receptions.groupby('nom_fournisseur')['quantite'].sum().sort_values(ascending=False).head(10)
fournisseurs_achats.plot(kind='barh', ax=axes[1, 1])
axes[1, 1].set_title('Top 10 des fournisseurs par volume')
axes[1, 1].set_xlabel('Quantité reçue')
axes[1, 1].set_ylabel('Fournisseur')

plt.tight_layout()
plt.savefig('analyse_sellams.png', dpi=300, bbox_inches='tight')
plt.show()

# 6. EXPORT DES DONNÉES POUR RAPPORT
with pd.ExcelWriter('rapport_sellams.xlsx', engine='openpyxl') as writer:
    ventes.to_excel(writer, sheet_name='Ventes', index=False)
    receptions.to_excel(writer, sheet_name='Receptions', index=False)
    stocks.to_excel(writer, sheet_name='Stocks', index=False)
    ventes_annuelles.to_excel(writer, sheet_name='Ventes_Annuelles', index=False)

print("\n Rapport exporté dans 'rapport_sellams.xlsx'")
print("Graphiques sauvegardés dans 'analyse_sellams.png'")

conn.close()