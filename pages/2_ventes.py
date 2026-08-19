import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from utils.database import *
from utils.charts import *
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Prédictions IA", page_icon="🤖", layout="wide")

st.title("🤖 Prédictions IA - Sellams Edimo Sports")
st.markdown("---")

# Chargement des données pour prédiction
st.subheader("📊 Données Historiques pour Prédiction")

query_pred = """
SELECT 
    p.id_produit,
    p.nom_produit,
    cp.nom_categorie,
    YEAR(f.date_facture) as annee,
    MONTH(f.date_facture) as mois,
    DAYOFWEEK(f.date_facture) as jour_semaine,
    SUM(lf.quantite) as quantite_vendue,
    AVG(lf.prix_unitaire) as prix_moyen
FROM facturec f
JOIN ligne_facturec lf ON f.id_facturec = lf.facturec_id
JOIN produit p ON lf.produit_id = p.id_produit
LEFT JOIN categorie_produit cp ON p.categorie_id = cp.id_categorie
WHERE f.date_facture >= DATE_SUB(NOW(), INTERVAL 3 YEAR)
GROUP BY p.id_produit, p.nom_produit, cp.nom_categorie, 
         YEAR(f.date_facture), MONTH(f.date_facture), DAYOFWEEK(f.date_facture)
ORDER BY annee DESC, mois DESC
"""

df_pred = load_data(query_pred)

if not df_pred.empty:
    # Préparation des données
    df_pred['mois_sin'] = np.sin(2 * np.pi * df_pred['mois'] / 12)
    df_pred['mois_cos'] = np.cos(2 * np.pi * df_pred['mois'] / 12)
    
    # Encodage des catégories
    categories = df_pred['nom_categorie'].unique()
    cat_mapping = {cat: i for i, cat in enumerate(categories)}
    df_pred['categorie_encoded'] = df_pred['nom_categorie'].map(cat_mapping)
    
    # Features
    feature_cols = ['annee', 'mois', 'jour_semaine', 'prix_moyen', 'categorie_encoded', 'mois_sin', 'mois_cos']
    X = df_pred[feature_cols]
    y = df_pred['quantite_vendue']
    
    # Division des données
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entraînement du modèle
    with st.spinner("Entraînement du modèle de prédiction en cours..."):
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Évaluation
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
    
    # Affichage des performances
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Précision du Modèle (R²)", f"{r2:.2%}")
    with col2:
        st.metric("📈 Erreur Moyenne", f"{mae:.0f} unités")
    
    st.markdown("---")
    
    # Prédictions pour les produits phares
    st.subheader("🎯 Prédictions pour les Produits Phares")
    
    # Sélection des top produits
    top_products = df_pred.groupby('nom_produit').agg({
        'quantite_vendue': 'sum'
    }).sort_values('quantite_vendue', ascending=False).head(10).reset_index()
    
    selected_product = st.selectbox(
        "Sélectionner un produit",
        options=top_products['nom_produit'].tolist()
    )
    
    if selected_product:
        # Prédiction pour les 6 prochains mois
        product_data = df_pred[df_pred['nom_produit'] == selected_product]
        
        if not product_data.empty:
            last_price = product_data['prix_moyen'].iloc[-1]
            last_cat = product_data['categorie_encoded'].iloc[-1]
            
            future_months = []
            predictions = []
            
            current_year = pd.Timestamp.now().year
            current_month = pd.Timestamp.now().month
            
            for i in range(1, 7):
                month = current_month + i
                year = current_year + (month // 12)
                month = month % 12
                if month == 0:
                    month = 12
                    year -= 1
                
                features = {
                    'annee': year,
                    'mois': month,
                    'jour_semaine': 1,
                    'prix_moyen': last_price,
                    'categorie_encoded': last_cat,
                    'mois_sin': np.sin(2 * np.pi * month / 12),
                    'mois_cos': np.cos(2 * np.pi * month / 12)
                }
                
                X_future = pd.DataFrame([features])
                pred = model.predict(X_future[feature_cols])[0]
                
                future_months.append(f"{month}/{year}")
                predictions.append(max(0, int(pred)))
            
            # Création du graphique
            fig = go.Figure()
            
            # Données historiques
            historique = product_data.groupby(['annee', 'mois']).agg({
                'quantite_vendue': 'sum'
            }).reset_index()
            historique['date'] = historique['mois'].astype(str) + '/' + historique['annee'].astype(str)
            
            fig.add_trace(go.Scatter(
                x=historique['date'],
                y=historique['quantite_vendue'],
                mode='lines+markers',
                name='Historique',
                line=dict(color='blue')
            ))
            
            # Prédictions
            fig.add_trace(go.Scatter(
                x=future_months,
                y=predictions,
                mode='lines+markers',
                name='Prédiction',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title=f'Prédictions des Ventes - {selected_product}',
                xaxis_title='Période',
                yaxis_title='Quantité Vendue',
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau des prédictions
            pred_df = pd.DataFrame({
                'Période': future_months,
                'Prédiction (unités)': predictions
            })
            st.dataframe(pred_df, use_container_width=True)
    
    # Données externes - Marché Camerounais
    st.markdown("---")
    st.subheader("🌍 Données du Marché Camerounais")
    
    # Simulation de données externes (à remplacer par API réelle)
    external_data = {
        'Sport': ['Football', 'Basketball', 'Athlétisme', 'Natation', 'Tennis', 'Volleyball'],
        'Popularité': [95, 78, 65, 52, 70, 60],
        'Tendance_Saison': [0.85, 0.75, 0.60, 0.50, 0.70, 0.65],
        'Croissance_2024': [0.12, 0.08, 0.05, 0.03, 0.09, 0.06]
    }
    df_external = pd.DataFrame(external_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            df_external,
            x='Sport',
            y='Popularité',
            title='Popularité des Sports au Cameroun',
            color='Popularité',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            df_external,
            x='Tendance_Saison',
            y='Croissance_2024',
            size='Popularité',
            text='Sport',
            title='Tendance vs Croissance par Sport',
            labels={'Tendance_Saison': 'Tendance Saison', 'Croissance_2024': 'Croissance 2024'}
        )
        fig.update_traces(textposition='top center')
        fig.update_layout(template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommandations
    st.markdown("---")
    st.subheader("💡 Recommandations Stratégiques")
    
    # Produits recommandés
    st.info("**Produits à forte croissance potentielle :**")
    for _, row in df_external.nlargest(3, 'Croissance_2024').iterrows():
        st.write(f"• **{row['Sport']}** - Croissance estimée : {row['Croissance_2024']:.1%}")
    
    # Produits à surveiller
    st.warning("**Produits nécessitant une attention particulière :**")
    for _, row in df_external.nsmallest(3, 'Tendance_Saison').iterrows():
        st.write(f"• **{row['Sport']}** - Tendance saisonnière : {row['Tendance_Saison']:.0%}")

else:
    st.warning("Pas assez de données historiques pour les prédictions.")