# model_immo.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Charger les données
data = pd.read_csv("immoApp.csv", sep=";")

# Préparation
y = data["Prix"]
X = data.drop("Prix", axis=1)
X = pd.get_dummies(X, drop_first=True)

# Séparation train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Entraînement du modèle
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Fonction de prédiction
def predict_price(features: dict):
    """features est un dict avec les caractéristiques de la maison"""
    nouvelle_maison = pd.DataFrame([features])
    nouvelle_maison = pd.get_dummies(nouvelle_maison)
    nouvelle_maison = nouvelle_maison.reindex(columns=X_train.columns, fill_value=0)
    prediction = model.predict(nouvelle_maison)
    return float(prediction[0])
