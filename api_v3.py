import mysql.connector
from flask import Flask, jsonify, request

app = Flask(__name__)


mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="ciel2027"
)
cursor = mydb.cursor()


#@app.route('/v3/login/', methods=['GET'])
def login():
    auth = request.authorization
    username = auth.username
    password = auth.password
    
    req = f"SELECT * FROM user WHERE login = '{username}' AND password = '{password}'"
    cursor.execute(req)
    data = cursor.fetchone()
    if data:
        #return jsonify("Accès autorisé", 200)
        return True
    else:
        #return jsonify("Accès refusé", 401)
        return False


@app.route('/v3/etudiants/', methods=['GET'])
def getEtudiants():
    if login() :
        etudiants = []
        req = "SELECT * FROM etudiant"
        cursor.execute(req)
        result = cursor.fetchall()
        for row in result:
            etudiant = {
                "idetudiant": row[0],
                "nom": row[1],
                "prenom": row[2],
                "email": row[3],
                "telephone": row[4],
            }
            etudiants.append(etudiant)
        return jsonify(etudiants), 200
    else:
        return jsonify("Accès refusé", 401)


@app.route('/v3/etudiants/<int:id>', methods=['GET'])
def getEtudiant(id):
    if login() :
        req = f"SELECT * FROM etudiant WHERE idetudiant = {id}"
        print (req)
        try :
            cursor.execute(req)
            row = cursor.fetchone()
            etudiant = {
                "idetudiant": row[0],
                "nom": row[1],
                "prenom": row[2],
                "email": row[3],
                "telephone": row[4]
            }
            return jsonify(etudiant), 200
        except TypeError :
            return jsonify({'erreur':'id invalide'}), 404
    else:
        return jsonify("Accès refusé", 401)


@app.route('/v3/etudiants/', methods=['POST'])
def addEtudiant():
    if login() :
        nom = request.json['nom']
        prenom = request.json['prenom']
        email = request.json['email']
        telephone = request.json['telephone']
        req = f"INSERT INTO etudiant (nom, prenom, email, telephone) \
            VALUES ('{nom}','{prenom}','{email}','{telephone}')"
        cursor.execute(req)
        mydb.commit()
        #return req
        return jsonify({'message':'Ajout OK'}), 201
    else:
        return jsonify("Accès refusé", 401)

@app.route('/v3/etudiants/<int:id>', methods=['PUT'])
def updateEtudiant(id):
    if login() :
        nom = request.json['nom']
        prenom = request.json['prenom']
        email = request.json['email']
        telephone = request.json['telephone']
        req = f"UPDATE etudiant \
            SET nom='{nom}', prenom='{prenom}', email='{email}', telephone='{telephone}' \
            WHERE idetudiant = {id}"
        cursor.execute(req)
        mydb.commit()
        #return req
        return jsonify({'message': 'Modification OK'}), 200
    else:
        return jsonify("Accès refusé", 401)

@app.route('/v3/etudiants/<int:id>', methods=['DELETE'])
def deleteEtudiant(id):
    if login() :
        req = f"DELETE FROM etudiant WHERE idetudiant = {id}"
        print(req)
        cursor.execute(req)
        mydb.commit()
        #return req
        return jsonify({'message': 'Il a disparu mdr !!!'}), 200
    else:
        return jsonify("Accès refusé", 401)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000, debug=True)