from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename 
from datetime import datetime
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
    'database': 'immoapp'
}

#  configuration upload images
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif', 'webp'}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Récupérer toutes les maisons
        cursor.execute("SELECT * FROM houses ORDER BY date_creation DESC LIMIT 6")
        houses = cursor.fetchall()
        cursor.execute("SELECT * FROM annonces ORDER BY date_creation DESC LIMIT 6")
        annonces = cursor.fetchall()

        # Pour chaque maison, récupérer ses images
        for house in houses:
            cursor.execute("SELECT filename FROM house_images WHERE house_id = %s", (house["id"],))
            house["images"] = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("index.html", houses=houses, annonces=annonces)
    except Exception as e:
        return f"Erreur : {e}"

@app.route("/logout")
def logout():
    session.clear()
    print("Vous êtes déconnecté.", "info")
    return redirect(url_for("home"))

@app.route("/loggin", methods=["GET", "POST"])
def loggin():
    if request.method == "POST":
        pseudo = request.form["pseudo"]
        password = request.form["password"]

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM admin WHERE pseudo = %s"
            cursor.execute(sql, (pseudo,))
            adm = cursor.fetchone()

            cursor.close()
            conn.close()

            if adm['pseudo'] != pseudo:
                flash("Email ou mot de passe incorrect.", "danger")
                print('danger pseudo')
                return redirect(url_for("loggin"))

            # Vérification du mot de passe avec bcrypt
            if adm['password'] == password:
                session["adm_id"] = adm["id"]
                session["adm_pseudo"] = adm["pseudo"]
                flash("Connexion réussie. Bienvenue, " + adm["pseudo"], "success")
                print(session["adm_id"])
                return redirect(url_for("dash"))
            else:
                flash("Email ou mot de passe incorrect.", "danger")
                print("danger password")
                return redirect(url_for("login"))

        except Exception as e:
            flash("Une erreur est survenue. Veuillez réessayer.", "danger")
            print("danger total")
            return redirect(url_for("login"))
            

    return render_template("copy.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user is None:
                flash("Email ou mot de passe incorrect.", "danger")
                return redirect(url_for("login"))

            # Vérification du mot de passe avec bcrypt
            if user['password'] == password:
                session["user_id"] = user["id"]
                session["user_name"] = user["nom"]
                session["user_email"] = user["email"]
                flash("Connexion réussie. Bienvenue, " + user["nom"], "success")
                print(session["user_id"])
                return redirect(url_for("home"))
            else:
                flash("Email ou mot de passe incorrect.", "danger")
                return redirect(url_for("login"))



        except Exception as e:
            flash("Une erreur est survenue. Veuillez réessayer.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        email = request.form["email"]
        telephone = request.form["phone"]
        password = request.form["password"]
        confirm_password = request.form["confirmPassword"]

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return redirect(url_for("register"))

        # Hash du mot de passe
        

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            sql = "INSERT INTO users (nom, prenom, password, telephone, email) VALUES (%s, %s, %s, %s, %s)"
            values = (nom, prenom, password, telephone, email)

            cursor.execute(sql, values)
            conn.commit()

            cursor.close()
            conn.close()

            flash("Inscription réussie. Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            return f"Erreur : {e}"

    return render_template("register.html")

@app.route("/tejirerieij")
def profil():
    return render_template("profil.html")

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
    
@app.route("/house")
def house():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Récupérer toutes les maisons
        cursor.execute("SELECT * FROM houses")
        houses = cursor.fetchall()

        # Pour chaque maison, récupérer ses images
        for house in houses:
            cursor.execute("SELECT filename FROM house_images WHERE house_id = %s", (house["id"],))
            
            house["images"] = cursor.fetchall()
           
        cursor.close()
        conn.close()
       
        return render_template("house.html", houses=houses)
        
    except Exception as e:
        return f"Erreur : {e}"
    
@app.route("/house/<int:house_id>/json")
def house_detail_json(house_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM houses WHERE id = %s", (house_id,))
        house = cursor.fetchone()

        if not house:
            return jsonify({"error": "Maison introuvable"}), 404

        # Charger les images associées
        cursor.execute("SELECT filename FROM house_images WHERE house_id = %s", (house_id,))
        images = cursor.fetchall()
        house["images"] = images

        return jsonify(house)
    except Exception as e:
        print(e)
        return jsonify({"error": "Erreur lors du chargement des détails"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()  
    

@app.route('/dlihldsuhisudaiu', methods=['GET', 'POST'])
def addHouse():
    if "user_id" in session:
        user_id = session['user_id']
    else:
        return redirect(url_for("login"))


    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        prix = request.form['prix']
        type = request.form['type']
        chambre = request.form['chambre']
        toilette = request.form['sldb']
        surface = request.form['surface']
        adresse = request.form['adresse']
        salon = request.form['salon']
        cuisine = request.form['cuisine']
        commune = request.form['commune']
        quartier = request.form['quartier']
        categorie = request.form['categorie']
        garantie = request.form['garantie']
        images = request.files.getlist("image")  # plusieurs fichiers
        piece = request.form['piece']
        contactPhone = request.form['contactPhone']
        contactNom = request.form['contactNom']
        print(images)
        
            
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Insert maison
            sql = """INSERT INTO houses 
                     (titre, description, prix, type, user_id,chambre, toilette, surface, adresse, salon, cuisine, garantie, commune, quartier, categorie, piece, contactPhone, contactNom) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (titre, description, prix, type, user_id, chambre, toilette, surface, adresse, salon, cuisine, garantie, commune, quartier, categorie, piece, contactPhone, contactNom)
            cursor.execute(sql,  values)
            house_id = cursor.lastrowid  # récupère l’ID de la maison
            print(images)

            # Sauvegarde des images
            for file in images:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                    cursor.execute("INSERT INTO house_images (house_id, filename) VALUES (%s, %s)", 
                                   (house_id, filename))                

            conn.commit()
            cursor.close()
            conn.close()
            print(images)
            return redirect(url_for('house'))
        except Exception as e:
            return f"Erreur : {e}"

        
        else : 
            print ('format non valid e')

    return render_template("add_house.html")

@app.route("/teheeh", methods=["GET", "POST"])
def addAnnonce():
    session.permanent = True
    if request.method == "POST":
        titre = request.form.get("titre")
        description = request.form.get("description")
        categorie = request.form.get("categorie")
        type = request.form.get("type")
        budget = request.form.get("budget")
        user_id = session['user_id']
        commune = request.form.get("commune")
        quartier = request.form.get("quartier")
        chambre = request.form.get("chambre")
        sldb = request.form.get("sldb")
        piece = request.form.get("piece")
        surface = request.form.get("surface")
        contactNom = request.form.get("contactNom")
        contactEmail = request.form.get("contactEmail")
        contactPhone = request.form.get("contactPhone")


        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            sql = """INSERT INTO annonces (titre, description, categorie, type, budget, user_id, commune, quartier, chambre, piece, surface, sldb, contactNom, contactEmail, contactPhone) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (titre, description, categorie, type, budget, user_id, commune, quartier, chambre, piece, surface, sldb, contactNom, contactEmail, contactPhone)

            cursor.execute(sql, values)
            conn.commit()

            cursor.close()
            conn.close()
            return redirect(url_for("annonce"))

        except Exception as e:
            return f"Erreur : {e}"

    return render_template("add_annonce.html")

@app.route("/test")
def test():
    return render_template("test1 copy 5.html")

@app.route("/dashboard")
def dash():
    if "adm_id" in session:
        adm_id = session['adm_id']
        pseudo = session['adm_pseudo']
    else:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/dashboard_user")
def dashuser():
    if "user_id" in session:
        user_id = session['user_id']
    else:
        return redirect(url_for("login"))
    return render_template("dashboard_user.html")

@app.route("/prediction")
def prediction():
    if "user_id" in session:
        user_id = session['user_id']
    else:
        return redirect(url_for("login"))
    return render_template("prediction.html")

if __name__ == "__main__":
    app.run(debug=True)
