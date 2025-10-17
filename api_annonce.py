from flask import Flask, request, jsonify
from flask_cors import CORS
from House import House
from config import db_config

# Initialisation de l’application Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Instancier la classe House
house_model = House(db_config)


# ====================== ROUTES GET ======================

@app.route("/api/houses", methods=["GET"])
def get_houses():
    """Récupérer toutes les maisons avec filtres"""
    filters = {
        "type": request.args.get("type", "all"),
        "status": request.args.get("status", "all"),
        "commune": request.args.get("commune", "all"),
        "quartier": request.args.get("quartier", ""),
        "prix": request.args.get("prix", ""),
        "search": request.args.get("search", "")
    }
    houses = house_model.get_all_houses(filters)
    return jsonify({"success": True, "data": houses})


@app.route("/api/houses/<int:house_id>", methods=["GET"])
def get_house(house_id):
    """Récupérer une maison spécifique par ID"""
    house = house_model.get_house_by_id(house_id)
    if house:
        return jsonify({"success": True, "data": house})
    else:
        return jsonify({"success": False, "message": "Maison non trouvée"}), 404


@app.route("/api/houses/stats", methods=["GET"])
def get_house_stats():
    """Récupérer les statistiques des maisons"""
    stats = house_model.get_stats()
    return jsonify({"success": True, "data": stats})


# ====================== ROUTES POST ======================

@app.route("/api/houses", methods=["POST"])
def add_house():
    """Ajouter une nouvelle maison"""
    data = request.get_json(force=True)
    errors = []

    # Validation des champs obligatoires
    required_fields = ["titre", "description", "prix", "type", "categorie", "commune", "quartier", "adresse", "contactnom", "contactphone"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Le champ '{field}' est requis")

    # Vérification doublon d’adresse
    if data.get("adresse") and house_model.address_exists(data["adresse"]):
        errors.append("Une maison avec cette adresse existe déjà")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # Insertion dans la base
    new_id = house_model.add_house(data)
    return jsonify({"success": True, "message": "Maison ajoutée avec succès", "id": new_id}), 201


@app.route("/api/houses/update", methods=["POST"])
def update_house():
    """Mettre à jour une maison existante"""
    data = request.get_json(force=True)
    house_id = data.get("id")

    if not house_id:
        return jsonify({"success": False, "message": "L’ID de la maison est requis"}), 400

    errors = []

    required_fields = ["titre", "description", "prix", "type", "categorie", "commune", "quartier", "adresse", "contactnom", "contactphone"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Le champ '{field}' est requis")

    # Vérifier doublon d’adresse (hors maison actuelle)
    if data.get("adresse") and house_model.address_exists(data["adresse"], exclude_id=house_id):
        errors.append("Une autre maison avec cette adresse existe déjà")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    house_model.update_house(house_id, data)
    return jsonify({"success": True, "message": "Maison mise à jour avec succès"})


# ====================== ROUTE PUT ======================

@app.route("/api/houses/toggle-status", methods=["PUT"])
def toggle_house_status():
    """Changer le statut d’une maison"""
    data = request.get_json(force=True)
    house_id = data.get("id")
    status = data.get("status", "active")

    if not house_id:
        return jsonify({"success": False, "message": "ID requis"}), 400

    house_model.toggle_house_status(house_id, status)
    return jsonify({"success": True, "message": "Statut de la maison modifié avec succès"})


# ====================== ROUTE DELETE ======================

@app.route("/api/houses/<int:house_id>", methods=["DELETE"])
def delete_house(house_id):
    """Supprimer une maison"""
    house_model.delete_house(house_id)
    return jsonify({"success": True, "message": "Maison supprimée avec succès"})


# ====================== ERREURS ======================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "message": "Ressource introuvable"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "message": "Erreur serveur interne"}), 500


# ====================== MAIN ======================

if __name__ == "__main__":
    app.run(debug=True)
