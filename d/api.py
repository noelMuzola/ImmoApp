from flask import Flask, request, jsonify
from flask_cors import CORS
from Agent import Agent
from config import db_config

# Initialisation de l’application Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Instancier la classe Agent
agent_model = Agent(db_config)


# ====================== ROUTES GET ======================

@app.route("/api/agents", methods=["GET"])
def get_agents():
    """Récupérer tous les agents avec filtres"""
    filters = {
        "status": request.args.get("status", "all"),
        "grade": request.args.get("grade", "all"),
        "district": request.args.get("district", "all"),
        "search": request.args.get("search", "")
    }
    agents = agent_model.get_all_agents(filters)
    return jsonify({"success": True, "data": agents})


@app.route("/api/agents/<int:agent_id>", methods=["GET"])
def get_agent(agent_id):
    """Récupérer un agent spécifique par ID"""
    agent = agent_model.get_agent_by_id(agent_id)
    if agent:
        return jsonify({"success": True, "data": agent})
    else:
        return jsonify({"success": False, "message": "Agent non trouvé"}), 404


@app.route("/api/agents/stats", methods=["GET"])
def get_stats():
    """Récupérer les statistiques des agents"""
    stats = agent_model.get_stats()
    return jsonify({"success": True, "data": stats})


# ====================== ROUTES POST ======================

@app.route("/api/agents", methods=["POST"])
def add_agent():
    """Ajouter un nouvel agent"""
    data = request.get_json(force=True)
    errors = []

    # Validation des champs obligatoires
    if not data.get("agentName"):
        errors.append("Le nom est requis")
    if not data.get("agentEmail"):
        errors.append("L'email est requis")
    if not data.get("agentMatricule"):
        errors.append("Le matricule est requis")
    if not data.get("agentGrade"):
        errors.append("Le grade est requis")
    if not data.get("agentDistrict"):
        errors.append("Le district est requis")

    # Validation doublons
    if agent_model.email_exists(data["agentEmail"]):
        errors.append("Cet email est déjà utilisé")
    if agent_model.matricule_exists(data["agentMatricule"]):
        errors.append("Ce matricule est déjà utilisé")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # Insertion dans la base
    new_id = agent_model.add_agent(data)
    return jsonify({"success": True, "message": "Agent ajouté avec succès", "id": new_id}), 201


@app.route("/api/agents/update", methods=["POST"])
def update_agent():
    """Mettre à jour un agent existant"""
    data = request.get_json(force=True)
    agent_id = data.get("id")
    if not agent_id:
        return jsonify({"success": False, "message": "ID requis"}), 400

    errors = []

    # Validation des champs
    if not data.get("agentName"):
        errors.append("Le nom est requis")
    if not data.get("agentEmail"):
        errors.append("L'email est requis")
    if not data.get("agentMatricule"):
        errors.append("Le matricule est requis")
    if not data.get("agentGrade"):
        errors.append("Le grade est requis")
    if not data.get("agentDistrict"):
        errors.append("Le district est requis")

    # Vérifier les doublons (exclure l’agent actuel)
    if agent_model.email_exists(data["agentEmail"], agent_id):
        errors.append("Cet email est déjà utilisé")
    if agent_model.matricule_exists(data["agentMatricule"], agent_id):
        errors.append("Ce matricule est déjà utilisé")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    agent_model.update_agent(agent_id, data)
    return jsonify({"success": True, "message": "Agent modifié avec succès"})


# ====================== ROUTE PUT ======================

@app.route("/api/agents/toggle-status", methods=["PUT"])
def toggle_agent_status():
    """Changer le statut d’un agent"""
    data = request.get_json(force=True)
    agent_id = data.get("id")
    status = data.get("status", "active")

    if not agent_id:
        return jsonify({"success": False, "message": "ID requis"}), 400

    agent_model.toggle_agent_status(agent_id, status)
    return jsonify({"success": True, "message": "Statut modifié avec succès"})


# ====================== ROUTE DELETE ======================

@app.route("/api/agents/<int:agent_id>", methods=["DELETE"])
def delete_agent(agent_id):
    """Supprimer un agent"""
    agent_model.delete_agent(agent_id)
    return jsonify({"success": True, "message": "Agent supprimé avec succès"})


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
