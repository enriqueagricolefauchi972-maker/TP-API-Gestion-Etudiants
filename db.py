import mysql.connector
class Database:

    # Constructeur
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database 

    # Connexion à la base de données  
    def connect(self):
        connector = mysql.connector.connect(
            host = self.host, 
            user = self.user, 
            password = self.password, 
            database = self.database)
        return connector

    # Voir tous les étudiants 
    def readAll(self):
        connector = self.connect()
        cursor = connector.cursor()
        try:
            cursor.execute(f"SELECT * FROM etudiant")
            data = cursor.fetchall() 
            return data
        except:
            return 400
        finally:
            connector.close()

    # Voir un étudiant 
    def readOne(self, id):
        connector = self.connect()
        cursor = connector.cursor()
        try:
            cursor.execute(f"SELECT * FROM etudiant WHERE idEtudiant = {id}")
            data = cursor.fetchone() 
            if data:
                return data
            else:
                return 404
        except:
            return 400
        finally:
            connector.close()
        
    # Créer un nouvel étudiant 
    def create(self, request):
        connector = self.connect()
        cursor = connector.cursor()
        try:
            # Récupération des données envoyées en JSON
            nom = request.json['nom']
            prenom = request.json['prenom']
            email = request.json['email']
            telephone = request.json['telephone']
            
            # Exécution de l'insertion
            cursor.execute(f"INSERT INTO etudiant (nom, prenom, email, telephone) VALUES ('{nom}', '{prenom}', '{email}', '{telephone}')")
            connector.commit() # Important pour enregistrer les modifications
            return 201
        except:
            return 400
        finally:
            connector.close()

    # Modifier un étudiant 
    def update(self, id, request):
        connector = self.connect()
        cursor = connector.cursor()
        try:
            # Récupération des nouvelles données en JSON
            nom = request.json['nom']
            prenom = request.json['prenom']
            email = request.json['email']
            telephone = request.json['telephone']
            
            # Exécution de la mise à jour
            cursor.execute(f"UPDATE etudiant SET nom='{nom}', prenom='{prenom}', email='{email}', telephone='{telephone}' WHERE idEtudiant = {id}")
            connector.commit()
            return 200
        except:
            return 400
        finally:
            connector.close()
    
    # Supprimer un étudiant 
    def delete(self, id):
        connector = self.connect()
        cursor = connector.cursor()
        try:
            cursor.execute(f"DELETE FROM etudiant WHERE idEtudiant = {id}")
            connector.commit() # CORRECTION CRITIQUE : Ajout du commit indispensable pour valider la suppression dans la base de données
            return 200
        except:
            return 400
        finally:
            connector.close()

    # Vérifier que les login / password existent dans la table user
    def login(self, request):
        conn = None # CORRECTION : Initialisation pour éviter une erreur dans le bloc 'finally' si la connexion échoue au début
        try:
            auth = request.authorization
            username = auth.username
            password = auth.password
        except:
            return 401
        try:
            conn = self.connect()
            curs = conn.cursor()
        except:
            return 500        
        try:
            curs.execute(f"SELECT * FROM user WHERE login = '{username}' AND password = '{password}'")
            data = curs.fetchone() 
            if data:
                return 200
            else:
                return 401
        except:
            return(401)
        finally:
            if conn: # CORRECTION : Ferme la connexion uniquement si elle a réussi à s'ouvrir
                conn.close()
