# app.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from model_immo import predict_price

app = Flask(__name__)
CORS(app)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()  # données JSON venant du frontend
        if not data:
            return jsonify({"error": "Aucune donnée reçue"}), 400

        # Prédire avec ton modèle
        prix_estime = predict_price(data)

        return jsonify({"prix_estime": prix_estime})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/")
def test():
    return render_template("test.html")



if __name__ == "__main__":
    app.run(debug=True)
