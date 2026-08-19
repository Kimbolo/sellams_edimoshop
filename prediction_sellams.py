import pandas as pd
import numpy as np
import mysql.connector
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
import requests
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SellamsPredictor:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='sellams_edimoshop'
        )
        self.model = None
        self.feature_columns = []
        
    def load_data(self):
        """Charger les données historiques"""
        query = """
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
        JOIN categorie_produit cp ON p.categorie_id = cp.id_categorie
        WHERE f.date_facture >= DATE_SUB(NOW(), INTERVAL 3 YEAR)
        GROUP BY p.id_produit, p.nom_produit, cp.nom_categorie, 
                 YEAR(f.date_facture), MONTH(f.date_facture), DAYOFWEEK(f.date_facture)
        ORDER BY annee DESC, mois DESC
        """
        self.data = pd.read_sql(query, self.conn)
        print(f"✅ Données chargées : {len(self.data)} lignes")
        return self.data
    
    def load_external_data(self):
        """Charger les données externes (articles de saison - Cameroun)"""
        print("\n📥 Récupération des données externes...")
        
        # Simulation de données externes (à remplacer par API réelle)
        # Exemple: données de marché, tendances, saisonnalité
        external_data = {
            'sport': ['Football', 'Basketball', 'Athlétisme', 'Natation', 'Tennis'],
            'tendance_saison': [0.85, 0.75, 0.65, 0.55, 0.70],
            'popularite_cameroun': [0.95, 0.80, 0.70, 0.60, 0.75]
        }
        self.external_df = pd.DataFrame(external_data)
        
        # Simuler d'autres données de marché
        # Dans la réalité, vous utiliseriez une API ou un web scraping
        print("✅ Données externes chargées")
        return self.external_df
    
    def prepare_features(self):
        """Préparer les caractéristiques pour la prédiction"""
        # Encodage des variables catégorielles
        le_categorie = LabelEncoder()
        self.data['categorie_encoded'] = le_categorie.fit_transform(self.data['nom_categorie'])
        
        # Création de caractéristiques supplémentaires
        self.data['mois_sin'] = np.sin(2 * np.pi * self.data['mois'] / 12)
        self.data['mois_cos'] = np.cos(2 * np.pi * self.data['mois'] / 12)
        
        # Caractéristiques pour la prédiction
        self.feature_columns = ['annee', 'mois', 'jour_semaine', 'prix_moyen', 
                               'categorie_encoded', 'mois_sin', 'mois_cos']
        
        X = self.data[self.feature_columns]
        y = self.data['quantite_vendue']
        
        return X, y
    
    def train_models(self):
        """Entraîner les modèles de prédiction"""
        X, y = self.prepare_features()
        
        # Split des données
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Modèle Random Forest
        print("\n🔧 Entraînement du modèle Random Forest...")
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.rf_model.fit(X_train, y_train)
        
        # Prédictions et évaluation
        y_pred_rf = self.rf_model.predict(X_test)
        rf_mae = mean_absolute_error(y_test, y_pred_rf)
        rf_r2 = r2_score(y_test, y_pred_rf)
        
        print(f"✅ Random Forest - MAE: {rf_mae:.2f}, R²: {rf_r2:.2f}")
        
        # Modèle Gradient Boosting
        print("🔧 Entraînement du modèle Gradient Boosting...")
        self.gb_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
        self.gb_model.fit(X_train, y_train)
        
        y_pred_gb = self.gb_model.predict(X_test)
        gb_mae = mean_absolute_error(y_test, y_pred_gb)
        gb_r2 = r2_score(y_test, y_pred_gb)
        
        print(f"✅ Gradient Boosting - MAE: {gb_mae:.2f}, R²: {gb_r2:.2f}")
        
        # Choix du meilleur modèle
        if rf_r2 > gb_r2:
            self.model = self.rf_model
            print("✅ Modèle choisi : Random Forest")
        else:
            self.model = self.gb_model
            print("✅ Modèle choisi : Gradient Boosting")
        
        # Sauvegarde du modèle
        joblib.dump(self.model, 'sellams_prediction_model.pkl')
        joblib.dump(self.feature_columns, 'feature_columns.pkl')
        
        return self.model
    
    def predict_future(self, product_id, months_ahead=6):
        """Prédire les ventes futures pour un produit"""
        # Récupérer les dernières données du produit
        query = f"""
        SELECT 
            p.id_produit,
            p.nom_produit,
            cp.nom_categorie,
            lf.prix_unitaire as prix_actuel
        FROM produit p
        JOIN categorie_produit cp ON p.categorie_id = cp.id_categorie
        LEFT JOIN ligne_facturec lf ON p.id_produit = lf.produit_id
        WHERE p.id_produit = {product_id}
        LIMIT 1
        """
        product_data = pd.read_sql(query, self.conn)
        
        if product_data.empty:
            return None
        
        # Préparer les données futures
        future_predictions = []
        current_date = datetime.now()
        
        for i in range(1, months_ahead + 1):
            future_date = current_date + timedelta(days=30*i)
            
            # Créer les caractéristiques
            features = {
                'annee': future_date.year,
                'mois': future_date.month,
                'jour_semaine': future_date.weekday(),
                'prix_moyen': product_data['prix_actuel'].iloc[0] or 10000,
                'categorie_encoded': 0,  # À encoder correctement
                'mois_sin': np.sin(2 * np.pi * future_date.month / 12),
                'mois_cos': np.cos(2 * np.pi * future_date.month / 12)
            }
            
            # Prédiction
            if self.model:
                X_pred = pd.DataFrame([features])
                X_pred = X_pred[self.feature_columns]
                prediction = self.model.predict(X_pred)[0]
                
                future_predictions.append({
                    'date': future_date.strftime('%Y-%m'),
                    'prediction': max(0, int(prediction)),
                    'produit': product_data['nom_produit'].iloc[0]
                })
        
        return pd.DataFrame(future_predictions)
    
    def generate_report(self):
        """Générer un rapport de prédiction exploitable par la direction"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT DE PRÉDICTION - SELLAMS EDIMO SPORTS")
        print("=" * 60)
        
        # Top produits à prédire
        top_query = """
        SELECT 
            p.id_produit,
            p.nom_produit,
            SUM(lf.quantite) as total_vendu,
            AVG(lf.prix_unitaire) as prix_moyen
        FROM produit p
        JOIN ligne_facturec lf ON p.id_produit = lf.produit_id
        GROUP BY p.id_produit, p.nom_produit
        ORDER BY total_vendu DESC
        LIMIT 10
        """
        top_products = pd.read_sql(top_query, self.conn)
        
        print("\n🎯 PRÉDICTIONS POUR LES PRODUITS PHARES")
        print("-" * 60)
        
        predictions_summary = []
        for _, product in top_products.iterrows():
            pred = self.predict_future(product['id_produit'], 6)
            if pred is not None:
                total_pred = pred['prediction'].sum()
                moyenne_pred = pred['prediction'].mean()
                predictions_summary.append({
                    'Produit': product['nom_produit'],
                    'Ventes_actuelles': product['total_vendu'],
                    'Prédiction_6_mois': int(total_pred),
                    'Moyenne_mensuelle': int(moyenne_pred)
                })
        
        df_summary = pd.DataFrame(predictions_summary)
        print(df_summary.to_string(index=False))
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS STRATÉGIQUES")
        print("-" * 60)
        
        # Identifier les produits à forte croissance
        df_summary['ratio_prediction'] = df_summary['Prédiction_6_mois'] / (df_summary['Ventes_actuelles'] + 1)
        top_growth = df_summary.nlargest(3, 'ratio_prediction')
        
        print("\n📈 Produits avec forte croissance potentielle :")
        for _, row in top_growth.iterrows():
            print(f"  • {row['Produit']} - Croissance estimée : {row['ratio_prediction']:.2%}")
        
        print("\n⚠️ Produits nécessitant une attention particulière :")
        low_growth = df_summary.nsmallest(3, 'ratio_prediction')
        for _, row in low_growth.iterrows():
            print(f"  • {row['Produit']} - Baisse estimée : {row['ratio_prediction']:.2%}")
        
        # Sauvegarder le rapport
        df_summary.to_excel('rapport_prediction_sellams.xlsx', index=False)
        print("\n✅ Rapport sauvegardé : rapport_prediction_sellams.xlsx")
        
        return df_summary
    
    def close(self):
        self.conn.close()

# Exécution du script
if __name__ == "__main__":
    predictor = SellamsPredictor()
    
    # Chargement des données
    predictor.load_data()
    predictor.load_external_data()
    
    # Entraînement des modèles
    predictor.train_models()
    
    # Génération du rapport
    report = predictor.generate_report()
    
    predictor.close()