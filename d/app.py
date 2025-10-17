from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from Agent import Agent
from usager import Usager
from vehicule import Vehicule
from api import app as api_app
from api_usager import app as api_usager_app
from api_vehicule import app as api_vehicule
import humanize
import mysql.connector
import os


app = Flask(__name__)
app.secret_key = 'DSNMLEZUIOeERBIUFZG9ZEUIG3Zé97c8UYG2398-23Y89723-T6-Eç75T_FZ76DI2UYFG873OT'


# Configuration base de données
db_config ={
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'controleroutiere'
}

# 📌 config upload images
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif', 'webp'}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def home():
    try:

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM agent")
        a = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM admin")
        p = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM vehicule")
        v = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usager")
        u = cursor.fetchone()[0]
        print(a,u,p, v)


        cursor.close()
        conn.close()


    except Exception as e:
      print(f"Erreur lors de la récupération des statistiques : {e}")
    a, p, v, u = 352, 98, 8743, 12569  # Valeurs par défaut si erreur
    user = session.get("agent")
    return render_template("home.html", a=a, p=p, u=u, v=v)

@app.route("/logout")
def logout():
    session.clear()
    print("Vous êtes déconnecté.", "info")
    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        mat = request.form["matricule"]
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM agent WHERE agentEmail = %s"
            cursor.execute(sql, (email,))
            agent = cursor.fetchone()

            cursor.close()
            conn.close()

            if agent is None:
                flash("Email ou mot de passe incorrect.", "danger")
                return redirect(url_for("login"))

            # Vérification du mot de passe avec bcrypt
            if agent['agentMatricule'] == mat and agent['agentEmail'] == email :
                session["agent_id"] = agent["id"]
                session["agent_email"] = agent["agentEmail"]
                flash("Connexion réussie.")
                print(session["agent_id"])
                return redirect(url_for("home"))
            else:
                flash("Email ou mot de passe incorrect.", "danger")
                return redirect(url_for("login"))



        except Exception as e:
            flash("Une erreur est survenue. Veuillez réessayer.", "danger")
            return redirect(url_for("login"))

    return render_template("loginAgent.html")

@app.route("/loginadm", methods=["GET", "POST"])
def loginadm():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM admin WHERE email = %s"
            cursor.execute(sql, (email,))
            admin = cursor.fetchone()

            cursor.close()
            conn.close()

            if admin is None:
                flash("Email ou mot de passe incorrect.", "danger")
                return redirect(url_for("loginadm"))

            # Vérification du mot de passe avec bcrypt
            if admin['motdepasse'] == password and admin['email'] == email :
                session["admin_id"] = admin["id"]
                session["admin_email"] = admin["email"]
                flash("Connexion réussie.")
                print(session["admin_id"])
                return redirect(url_for("gestionagent"))
            else:
                flash("Email ou mot de passe incorrect.", "danger")
                return redirect(url_for("loginadm"))

        except Exception as e:
            flash("Une erreur est survenue. Veuillez réessayer.", "danger")
            return redirect(url_for("loginadm"))

    return render_template("conne.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form["nom"]
        email = request.form["email"]
        password = request.form["password"]

        # Hash du mot de passe


        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            sql = "INSERT INTO admin (nom, email, motdepasse) VALUES (%s, %s, %s)"
            values = (nom, email, password)

            cursor.execute(sql, values)
            conn.commit()

            cursor.close()
            conn.close()

            flash("Inscription réussie. Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            return f"Erreur : {e}"

    return render_template("signAdmin.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nom = request.form["nom"]
        email = request.form["email"]
        phone = request.form["phone"]
        sujet = request.form["sujet"]
        contenu = request.form["message"]


        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            sql = "INSERT INTO contact (nom, email, phone, sujet, contenu) VALUES (%s, %s, %s, %s, %s)"
            values = (nom, email, phone, sujet, contenu)

            cursor.execute(sql, values)
            conn.commit()

            cursor.close()
            conn.close()

            flash("message envoyé.", "success")
            return redirect(url_for("contact"))
        except Exception as e:
            return f"Erreur : {e}"

    return render_template("contact.html")

@app.route("/histoire")
def historique():
    return render_template("historique.html")

@app.route("/apropos")
def apropos():
    return render_template("apropos.html")

@app.route("/service")
def service():
    return render_template("services.html")

@app.route("/gestionagent")
def gestionagent():
    conn = db_config      # connexion MySQL
    agent_model = Agent(conn)       # création de l’objet Agent
    stats = agent_model.get_stats() # appel de la méthode avec self
    agents = agent_model.get_all_agents() # appel de la méthode pour recuperer tout les agents

    for agent in agents:
        names = agent['agentName'].split()
        agent['initiales'] = ''.join([n[0].upper() for n in names])
        if agent['status'] == 'active' :
            statusClass = 'status-active'
        elif agent['status'] == 'inactive' :
            statusClass = 'status-inactive'
        else :
            statusClass = 'status-pending'

    return render_template("manaAgent.html", stats=stats, agents=agents, status = statusClass)

@app.route("/annonce")
def annonce():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM annonces")
        annonces = cursor.fetchall()
        date = annonces[0]['date_creation']
        date_pub= humanize.naturaltime(datetime.now() - date)
        print("Publié " + humanize.naturaltime(datetime.now() - date))
        cursor.close()
        conn.close()
        return render_template("annonce.html", annonces=annonces, date_pub=date_pub)
    except Exception as e:
        return f"Erreur : {e}"


@app.route("/gestusager")
def gestusager():
    conn = db_config      # connexion MySQL
    usager_model = Usager(conn)       # création de l’objet Agent
    stats = usager_model.get_stats() # appel de la méthode avec self
    usagers = usager_model.get_all_usagers() # appel de la méthode pour recuperer tout les usagers

    for usager in usagers:
        names = usager['userName'].split()
        usager['initiales'] = ''.join([n[0].upper() for n in names])
        if usager['userStatus'] == 'active' :
            statusClass = 'status-active'
        elif usager['userStatus'] == 'inactive' :
            statusClass = 'status-inactive'
        else :
            statusClass = 'status-pending'

    return render_template("manageUsager.html", stats=stats, usagers=usagers, status = statusClass)

@app.route("/gestvehicule")
def gestvehicule():
    conn = db_config      # connexion MySQL
    vehicule_model = Vehicule(conn)       # création de l’objet Agent
    stats = vehicule_model.get_stats() # appel de la méthode avec self
    vehicules = vehicule_model.get_all() # appel de la méthode pour recuperer tout les agents

    for vehicule in vehicules:
        names = vehicule['modele'].split()
        vehicule['initiales'] = ''.join([n[0].upper() for n in names])
        if vehicule['status'] == 'active' :
            statusClass = 'status-active'
        elif vehicule['status'] == 'inactive' :
            statusClass = 'status-inactive'
        else :
            statusClass = 'status-pending'

    return render_template("manageVehicule.html", stats=stats, vehicules=vehicules, status = statusClass)

@app.route("/adm")
def adm():
    return render_template("administrator.html")

@app.route("/test")
def test():
    return render_template("videosurveillance.html") 

@app.route("/dashboard_user")
def dashuser():
    return render_template("espaceAgent.html")

@app.route('/api/agents', methods=['POST'])
def add_agent():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Aucune donnée reçue"
            }), 400

        conn = db_config      # Add agent
        agent_model = Agent(conn)
        success = agent_model.add_agent(data)
        if success:
            return jsonify({
                "success": True,
                "message": "Agent ajouté avec succès"
            }), 201
        else:
            return jsonify({
                "success": False,
                "message": "Erreur lors de l'ajout de l'agent"
            }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur interne du serveur : {str(e)}"
        }), 500

