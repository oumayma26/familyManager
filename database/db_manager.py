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
                marital_status TEXT DEFAULT 'celibataire' CHECK(marital_status IN ('marie', 'celibataire')),
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
            ('pension_conjoint', '40'),
            ('pension_enfant', '40'),
            ('pension_parent', '20'),
            ('pension_orphelin', '40')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO config (key, value) 
            VALUES (?, ?)
        """, pension_defaults)

        # Table des paiements de pensions mensuels
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pension_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                martyr_id INTEGER NOT NULL,
                beneficiary_id INTEGER NOT NULL,
                beneficiary_type TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_month INTEGER NOT NULL,
                payment_year INTEGER NOT NULL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (martyr_id) REFERENCES persons(id),
                FOREIGN KEY (beneficiary_id) REFERENCES persons(id),
                UNIQUE(martyr_id, beneficiary_id, payment_month, payment_year)
            )
        """)

        
        conn.commit()
        conn.close()
        print("✅ Base de données créée avec succès !")
    
    # ========== CRUD PERSONS ==========
    
    def add_person(self, first_name, last_name, cin=None, birth_date=None, 
                   death_date=None, gender=None, is_martyr=1, is_martyr_family=0,
                   notes=None, photo_path=None, marital_status='celibataire'):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO persons (cin, first_name, last_name, birth_date, death_date, 
                               gender, is_martyr, is_martyr_family, notes, photo_path, marital_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cin, first_name, last_name, birth_date, death_date, 
              gender, is_martyr, is_martyr_family, notes, photo_path, marital_status))
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
                         'death_date', 'gender', 'notes', 'photo_path', 'is_martyr', 'is_martyr_family', 'marital_status']
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
        
        # Supprimer la photo
        cursor.execute("SELECT photo_path FROM persons WHERE id = ?", (person_id,))
        row = cursor.fetchone()
        if row and row['photo_path']:
            import os
            try:
                os.remove(row['photo_path'])
            except Exception as e:
                print(f"Erreur suppression photo: {e}")
        
        # Supprimer les relations
        cursor.execute("DELETE FROM relationships WHERE person1_id = ? OR person2_id = ?", 
                    (person_id, person_id))
        
        # Supprimer la personne
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

    # ========== PENSION PAYMENTS ==========

    def get_martyr_family_for_pension(self, martyr_id):
        """Récupère les membres de famille vivants d'un martyr pour calcul des pensions"""
        conn = self.connect()
        cursor = conn.cursor()

        # Récupérer le martyr
        cursor.execute("SELECT * FROM persons WHERE id = ? AND is_martyr = 1", (martyr_id,))
        martyr = cursor.fetchone()
        if not martyr:
            conn.close()
            return None

        martyr = dict(martyr)

        # Récupérer toutes les relations
        cursor.execute("""
            SELECT r.*, p.* FROM relationships r
            JOIN persons p ON (r.person1_id = p.id OR r.person2_id = p.id)
            WHERE (r.person1_id = ? OR r.person2_id = ?)
            AND p.id != ?
            AND (p.death_date IS NULL OR p.death_date = '')
        """, (martyr_id, martyr_id, martyr_id))

        relations = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Organiser par type de relation
        family = {
            'martyr': martyr,
            'parents': [],
            'spouses': [],
            'children': [],
            'siblings': []
        }

        for rel in relations:
            if rel['person1_id'] == martyr_id:
                other_id = rel['person2_id']
            else:
                other_id = rel['person1_id']

            # Récupérer la personne complète
            person = self.get_person(other_id)
            if person and (not person.get('death_date') or not person['death_date'].strip()):
                rel_type = rel['relation_type']
                if rel_type == 'parent':
                    family['parents'].append(person)
                elif rel_type == 'spouse':
                    family['spouses'].append(person)
                elif rel_type == 'child':
                    family['children'].append(person)
                elif rel_type == 'sibling':
                    family['siblings'].append(person)

        return family

    def calculate_pensions(self, martyr_id):
        """Calcule les pensions pour un martyr selon les règles"""
        family = self.get_martyr_family_for_pension(martyr_id)
        if not family:
            return []

        martyr = family['martyr']
        smig = self.get_smig()
        total_pension = smig * 3

        pensions = []

        marital_status = martyr.get('marital_status', 'celibataire')

        if marital_status == 'celibataire':
            # Martyr célibataire
            parents = family['parents']
            siblings = family['siblings']

            if parents:
                # Parents vivants → 100% aux parents
                num_parents = len(parents)
                if num_parents == 1:
                    # Un seul parent vivant → 100%
                    parent = parents[0]
                    pensions.append({
                        'beneficiary_id': parent['id'],
                        'beneficiary_name': f"{parent['first_name']} {parent['last_name']}",
                        'beneficiary_type': 'parent',
                        'amount': total_pension,
                        'percentage': 100
                    })
                else:
                    # Deux parents vivants → 50% chacun
                    for parent in parents:
                        pensions.append({
                            'beneficiary_id': parent['id'],
                            'beneficiary_name': f"{parent['first_name']} {parent['last_name']}",
                            'beneficiary_type': 'parent',
                            'amount': total_pension / 2,
                            'percentage': 50
                        })
            elif siblings:
                # Parents morts → frères/sœurs se partagent
                num_siblings = len(siblings)
                for sibling in siblings:
                    pensions.append({
                        'beneficiary_id': sibling['id'],
                        'beneficiary_name': f"{sibling['first_name']} {sibling['last_name']}",
                        'beneficiary_type': 'sibling',
                        'amount': total_pension / num_siblings,
                        'percentage': round(100 / num_siblings, 2)
                    })

        else:  # marié
            # Martyr marié
            parents = family['parents']
            spouses = family['spouses']
            children = family['children']

            # Parents : 20%
            if parents:
                parent_share = total_pension * 0.20
                num_parents = len(parents)
                for parent in parents:
                    pensions.append({
                        'beneficiary_id': parent['id'],
                        'beneficiary_name': f"{parent['first_name']} {parent['last_name']}",
                        'beneficiary_type': 'parent',
                        'amount': parent_share / num_parents,
                        'percentage': round(20 / num_parents, 2)
                    })

            # Conjoint(e) : 40%
            if spouses:
                spouse_share = total_pension * 0.40
                num_spouses = len(spouses)
                for spouse in spouses:
                    pensions.append({
                        'beneficiary_id': spouse['id'],
                        'beneficiary_name': f"{spouse['first_name']} {spouse['last_name']}",
                        'beneficiary_type': 'spouse',
                        'amount': spouse_share / num_spouses,
                        'percentage': round(40 / num_spouses, 2)
                    })

            # Enfants : 40%
            if children:
                children_share = total_pension * 0.40
                num_children = len(children)
                for child in children:
                    pensions.append({
                        'beneficiary_id': child['id'],
                        'beneficiary_name': f"{child['first_name']} {child['last_name']}",
                        'beneficiary_type': 'child',
                        'amount': children_share / num_children,
                        'percentage': round(40 / num_children, 2)
                    })

        return pensions

    def pay_pensions(self, month, year):
        """Paie les pensions pour tous les martyrs pour un mois donné"""
        conn = self.connect()
        cursor = conn.cursor()

        results = {
            'paid': [],
            'skipped': [],
            'errors': []
        }

        martyrs = self.get_martyrs()

        for martyr in martyrs:
            martyr_id = martyr['id']
            pensions = self.calculate_pensions(martyr_id)

            if not pensions:
                results['skipped'].append({
                    'martyr_id': martyr_id,
                    'martyr_name': f"{martyr['first_name']} {martyr['last_name']}",
                    'reason': 'Aucun bénéficiaire vivant'
                })
                continue

            for pension in pensions:
                beneficiary_id = pension['beneficiary_id']

                # Vérifier si déjà payé ce mois
                cursor.execute("""
                    SELECT id FROM pension_payments 
                    WHERE martyr_id = ? AND beneficiary_id = ? 
                    AND payment_month = ? AND payment_year = ?
                """, (martyr_id, beneficiary_id, month, year))

                if cursor.fetchone():
                    results['skipped'].append({
                        'martyr_id': martyr_id,
                        'martyr_name': f"{martyr['first_name']} {martyr['last_name']}",
                        'beneficiary': pension['beneficiary_name'],
                        'reason': 'Déjà payé ce mois'
                    })
                    continue

                try:
                    cursor.execute("""
                        INSERT INTO pension_payments 
                        (martyr_id, beneficiary_id, beneficiary_type, amount, payment_month, payment_year)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (martyr_id, beneficiary_id, pension['beneficiary_type'], 
                          pension['amount'], month, year))

                    results['paid'].append({
                        'martyr_id': martyr_id,
                        'martyr_name': f"{martyr['first_name']} {martyr['last_name']}",
                        'beneficiary': pension['beneficiary_name'],
                        'type': pension['beneficiary_type'],
                        'amount': pension['amount'],
                        'percentage': pension['percentage']
                    })
                except Exception as e:
                    results['errors'].append({
                        'martyr_id': martyr_id,
                        'error': str(e)
                    })

        conn.commit()
        conn.close()
        return results

    def get_pension_history(self, martyr_id=None, month=None, year=None):
        """Récupère l'historique des paiements de pensions"""
        conn = self.connect()
        cursor = conn.cursor()

        query = """
            SELECT pp.*, 
                   m.first_name as martyr_first, m.last_name as martyr_last,
                   b.first_name as ben_first, b.last_name as ben_last
            FROM pension_payments pp
            JOIN persons m ON pp.martyr_id = m.id
            JOIN persons b ON pp.beneficiary_id = b.id
            WHERE 1=1
        """
        params = []

        if martyr_id:
            query += " AND pp.martyr_id = ?"
            params.append(martyr_id)
        if month:
            query += " AND pp.payment_month = ?"
            params.append(month)
        if year:
            query += " AND pp.payment_year = ?"
            params.append(year)

        query += " ORDER BY pp.payment_year DESC, pp.payment_month DESC, pp.payment_date DESC"

        cursor.execute(query, params)
        payments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return payments

    def get_total_pensions_paid(self, month=None, year=None):
        """Calcule le total des pensions payées"""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT SUM(amount) as total FROM pension_payments WHERE 1=1"
        params = []

        if month:
            query += " AND payment_month = ?"
            params.append(month)
        if year:
            query += " AND payment_year = ?"
            params.append(year)

        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else 0