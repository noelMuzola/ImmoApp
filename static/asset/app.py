import re
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
import os
import logging

app = Flask(__name__)
app.secret_key = 'DSNMLEZUIOeERBIUFZG9ZEUIG3Zé97c8UYG2398-23Y89723-T6-Eç75T_FZ76DI2UYFG873OT'

# Configuration base de données
db_config ={
    'host': 'localhost',
    'user': 'root',
    'password': '',  # ⚠️ adapte selon ton MySQL
    'database': 'immoapp'
}

# 📌 config upload images
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif', 'webp'}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    try:
        if "user_id" in session:
            GO = 1
        else:
            GO = 0

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        U = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM houses")
        P = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT commune) FROM houses")
        Q = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT quartier) FROM houses")
        C = cursor.fetchone()[0]

    
        cursor.close()
        conn.close()
        

    except Exception as e: 
      print(f"Erreur lors de la récupération des statistiques : {e}")
    U, P, Q, C = 0, 0, 0, 0  # Valeurs par défaut si erreur
    user = session.get("user")


    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Récupérer toutes les maisons
        cursor.execute("SELECT * FROM houses")
        houses = cursor.fetchall()
        cursor.execute("SELECT * FROM annonces")
        annonces = cursor.fetchall()
        # Pour chaque maison, récupérer ses images
        for house in houses:
            cursor.execute("SELECT filename FROM house_images WHERE house_id = %s", (house["id"],))
            house["images"] = cursor.fetchall()

        cursor.close()
        conn.close()
            
            
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM users")
            U = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM houses")
            P = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT commune) FROM houses")
            Q = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT quartier) FROM houses")
            C = cursor.fetchone()[0]

        
            cursor.close()
            conn.close()
            

        except Exception as e: 
            print(f"Erreur lors de la récupération des statistiques : {e}")
            U, P, Q, C = 0, 0, 0, 0  # Valeurs par défaut si erreur

        return render_template("index.html",go=GO, p=P, u=U, c=C, q=Q, houses=houses, annonces=annonces)
    except Exception as e:
        return f"Erreur : {e}"


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
        pseudo = request.form["pseudo"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_Password"]

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return redirect(url_for("register"))

        # Hash du mot de passe
        

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            sql = "INSERT INTO users (pseudo, email, password) VALUES (%s, %s, %s)"
            values = (pseudo, email, password)

            cursor.execute(sql, values)
            conn.commit()

            cursor.close()
            conn.close()

            flash("Inscription réussie. Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            return f"Erreur : {e}"

    return render_template("register.html")

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

        return render_template("maison.html", houses=houses)
    except Exception as e:
        return f"Erreur : {e}"

@app.route("/add_annonce", methods=["GET", "POST"])
def add_annonce():
    if request.method == "POST":
        titre = request.form.get("titre")
        description = request.form.get("description")
        categorie = request.form.get("categorie")
        budget = request.form.get("budget")
        user_id = session['user_id']
        commune = request.form.get("commune")
        quartier = request.form.get("quartier")

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            sql = """INSERT INTO annonces (titre, description, type, budget, user_id, commune, quartier) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (titre, description, categorie, budget, user_id, commune, quartier)

            cursor.execute(sql, values)
            conn.commit()

            cursor.close()
            conn.close()
            return redirect(url_for("annonce"))

        except Exception as e:
            return f"Erreur : {e}"

    return render_template("add_annonce.html")

@app.route("/annonce")
def annonce():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM annonces")
        annonces = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("annonce.html", annonces=annonces)
    except Exception as e:
        return f"Erreur : {e}"    

@app.route('/add_house', methods=['GET', 'POST'])
def add_house():
    if "user_id" in session:
        user_id = session['user_id']
    else:
        return redirect(url_for("login"))


    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        prix = request.form['prix']
        type_maison = request.form['type']
        chambre = request.form['chambre']
        toilette = request.form['sldb']
        surface = request.form['surface']
        adresse = request.form['adresse']
        salon = request.form['salon']
        cuisine = request.form['cuisine']
        proprietaire = request.form['proprietaire']
        commune = request.form['commune']
        quartier = request.form['quartier']
        categorie = request.form['categories']
        garanti = request.form['garanti']
        images = request.files.getlist("image")  # plusieurs fichiers

        
            
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Insert maison
            sql = """INSERT INTO houses 
                     (titre, description, prix, type, user_id,chambre, toilette, surface, adresse, salon, cuisine, proprietaire, garanti, commune, quartier, categorie) 
                     VALUES (%s, %s, %s, %s, %s, %s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (titre, description, prix, type_maison, user_id, chambre, toilette, surface, adresse, salon, cuisine, proprietaire, garanti, commune, quartier, categorie)
            cursor.execute(sql, values)
            house_id = cursor.lastrowid  # récupère l’ID de la maison

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
            return redirect(url_for('house'))
        except Exception as e:
            return f"Erreur : {e}"

        
        else : print ('format non valide')

    return render_template("add_house.html")
    
@app.route('/house/<int:house_id>')
def get_house_detail(house_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    print("gftgfhgfyuj")

    # Récupérer la maison
    cursor.execute("SELECT * FROM houses WHERE id = %s", (house_id,))
    house = cursor.fetchone()

    # Récupérer les images associées
    cursor.execute("SELECT image_url FROM house_images WHERE house_id = %s", (house_id,))
    images = cursor.fetchall()

    cursor.close()
    conn.close()

   # return jsonify({
    #    "house": house,
     #   "images": images
    #})

@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.args.get("q", "")  # récupère la valeur de la barre de recherche
    results = []

    if query:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT * FROM houses 
            WHERE titre LIKE %s OR description LIKE %s OR prix LIKE %s
        """
        cursor.execute(sql, (f"%{query}%", f"%{query}%", f"%{query}%"))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template("recherche.html", query=query, results=results)

@app.route("/profil", methods=['GET'])
def profil():
    if "user_id" in session:
        username = session['user_name']
        email    = session['user_email']
    else:
        return redirect(url_for("login"))
    
    return render_template("profil.html", username=username, email=email)   

@app.route("/dashboard")
def dashboard():
    # if "admin" in session:
    #     pseudo = session['admin_name']
    # else:
    #     return "n'avez pas accés à cette page"
    
    return render_template("dashboard.html")


@app.route("/my")
def my():
    return render_template("my.html")

@app.route("/logout")
def logout():
    session.clear()
    print("Vous êtes déconnecté.", "info")
    return redirect(url_for("home"))

@app.route("/test")
def test():
    return render_template("test.html")

@app.route('/modifier_utilisateur/<int:user_id>', methods=['GET', 'POST'])
def modifier_utilisateur(user_id):
    # Vérifier si l'utilisateur est connecté et est admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('login'))
    
    # Récupérer les données de l'utilisateur
    cur = mysql.connection.cursor()
    
    if request.method == 'GET':
        try:
            cur.execute("SELECT * FROM utilisateurs WHERE id = %s", (user_id,))
            user = cur.fetchone()
            
            if not user:
                flash('Utilisateur non trouvé.', 'danger')
                return redirect(url_for('liste_utilisateurs'))
                
            return render_template('modifier_utilisateur.html', user=user)
            
        except Exception as e:
            flash(f'Erreur lors de la récupération des données: {str(e)}', 'danger')
            return redirect(url_for('liste_utilisateurs'))
        
        finally:
            cur.close()
    
    elif request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form['telephone']
        adresse = request.form['adresse']
        etat = request.form['etat']
        password = request.form['password']
        
        # Validation des données
        errors = []
        
        # Validation du nom
        if not nom or len(nom) > 100:
            errors.append('Le nom doit être renseigné et faire moins de 100 caractères.')
        
        # Validation du prénom
        if not prenom or len(prenom) > 20:
            errors.append('Le prénom doit être renseigné et faire moins de 20 caractères.')
        
        # Validation de l'email
        if not email or len(email) > 50 or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Email invalide.')
        
        # Validation du téléphone
        if telephone and len(telephone) > 15:
            errors.append('Le téléphone ne doit pas dépasser 15 caractères.')
        
        # Validation de l'adresse
        if adresse and len(adresse) > 100:
            errors.append('L\'adresse ne doit pas dépasser 100 caractères.')
        
        # Validation du mot de passe
        if password and (len(password) < 6 or len(password) > 50):
            errors.append('Le mot de passe doit contenir entre 6 et 50 caractères.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            
            # Recharger les données utilisateur pour réafficher le formulaire
            cur.execute("SELECT * FROM utilisateurs WHERE id = %s", (user_id,))
            user = cur.fetchone()
            return render_template('modifier_utilisateur.html', user=user)
        
        try:
            # Vérifier si l'email existe déjà pour un autre utilisateur
            cur.execute("SELECT id FROM utilisateurs WHERE email = %s AND id != %s", (email, user_id))
            existing_user = cur.fetchone()
            
            if existing_user:
                flash('Cet email est déjà utilisé par un autre utilisateur.', 'danger')
                cur.execute("SELECT * FROM utilisateurs WHERE id = %s", (user_id,))
                user = cur.fetchone()
                return render_template('modifier_utilisateur.html', user=user)
            
            # Préparer la requête de mise à jour
            update_fields = []
            values = []
            
            update_fields.append("nom = %s")
            values.append(nom)
            
            update_fields.append("prenom = %s")
            values.append(prenom)
            
            update_fields.append("email = %s")
            values.append(email)
            
            update_fields.append("telephone = %s")
            values.append(telephone)
            
            update_fields.append("adresse = %s")
            values.append(adresse)
            
            update_fields.append("etat = %s")
            values.append(etat)
            
            # Si un nouveau mot de passe est fourni
            # if password:
            #     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            #     update_fields.append("password = %s")
            #     values.append(hashed_password)
            
            values.append(user_id)
            
            # Exécuter la mise à jour
            query = f"UPDATE utilisateurs SET {', '.join(update_fields)} WHERE id = %s"
            cur.execute(query, values)
            mysql.connection.commit()
            
            flash('Utilisateur modifié avec succès!', 'success')
            return redirect(url_for('liste_utilisateurs'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'danger')
            cur.execute("SELECT * FROM utilisateurs WHERE id = %s", (user_id,))
            user = cur.fetchone()
            return render_template('modifier_utilisateur.html', user=user)
        
        finally:
            cur.close()

if __name__ == "__main__":
    app.run(debug=True)
