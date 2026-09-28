from flask import Flask, jsonify, request
from db import Database

app = Flask(__name__)

#db = Database("192.168.1.xxx", "extern_user", "Bt5@c13l972", "ciel2027")
db = Database("127.0.0.1", "root", "", "ciel2027")
    
@app.route('/v4/etudiants/', methods=['GET'])
def getEtudiants():
    code = db.login(request)
    if code == 500:
        return jsonify({'message': 'Echec de connexion à la base de données'}), 500
    if code == 401:
        return jsonify({'message': 'Accès non autorisé'}), 401
        
    etudiants = []
    data = db.readAll()
    if data == 401:
        return jsonify("Requête invalide"), 400
    if data == 400:
        return jsonify("Requête invalide"), 400
    for row in data:
        etudiant = {
            "idetudiant": row[0],
            "nom": row[1],
            "prenom": row[2],
            "email": row[3],
            "telephone": row[4]
            }
        etudiants.append(etudiant)
    return jsonify(etudiants), 200

@app.route('/v4/etudiants/<int:id>', methods=['GET'])
def getEtudiant(id):
    code = db.login(request)
    if code == 500:
        return jsonify({'message': 'Echec de connexion à la base de données'}), 500
    if code == 401:
        return jsonify({'message': 'Accès non autorisé'}), 401
    
    data = db.readOne(id)
    if data == 400:
        return jsonify("Requête invalide"), 400
    if data != 404:
        etudiant = {
            "idetudiant": data[0],
            "nom": data[1],
            "prenom": data[2],
            "email": data[3],
            "telephone": data[4]
        }
        return jsonify(etudiant), 200
    else: 
        return jsonify("id invalide"), 404
    
@app.route('/v4/etudiants/', methods=['POST'])
def addEtudiant():
    code = db.login(request)
    if code == 500:
        return jsonify({'message': 'Echec de connexion à la base de données'}), 500
    if code == 401:
        return jsonify({'message': 'Accès non autorisé'}), 401

    res = db.create(request)

    if res == 201:
        return jsonify({'message': 'Ajout OK'}), 201
    else:
        return jsonify("Requête invalide"), 400
    
@app.route('/v4/etudiants/<int:id>', methods=['PUT'])
def updateEtudiant(id):
    code = db.login(request)
    if code == 500:
        return jsonify({'message': 'Echec de connexion à la base de données'}), 500
    if code == 401:
        return jsonify({'message': 'Accès non autorisé'}), 401

    res = db.update(id, request)
    if res == 200:
        return jsonify({'message': 'Modification OK'}), 200
    else:
        return jsonify("Requête invalide"), 400


@app.route('/v4/etudiants/<int:id>', methods=['DELETE'])
def deleteEtudiant(id):
    code = db.login(request)
    if code == 500:
        return jsonify({'message': 'Echec de connexion à la base de données'}), 500
    if code == 401:
        return jsonify({'message': 'Accès non autorisé'}), 401

    res = db.delete(id)
    if res == 200:
        # CORRECTION : Retour du message d'origine attendu par vos tests Postman
        return jsonify({'message': 'Il a disparu mdr !!!'}), 200
    else:
        return jsonify("Requête invalide"), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000, debug=True)
