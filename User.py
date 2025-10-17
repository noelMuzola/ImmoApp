import mysql.connector

class User:
    def __init__(self, db_config):
        self.db = mysql.connector.connect(**db_config)
        self.cursor = self.db.cursor(dictionary=True)
        self.table = "users"

    # 1️⃣ Récupérer toutes les users
    def get_all_users(self, filters=None):
        if filters is None:
            filters = {}

        sql = f"SELECT * FROM {self.table} WHERE 1=1"
        params = []

        # Filtrage dynamique
        if 'etat' in filters and filters['etat'] != 'all':
            sql += " AND etat = %s"
            params.append(filters['etat'])

        if 'date_creation' in filters and filters['date_creation'] != 'all':
            sql += " AND date_creation = %s"
            params.append(filters['date_creation'])

        if 'search' in filters and filters['search']:
            sql += " AND (nom LIKE %s OR prenom LIKE %s OR telephone LIKE %s)"
            search_term = f"%{filters['search']}%"
            params.extend([search_term, search_term, search_term])

        sql += " ORDER BY date_creation DESC"
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    # 2️⃣ Récupérer un user par ID
    def get_user_by_id(self, user_id):
        sql = f"SELECT * FROM {self.table} WHERE id = %s"
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchone()

    # 3️⃣ Ajouter un nouveau user
    def add_user(self, data):
        sql = f"""
        INSERT INTO {self.table} 
        (nom, prenom, password, telephone, email, image_profile,adresse)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("nom"),
            data.get("prenom"),
            data.get("password"),
            data.get("telephone"),
            data.get("email"),
            data.get("image_profile"),
            data.get("adresse")
        )
        self.cursor.execute(sql, values)
        self.db.commit()
        return self.cursor.lastrowid

    # 4️⃣ Modifier un user
    def update_user(self, user_id, data):
        sql = f"""
        UPDATE {self.table} SET
            nom = %s,
            prenom = %s,
            telephone = %s,
            email = %s,
            image_profile = %s,
            adresse = %s
        WHERE id = %s
        """
        values = (
            data.get("nom"),
            data.get("prenom"),
            data.get("telephone"),
            data.get("email"),
            data.get("image_profile"),
            data.get("adresse"),
            user_id
         )
        self.cursor.execute(sql, values)
        self.db.commit()
        return True

    # 5️⃣ Changer le statut d'un user
    def toggle_user_status(self, user_id, status):
        sql = f"UPDATE {self.table} SET etat = %s WHERE id = %s"
        self.cursor.execute(sql, (status, user_id))
        self.db.commit()
        return True

    # 6️⃣ Supprimer un user
    def delete_user(self, user_id):
        sql = f"DELETE FROM {self.table} WHERE id = %s"
        self.cursor.execute(sql, (user_id,))
        self.db.commit()
        return True

    # 7️⃣ Obtenir les statistiques globales
    def get_stats(self):
        user_stats = {}

        self.cursor.execute(f"SELECT COUNT(*) as total FROM {self.table}")
        user_stats["total"] = self.cursor.fetchone()["total"]

        self.cursor.execute(f"SELECT COUNT(*) as active FROM {self.table} WHERE etat = 'active'")
        user_stats["active"] = self.cursor.fetchone()["active"]

        self.cursor.execute(f"SELECT COUNT(*) as desactive FROM {self.table} WHERE etat = 'desactive'")
        user_stats["desactive"] = self.cursor.fetchone()["desactive"]

        user_stats["rate"] = round((user_stats["active"] / user_stats["total"]) * 100) if user_stats["total"] > 0 else 0

        return user_stats

    # 8️⃣ Vérifier doublon par adresse
    def address_exists(self, adresse, exclude_id=None):
        sql = f"SELECT COUNT(*) as count FROM {self.table} WHERE adresse = %s"
        params = [adresse]
        if exclude_id:
            sql += " AND id != %s"
            params.append(exclude_id)

        self.cursor.execute(sql, tuple(params))
        return self.cursor.fetchone()["count"] > 0

    # 9️⃣ Fermer la connexion proprement
    def close(self):
        self.cursor.close()
        self.db.close()
