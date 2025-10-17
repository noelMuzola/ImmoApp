# House.py
import mysql.connector

class House:
    def __init__(self, db_config):
        self.db = mysql.connector.connect(**db_config)
        self.cursor = self.db.cursor(dictionary=True)
        self.table = "houses"

    # 1️⃣ Récupérer toutes les maisons
    def get_all_houses(self, filters=None):
        if filters is None:
            filters = {}

        sql = f"SELECT * FROM {self.table} WHERE 1=1"
        params = []

        # Filtrage dynamique
        if 'type' in filters and filters['type'] != 'all':
            sql += " AND houseType = %s"
            params.append(filters['type'])

        if 'status' in filters and filters['status'] != 'all':
            sql += " AND status = %s"
            params.append(filters['status'])

        if 'commune' in filters and filters['commune'] != 'all':
            sql += " AND commune = %s"
            params.append(filters['commune'])

        if 'quartier' in filters and filters['quartier']:
            sql += " AND quartier >= %s"
            params.append(filters['quartier'])

        if 'prix' in filters and filters['prix']:
            sql += " AND prix <= %s"
            params.append(filters['prix'])

        if 'search' in filters and filters['search']:
            sql += " AND (titre LIKE %s OR description LIKE %s OR categorie LIKE %s)"
            search_term = f"%{filters['search']}%"
            params.extend([search_term, search_term, search_term])

        sql += " ORDER BY date_creation DESC"
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    # 2️⃣ Récupérer une maison par ID
    def get_house_by_id(self, house_id):
        sql = f"SELECT * FROM {self.table} WHERE id = %s"
        self.cursor.execute(sql, (house_id,))
        return self.cursor.fetchone()

    # 3️⃣ Ajouter une nouvelle maison
    def add_house(self, data):
        sql = f"""
        INSERT INTO {self.table} 
        (titre, description, prix, user_id, type, categorie, contactnom, contactphone, piece, commune, surface, quartier, adresse, chambre,toilette, salon, cuisine, garantie)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("titre"),
            data.get("description"),
            data.get("prix"),
            data.get("type"),
            data.get("categorie"),
            data.get("adresse"),
            data.get("commune"),
            data.get("quartier"),
            data.get("chambre"),
            data.get("toilee"),
            data.get("salon"),
            data.get("piece"),
            data.get("contactphone"),
            data.get("contactnom"),
            data.get("user_id"),
            data.get("cuisine"),
            data.get("surface"),
            data.get("garantie")
        )
        self.cursor.execute(sql, values)
        self.db.commit()
        return self.cursor.lastrowid

    # 4️⃣ Modifier une maison
    def update_house(self, house_id, data):
        sql = f"""
        UPDATE {self.table} SET
            title = %s,
            description = %s,
            price = %s,
            houseType = %s,
            address = %s,
            district = %s,
            bedrooms = %s,
            bathrooms = %s,
            surface = %s,
            image = %s,
            status = %s
        WHERE id = %s
        """
        values = (
            data.get("titre"),
            data.get("description"),
            data.get("prix"),
            data.get("type"),
            data.get("categorie"),
            data.get("adresse"),
            data.get("commune"),
            data.get("quartier"),
            data.get("chambre"),
            data.get("toilee"),
            data.get("salon"),
            data.get("piece"),
            data.get("contactphone"),
            data.get("contactnom"),
            data.get("user_id"),
            data.get("cuisine"),
            data.get("surface"),
            data.get("garantie"),
            house_id
         )
        self.cursor.execute(sql, values)
        self.db.commit()
        return True

    # 5️⃣ Changer le statut d'une maison (ex: disponible / vendue)
    def toggle_house_status(self, house_id, status):
        sql = f"UPDATE {self.table} SET status = %s WHERE id = %s"
        self.cursor.execute(sql, (status, house_id))
        self.db.commit()
        return True

    # 6️⃣ Supprimer une maison
    def delete_house(self, house_id):
        sql = f"DELETE FROM {self.table} WHERE id = %s"
        self.cursor.execute(sql, (house_id,))
        self.db.commit()
        return True

    # 7️⃣ Obtenir les statistiques globales
    def get_stats(self):
        stats = {}

        self.cursor.execute(f"SELECT COUNT(*) as total FROM {self.table}")
        stats["total"] = self.cursor.fetchone()["total"]

        self.cursor.execute(f"SELECT COUNT(*) as active FROM {self.table} WHERE status = 'active'")
        stats["active"] = self.cursor.fetchone()["active"]

        self.cursor.execute(f"SELECT COUNT(*) as desactive FROM {self.table} WHERE status = 'desactive'")
        stats["desactive"] = self.cursor.fetchone()["desactive"]

        stats["rate"] = round((stats["active"] / stats["total"]) * 100) if stats["total"] > 0 else 0

        return stats

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
