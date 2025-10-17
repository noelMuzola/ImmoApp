# Agent.py
import mysql.connector

class Agent:
    def __init__(self, db_config):
        self.db = mysql.connector.connect(**db_config)
        self.cursor = self.db.cursor(dictionary=True)
        self.table = "agent"

    # 1️⃣ Récupérer tous les agents
    def get_all_agents(self, filters=None):
        if filters is None:
            filters = {}

        sql = f"SELECT * FROM {self.table} WHERE 1=1"
        params = []

        if 'status' in filters and filters['status'] != 'all':
            sql += " AND status = %s"
            params.append(filters['status'])

        if 'grade' in filters and filters['grade'] != 'all':
            sql += " AND agentGrade = %s"
            params.append(filters['grade'])

        if 'district' in filters and filters['district'] != 'all':
            sql += " AND agentDistrict = %s"
            params.append(filters['district'])

        if 'search' in filters and filters['search']:
            sql += " AND (agentName LIKE %s OR agentEmail LIKE %s OR agentMatricule LIKE %s)"
            search_term = f"%{filters['search']}%"
            params.extend([search_term, search_term, search_term])

        sql += " ORDER BY agentName ASC"
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    # 2️⃣ Récupérer un agent par ID
    def get_agent_by_id(self, agent_id):
        sql = f"SELECT * FROM {self.table} WHERE id = %s"
        self.cursor.execute(sql, (agent_id,))
        return self.cursor.fetchone()

    # 3️⃣ Ajouter un nouvel agent
    def add_agent(self, data):
        sql = f"""
        INSERT INTO {self.table} 
        (agentName, agentEmail, agentMatricule, agentGrade, agentDistrict, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("agentName"),
            data.get("agentEmail"),
            data.get("agentMatricule"),
            data.get("agentGrade"),
            data.get("agentDistrict"),
            data.get("status", "active")
        )
        self.cursor.execute(sql, values)
        self.db.commit()
        return self.cursor.lastrowid

    # 4️⃣ Modifier un agent
    def update_agent(self, agent_id, data):
        sql = f"""
        UPDATE {self.table} SET
            agentName = %s,
            agentEmail = %s,
            agentMatricule = %s,
            agentGrade = %s,
            agentDistrict = %s,
            status = %s
        WHERE id = %s
        """
        values = (
            data.get("agentName"),
            data.get("agentEmail"),
            data.get("agentMatricule"),
            data.get("agentGrade"),
            data.get("agentDistrict"),
            data.get("status"),
            agent_id
        )
        self.cursor.execute(sql, values)
        self.db.commit()
        return True

    # 5️⃣ Changer le statut
    def toggle_agent_status(self, agent_id, status):
        sql = f"UPDATE {self.table} SET status = %s WHERE id = %s"
        self.cursor.execute(sql, (status, agent_id))
        self.db.commit()
        return True

    # 6️⃣ Supprimer un agent
    def delete_agent(self, agent_id):
        sql = f"DELETE FROM {self.table} WHERE id = %s"
        self.cursor.execute(sql, (agent_id,))
        self.db.commit()
        return True

    # 7️⃣ Obtenir les statistiques
    def get_stats(self):
        stats = {}

        self.cursor.execute(f"SELECT COUNT(*) as total FROM {self.table}")
        stats["total"] = self.cursor.fetchone()["total"]

        self.cursor.execute(f"SELECT COUNT(*) as active FROM {self.table} WHERE status = 'active'")
        stats["active"] = self.cursor.fetchone()["active"]

        self.cursor.execute(f"SELECT COUNT(*) as inactive FROM {self.table} WHERE status = 'inactive'")
        stats["inactive"] = self.cursor.fetchone()["inactive"]

        stats["activity_rate"] = round((stats["active"] / stats["total"]) * 100) if stats["total"] > 0 else 0

        return stats

    # 8️⃣ Vérifier doublon matricule
    def matricule_exists(self, matricule, exclude_id=None):
        sql = f"SELECT COUNT(*) as count FROM {self.table} WHERE agentMatricule = %s"
        params = [matricule]
        if exclude_id:
            sql += " AND id != %s"
            params.append(exclude_id)

        self.cursor.execute(sql, tuple(params))
        return self.cursor.fetchone()["count"] > 0

    # 9️⃣ Vérifier doublon email
    def email_exists(self, email, exclude_id=None):
        sql = f"SELECT COUNT(*) as count FROM {self.table} WHERE agentEmail = %s"
        params = [email]
        if exclude_id:
            sql += " AND id != %s"
            params.append(exclude_id)

        self.cursor.execute(sql, tuple(params))
        return self.cursor.fetchone()["count"] > 0