@app.route('/api/agents/<int:id>', methods=['GET'])
def get_agent(id):
    conn = db_config      # get agent
    agent_model = Agent(conn)
    agent = agent_model.get_agent_by_id(id)
    return jsonify({"success": True, "data": agent}) if agent else jsonify({"success": False, "message": "Agent non trouvé"})

@app.route('/api/agents/<int:id>', methods=['PUT'])
def update_agent(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Aucune donnée reçue"
            }), 400

        conn = db_config      # update agent
        agent_model = Agent(conn)
        success = agent_model.update_agent(id, data)
        if success:
            return jsonify({
                "success": True,
                "message": "Agent modifié avec succès"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Erreur lors de la modification (aucune ligne mise à jour)"
            }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur interne du serveur : {str(e)}"
        }), 500

@app.route('/api/agents/<int:id>/status', methods=['PUT'])
def toggle_statdus(id):
    conn = db_config      # changer le statut d'un agent
    agent_model = Agent(conn)
    data = request.get_json()
    status = data.get('status')
    print (data)
    print (status)
    success = agent_model.toggle_agent_status(id, status)
    return jsonify({"success": success, "message": "Statut modifié avec succès" if success else "Erreur de modification"})

@app.route('/api_usager/usagers', methods=['POST'])
def add_usager():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Aucune donnée reçue"
            }), 400

        conn = db_config      # connexion MySQL
        usager_model = Usager(conn)
        success = usager_model.add_usager(data)
        if success:
            return jsonify({
                "success": True,
                "message": "Usager ajouté avec succès"
            }), 201
        else:
            return jsonify({
                "success": False,
                "message": "Erreur lors de l'ajout de l'Usager"
            }), 400 

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur interne du serveur : {str(e)}"
        }), 500

@app.route('/api_usager/usagers/<int:id>', methods=['GET'])
def get_usager(id):
    conn = db_config
    usager_model = Usager(conn)
    usager = usager_model.get_usager_by_id(id)
    return jsonify({"success": True, "data": usager}) if usager else jsonify({"success": False, "message": "Usager non trouvé"})

@app.route('/api_usager/usagers/<int:id>', methods=['PUT'])
def update_usager(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Aucune donnée reçue"
            }), 400

        conn = db_config      # connexion MySQL
        usager_model = Usager(**conn)
        success = usager_model.update_usager(id, data)
        if success:
            return jsonify({
                "success": True,
                "message": "Agent modifié avec succès"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Erreur lors de la modification (aucune ligne mise à jour)"
            }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur interne du serveur : {str(e)}"
        }), 500

@app.route('/api_usager/usagers/<int:id>/status', methods=['PUT']) 
def toggle_status(id):
    conn = db_config     # changer le statut
    usager_model = Usager(conn)
    data = request.get_json()
    status = data.get('status')
    success = usager_model.toggle_usager_status(id, status)
    return jsonify({"success": success, "message": "Statut modifié avec succès" if success else "Erreur de modification"})
@app.route('/api_vehicule/vehicules', methods=['GET'])
def api_get_all():
    return api_vehicule.get_all_vehicules(db_config)


@app.route('/api_vehicule/vehicules/<matricule>', methods=['GET'])
def api_get_one(matricule):
    return api_vehicule.get_vehicule(matricule, db_config)


@app.route('/api_vehicule/vehicules', methods=['POST'])
def api_add_vehicle():
    return api_vehicule.add_vehicule(db_config, request)


@app.route('/api_vehicule/vehicules/<matricule>', methods=['DELETE'])
def api_delete_vehicle(matricule):
    return api_vehicule.delete_vehicule(matricule, db_config)


if __name__ == "__main__":
    app.run(debug=True)
