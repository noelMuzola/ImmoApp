from flask import Flask, request, jsonify
from flask_cors import CORS
from User import User
from config import db_config

# Initialisation de l’application Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Instancier la classe House
user_model = User(db_config)


# ====================== ROUTES GET ======================

@app.route("/api/users", methods=["GET"])
def get_users():
    """Récupérer toutes les users avec filtres"""
    filters = {
        "etat": request.args.get("etat", "all"),
        "date_creation": request.args.get("date_creation", "all"),
        "search": request.args.get("search", "")
    }
    users = user_model.get_all_users(filters)
    return jsonify({"success": True, "data": users})


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Récupérer un user spécifique par ID"""
    user = user_model.get_user_by_id(user_id)
    if user:
        return jsonify({"success": True, "data": user})
    else:
        return jsonify({"success": False, "message": "User non trouvée"}), 404


@app.route("/api/users/stats", methods=["GET"])
def get_user_stats():
    """Récupérer les statistiques des users"""
    stats = user_model.get_stats()
    return jsonify({"success": True, "data": stats})


# ====================== ROUTES POST ======================

@app.route("/api/users", methods=["POST"])
def add_user():
    """Ajouter un nouveau user"""
    data = request.get_json(force=True)
    errors = []

    # Validation des champs obligatoires
    required_fields = ["nom", "prenom", "password" "telephone", "image_profile","adresse"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Le champ '{field}' est requis")

    # Vérification doublon d’adresse
    if data.get("adresse") and user_model.address_exists(data["adresse"]):
        errors.append("Un user avec cette adresse existe déjà")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # Insertion dans la base
    new_id = user_model.add_user(data)
    return jsonify({"success": True, "message": "User ajoutée avec succès", "id": new_id}), 201


@app.route("/api/users/update", methods=["POST"])
def update_user():
    """Mettre à jour un user existante"""
    data = request.get_json(force=True)
    user_id = data.get("id")

    if not user_id:
        return jsonify({"success": False, "message": "L’ID du user est requis"}), 400

    errors = []

    required_fields = ["nom", "prenom", "telephone", "email", "image_profile", "adresse"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Le champ '{field}' est requis")

    # Vérifier doublon d’adresse (hors user actuelle)
    if data.get("adresse") and user_model.address_exists(data["adresse"], exclude_id=user_id):
        errors.append("Un autre user avec cette adresse existe déjà")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    user_model.update_user(user_id, data)
    return jsonify({"success": True, "message": "User mise à jour avec succès"})


# ====================== ROUTE PUT ======================

@app.route("/api/users/toggle-status", methods=["PUT"])
def toggle_user_status():
    """Changer le statut d’un user"""
    data = request.get_json(force=True)
    user_id = data.get("id")
    status = data.get("etat", "active")

    if not user_id:
        return jsonify({"success": False, "message": "ID requis"}), 400

    user_model.toggle_user_status(user_id, status)
    return jsonify({"success": True, "message": "Statut de user modifié avec succès"})


# ====================== ROUTE DELETE ======================

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Supprimer un user"""
    user_model.delete_house(user_id)
    return jsonify({"success": True, "message": "User supprimée avec succès"})


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
