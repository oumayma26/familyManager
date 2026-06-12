import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path="family_tree.db"):
        self.db_path = db_path
        self.conn = None
        self.create_tables()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        # Table des personnes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cin TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birth_date TEXT,
                death_date TEXT,
                gender TEXT CHECK(gender IN ('M', 'F')),
                is_martyr INTEGER DEFAULT 1,
                is_martyr_family INTEGER DEFAULT 0,
                notes TEXT,
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des relations familiales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person1_id INTEGER NOT NULL,
                person2_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL CHECK(relation_type IN (
                    'parent', 'child', 'spouse', 'sibling'
                )),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person1_id) REFERENCES persons(id),
                FOREIGN KEY (person2_id) REFERENCES persons(id),
                UNIQUE(person1_id, person2_id, relation_type)
            )
        """)

        # Table de configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Insérer le SMIG par défaut si pas encore présent
        cursor.execute("""
            INSERT OR IGNORE INTO config (key, value) 
            VALUES ('smig', '460')
        """)

        # Configuration des pensions (dans la table config existante)
        pension_defaults = [
            ('pension_conjoint', '60'),
            ('pension_enfant', '30'),
            ('pension_parent', '40'),
            ('pension_orphelin', '50')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO config (key, value) 
            VALUES (?, ?)
        """, pension_defaults)

        # Table des pensions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pensions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                martyr_id INTEGER NOT NULL,
                membre_id INTEGER NOT NULL,
                type_pension TEXT NOT NULL CHECK(type_pension IN (
                    'conjoint', 'enfant', 'parent', 'orphelin'
                )),
                montant_mensuel REAL NOT NULL,
                date_debut TEXT,
                statut TEXT DEFAULT 'actif' CHECK(statut IN ('actif', 'suspendu')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (martyr_id) REFERENCES persons(id),
                FOREIGN KEY (membre_id) REFERENCES persons(id)
            )
        """)

        # Table des paiements (historique)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paiements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pension_id INTEGER NOT NULL,
                mois_annee TEXT NOT NULL,
                montant_paye REAL NOT NULL,
                date_paiement TEXT,
                mode_paiement TEXT CHECK(mode_paiement IN ('virement', 'especes', 'cheque')),
                statut TEXT DEFAULT 'paye' CHECK(statut IN ('paye', 'en_attente', 'retard')),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pension_id) REFERENCES pensions(id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Base de données créée avec succès !")
    
    # ========== CRUD PERSONS ==========
    
    def add_person(self, first_name, last_name, cin=None, birth_date=None, 
                   death_date=None, gender=None, is_martyr=1, is_martyr_family=0,
                   notes=None, photo_path=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO persons (cin, first_name, last_name, birth_date, death_date, 
                               gender, is_martyr, is_martyr_family, notes, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cin, first_name, last_name, birth_date, death_date, 
              gender, is_martyr, is_martyr_family, notes, photo_path))
        person_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return person_id
    
    def get_person(self, person_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM persons WHERE id = ?", (person_id,))
        person = cursor.fetchone()
        conn.close()
        return dict(person) if person else None
    
    def get_all_persons(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM persons ORDER BY last_name, first_name")
        persons = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return persons
    
    def update_person(self, person_id, **kwargs):
        allowed_fields = ['cin','first_name', 'last_name', 'birth_date', 
                         'death_date', 'gender', 'notes', 'photo_path', 'is_martyr', 'is_martyr_family']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [person_id]
        
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE persons SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
        return True
    
    def delete_person(self, person_id):
        conn = self.connect()
        cursor = conn.cursor()
        # Supprimer d'abord les relations
        cursor.execute("DELETE FROM relationships WHERE person1_id = ? OR person2_id = ?", 
                      (person_id, person_id))
        # Puis la personne
        cursor.execute("DELETE FROM persons WHERE id = ?", (person_id,))
        conn.commit()
        conn.close()
    
    # ========== RELATIONSHIPS ==========
    
    def add_relationship(self, person1_id, person2_id, relation_type):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO relationships (person1_id, person2_id, relation_type)
            VALUES (?, ?, ?)
        """, (person1_id, person2_id, relation_type))
        conn.commit()
        conn.close()
    
    def get_relationships(self, person_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, 
                   p1.first_name as p1_first, p1.last_name as p1_last,
                   p2.first_name as p2_first, p2.last_name as p2_last
            FROM relationships r
            JOIN persons p1 ON r.person1_id = p1.id
            JOIN persons p2 ON r.person2_id = p2.id
            WHERE r.person1_id = ? OR r.person2_id = ?
        """, (person_id, person_id))
        relations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return relations
    
    def get_martyrs(self):
        """Récupère uniquement les martyrs"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM persons WHERE is_martyr = 1 ORDER BY last_name, first_name")
        persons = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return persons
    
    def get_martyr_families(self):
        """Récupère uniquement les familles de martyrs"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM persons WHERE is_martyr_family = 1 ORDER BY last_name, first_name")
        persons = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return persons
    
    def get_family_members(self, person_id):
        """Récupère tous les membres de la famille d'une personne"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Trouver toutes les personnes connectées par relation
        cursor.execute("""
            SELECT DISTINCT p.* FROM persons p
            WHERE p.id = ?
            OR p.id IN (
                SELECT person1_id FROM relationships WHERE person2_id = ?
                UNION
                SELECT person2_id FROM relationships WHERE person1_id = ?
            )
        """, (person_id, person_id, person_id))
        
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return members

    def get_stats(self):
        """Récupère les statistiques globales"""
        conn = self.connect()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total martyrs
        cursor.execute("SELECT COUNT(*) FROM persons WHERE is_martyr = 1")
        stats['total_martyrs'] = cursor.fetchone()[0]
        
        # Total familles
        cursor.execute("SELECT COUNT(*) FROM persons WHERE is_martyr_family = 1")
        stats['total_families'] = cursor.fetchone()[0]
        
        # Total personnes
        cursor.execute("SELECT COUNT(*) FROM persons")
        stats['total_persons'] = cursor.fetchone()[0]
        
        # Répartition par genre
        cursor.execute("SELECT gender, COUNT(*) FROM persons GROUP BY gender")
        stats['gender_distribution'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Martyrs sans famille (pas de relations)
        cursor.execute("""
            SELECT COUNT(*) FROM persons p
            WHERE p.is_martyr = 1
            AND p.id NOT IN (
                SELECT person1_id FROM relationships
                UNION
                SELECT person2_id FROM relationships
            )
        """)
        stats['martyrs_without_family'] = cursor.fetchone()[0]
        
        # Personnes sans CIN
        cursor.execute("SELECT COUNT(*) FROM persons WHERE cin IS NULL OR cin = ''")
        stats['without_cin'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    # ========== PENSIONS ==========
    
    def add_pension(self, martyr_id, membre_id, type_pension, date_debut=None):
        montant = self.calculer_pension(type_pension)
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pensions (martyr_id, membre_id, type_pension, 
                                montant_mensuel, date_debut)
            VALUES (?, ?, ?, ?, ?)
        """, (martyr_id, membre_id, type_pension, montant, date_debut))
        pension_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pension_id
    
    def get_pensions_by_martyr(self, martyr_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, 
                   m.first_name, m.last_name,
                   m.gender, m.birth_date
            FROM pensions p
            JOIN persons m ON p.membre_id = m.id
            WHERE p.martyr_id = ?
            ORDER BY p.type_pension, m.last_name
        """, (martyr_id,))
        pensions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return pensions
    
    def get_total_pensions_martyr(self, martyr_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(montant_mensuel) FROM pensions 
            WHERE martyr_id = ? AND statut = 'actif'
        """, (martyr_id,))
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total
    
    def get_stats_pensions(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        # Total pensions actives
        cursor.execute("""
            SELECT COUNT(*), SUM(montant_mensuel) 
            FROM pensions WHERE statut = 'actif'
        """)
        count, total = cursor.fetchone()
        
        # Par type
        cursor.execute("""
            SELECT type_pension, COUNT(*), SUM(montant_mensuel)
            FROM pensions WHERE statut = 'actif'
            GROUP BY type_pension
        """)
        by_type = {row[0]: {'count': row[1], 'total': row[2]} for row in cursor.fetchall()}
        
        conn.close()
        return {
            'total_pensions': count or 0,
            'montant_total': total or 0,
            'par_type': by_type
        }

    # ========== CONFIG ==========

    def get_config(self, key, default=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    
    def set_config(self, key, value):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)
        """, (key, value))
        conn.commit()
        conn.close()
    
    def get_smig(self):
        return float(self.get_config('smig', '460'))
    
    def set_smig(self, valeur):
        self.set_config('smig', str(valeur))
    
    def get_pension_pourcentage(self, type_pension):
        """Récupère le pourcentage d'une pension depuis config"""
        key = f'pension_{type_pension}'
        return int(self.get_config(key, '0'))
    
    def set_pension_pourcentage(self, type_pension, pourcentage):
        """Modifie le pourcentage d'une pension dans config"""
        key = f'pension_{type_pension}'
        self.set_config(key, str(pourcentage))
    
    def get_all_pension_pourcentages(self):
        """Récupère tous les pourcentages"""
        return {
            'conjoint': self.get_pension_pourcentage('conjoint'),
            'enfant': self.get_pension_pourcentage('enfant'),
            'parent': self.get_pension_pourcentage('parent'),
            'orphelin': self.get_pension_pourcentage('orphelin')
        }
    
    def calculer_pension(self, type_pension):
        """Calcule le montant d'une pension selon SMIG et pourcentage"""
        smig = self.get_smig()
        pourcentage = self.get_pension_pourcentage(type_pension)
        return smig * (pourcentage / 100)
    

    # ========== PAIEMENTS ==========
    
    def add_paiement(self, pension_id, mois_annee, montant_paye, 
                     date_paiement=None, mode_paiement='virement', notes=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO paiements (pension_id, mois_annee, montant_paye, 
                                 date_paiement, mode_paiement, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pension_id, mois_annee, montant_paye, date_paiement, mode_paiement, notes))
        paiement_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return paiement_id
    
    def get_paiements_by_pension(self, pension_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM paiements 
            WHERE pension_id = ? 
            ORDER BY mois_annee DESC
        """, (pension_id,))
        paiements = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return paiements
    
    def get_paiements_by_martyr(self, martyr_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pa.*, p.type_pension, m.first_name, m.last_name
            FROM paiements pa
            JOIN pensions p ON pa.pension_id = p.id
            JOIN persons m ON p.membre_id = m.id
            WHERE p.martyr_id = ?
            ORDER BY pa.mois_annee DESC
        """, (martyr_id,))
        paiements = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return paiements
    
    def get_alertes(self):
        """Récupère les alertes : pensions en retard, enfants majeurs, etc."""
        conn = self.connect()
        cursor = conn.cursor()
        alertes = []
        
        # 1. Pensions sans paiement depuis 2 mois
        from datetime import datetime, timedelta
        deux_mois = (datetime.now() - timedelta(days=60)).strftime("%Y-%m")
        
        cursor.execute("""
            SELECT p.id, p.martyr_id, p.membre_id, p.type_pension,
                   m.first_name, m.last_name,
                   ma.first_name as martyr_first, ma.last_name as martyr_last
            FROM pensions p
            JOIN persons m ON p.membre_id = m.id
            JOIN persons ma ON p.martyr_id = ma.id
            WHERE p.statut = 'actif'
            AND p.id NOT IN (
                SELECT pension_id FROM paiements 
                WHERE mois_annee >= ?
            )
        """, (deux_mois,))
        
        for row in cursor.fetchall():
            alertes.append({
                'type': 'retard_paiement',
                'message': "Pension non payée depuis 2 mois pour {row['first_name']} {row['last_name']} (famille de {row['martyr_first']} {row['martyr_last']})",
                'niveau': 'urgent'
            })
        
        # 2. Enfants qui atteignent 18 ans cette année
        from datetime import datetime
        annee = datetime.now().year
        
        cursor.execute("""
            SELECT p.id, p.membre_id, m.first_name, m.last_name, m.birth_date,
                   ma.first_name as martyr_first, ma.last_name as martyr_last
            FROM pensions p
            JOIN persons m ON p.membre_id = m.id
            JOIN persons ma ON p.martyr_id = ma.id
            WHERE p.type_pension = 'enfant'
            AND p.statut = 'actif'
            AND m.birth_date LIKE ?
        """, (f"%{annee - 18}",))
        
        for row in cursor.fetchall():
            alertes.append({
                'type': 'majoration',
                'message': f"{row['first_name']} {row['last_name']} atteint 18 ans cette année (famille de {row['martyr_first']} {row['martyr_last']})",
                'niveau': 'attention'
            })
        
        # 3. Martyrs sans famille (pas de relations)
        cursor.execute("""
            SELECT p.id, p.first_name, p.last_name
            FROM persons p
            WHERE p.is_martyr = 1
            AND p.id NOT IN (
                SELECT person1_id FROM relationships
                UNION
                SELECT person2_id FROM relationships
            )
        """)
        
        for row in cursor.fetchall():
            alertes.append({
                'type': 'sans_famille',
                'message': f"{row['first_name']} {row['last_name']} n'a aucune famille enregistrée",
                'niveau': 'info'
            })
        
        conn.close()
        return alertes