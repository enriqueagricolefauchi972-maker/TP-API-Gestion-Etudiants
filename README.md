<p align="center">
  <img src="images/logo.png" alt="Lycée Joseph Gaillard" width="220">
</p>

<h1 align="center">Rapport de TP : API REST</h1>
<h3 align="center">API REST de gestion des étudiants</h3>

**Enrique Agricole Fauchi**
BTS CIEL (Cybersécurité, Informatique et Réseau)

## Sommaire

1. [Introduction](#1-introduction)
2. [API v1](#2-api-v1)
3. [API v2](#3-api-v2)
4. [API v3](#4-api-v3)
5. [API v4](#5-api-v4)
6. [Le fichier db.py](#6-le-fichier-dbpy)
7. [Comparaison des versions](#7-comparaison-des-versions)
8. [Difficultés et améliorations possibles](#8-difficultés-et-améliorations-possibles)
9. [Conclusion](#9-conclusion)
10. [Annexes : diagrammes](#10-annexes--diagrammes)

**Fichiers du projet :** [`api_v1.py`](api_v1.py) · [`api_v2.py`](api_v2.py) · [`api_v3.py`](api_v3.py) · [`api_v4.py`](api_v4.py) · [`db.py`](db.py) · [`ciel2027.sql`](ciel2027.sql)

---

## 1. Introduction

Dans ce TP, j'ai créé une API REST avec Python et Flask. Elle permet de gérer une liste d'étudiants stockée dans une base de données MySQL nommée `ciel2027`. On peut afficher tous les étudiants, en afficher un seul, en ajouter, les modifier et les supprimer.

J'ai fait quatre versions, chacune améliorant la précédente :

- **v1** : l'API de base, sans gestion d'erreurs.
- **v2** : ajout d'une gestion d'erreur quand l'id n'existe pas.
- **v3** : ajout d'une authentification par login et mot de passe.
- **v4** : le code qui parle à la base de données est séparé dans un fichier `db.py`, et les erreurs sont mieux gérées.

Pour tester, j'ai utilisé Postman. Le professeur a aussi testé mes API avec Postman et tout fonctionne.

### Outils utilisés

- Python avec Flask (création de l'API)
- `mysql.connector` (connexion à MySQL)
- MySQL en local (`127.0.0.1`)
- Postman (tests des requêtes)

### La base de données

La base `ciel2027` contient deux tables que j'utilise :

| Table | Colonnes |
|---|---|
| `etudiant` | `idetudiant`, `nom`, `prenom`, `email`, `telephone` |
| `user` | `login`, `password` (sert à l'authentification à partir de la v3) |

### Les routes

Dans chaque version, on retrouve les mêmes 5 routes. Seule la partie de l'URL (`v1`, `v2`, `v3`, `v4`) change.

| Méthode | URL | Rôle |
|---|---|---|
| GET | `/{api_version}/etudiants/` | Récupérer tous les étudiants |
| GET | `/{api_version}/etudiants/<id>` | Récupérer un étudiant |
| POST | `/{api_version}/etudiants/` | Ajouter un étudiant (données en JSON) |
| PUT | `/{api_version}/etudiants/<id>` | Modifier un étudiant (données en JSON) |
| DELETE | `/{api_version}/etudiants/<id>` | Supprimer un étudiant |

---

## 2. API v1

La v1 est la version de départ. Au début du fichier, je me connecte à la base MySQL avec `mysql.connector` et ensuite, chaque route exécute une requête SQL et renvoie le résultat en JSON avec `jsonify`.

### Exemple : afficher tous les étudiants

```python
@app.route('/v1/etudiants/', methods=['GET'])
def getEtudiants():
    etudiants = []
    request = "SELECT * FROM etudiant"
    cursor.execute(request)
    result = cursor.fetchall()
    for row in result:
        etudiant = {"idetudiant": row[0], "nom": row[1], ...}
        etudiants.append(etudiant)
    return jsonify(etudiants), 201
```

Le curseur renvoie chaque ligne sous forme de liste. Je transforme donc chaque ligne en dictionnaire pour que `jsonify` puisse produire du JSON lisible avec les noms des champs.

### Ajout, modification, suppression

Pour POST et PUT, je récupère les champs `nom`, `prenom`, `email` et `telephone` dans le JSON envoyé (`request.json`), je construis la requête INSERT ou UPDATE, puis je fais `mydb.commit()` pour enregistrer. Pour DELETE, j'exécute un DELETE avec l'id donné dans l'URL.

### Limites de la v1

- Si on demande un id qui n'existe pas, `row` vaut `None` et le programme plante (erreur 500).
- Le GET de tous les étudiants renvoie le code 201 (Created) alors qu'un 200 serait plus logique, car on ne crée rien.

### Tests Postman

**GET `/v1/etudiants/`** : liste des étudiants

![GET v1 etudiants](images/v1_get_etudiants.png)

**POST `/v1/etudiants/`** : ajout d'un étudiant

![POST v1 etudiants](images/v1_post_etudiant.png)

---

## 3. API v2

La v2 corrige le principal problème de la v1 : la gestion d'un id inexistant. Dans la route GET d'un étudiant, j'ai mis la lecture dans un bloc `try / except`.

```python
try :
    cursor.execute(req)
    row = cursor.fetchone()
    etudiant = {"idetudiant": row[0], "nom": row[1], ...}
    return jsonify(etudiant), 200
except TypeError :
    return jsonify({'erreur':'id invalide'}), 404
```

Quand l'id n'existe pas, `fetchone()` renvoie `None`. Essayer de faire `row[0]` sur `None` provoque une `TypeError`. Je l'attrape avec `except` et je renvoie un message clair avec le code 404 (Not Found) au lieu de faire planter l'API.

Les autres routes sont identiques à la v1.

### Test Postman

**GET `/v2/etudiants/<id>`** avec un id qui n'existe pas (404)

![GET v2 id invalide](images/v2_id_invalide_404.png)

---

## 4. API v3

La v3 ajoute la sécurité : il faut maintenant s'authentifier pour utiliser l'API. J'ai écrit une fonction `login()` qui utilise l'authentification de type Basic Auth (`request.authorization`). Elle lit le login et le mot de passe envoyés par Postman, puis cherche dans la table `user` si ce couple existe.

```python
def login():
    auth = request.authorization
    username = auth.username
    password = auth.password
    req = f"SELECT * FROM user WHERE login = '{username}' AND password = '{password}'"
    cursor.execute(req)
    data = cursor.fetchone()
    if data:
        return True
    else:
        return False
```

Au début de chaque route, je teste `if login() :`. Si c'est vrai, la route fait son travail normalement. Sinon, elle renvoie « Accès refusé ».

Dans Postman, il faut donc aller dans l'onglet Authorization, choisir Basic Auth et entrer un login et un mot de passe présents dans la table `user`.

### Limites de la v3

- Le code de login est copié dans chaque route : ça fait beaucoup de répétitions.
- Pour le refus d'accès, j'ai écrit `jsonify("Accès refusé", 401)`. En fait, le 401 est mis dans le JSON et non dans le vrai code HTTP de la réponse. Il aurait fallu écrire `jsonify("Accès refusé"), 401`. Cette erreur est corrigée en v4.
- Si on n'envoie aucun login, `auth` vaut `None` et l'API plante. C'est aussi corrigé en v4.

### Tests Postman

**Mauvais mot de passe** : l'accès est refusé.

![v3 accès refusé](images/v3_acces_refuse.png)

**Bon mot de passe** : l'API renvoie la liste des étudiants, donc l'accès est autorisé.

![v3 accès autorisé](images/v3_acces_autorise.png)

---

## 5. API v4

La v4 est la version la plus propre. J'ai déplacé tout le code qui utilise la base de données dans une classe `Database` (fichier `db.py`). Le fichier de l'API ne contient plus de SQL : il appelle seulement des fonctions comme `db.readAll()` ou `db.create(request)`.

```python
from db import Database
db = Database("127.0.0.1", "root", "", "ciel2027")
```

Chaque route commence par vérifier l'identité de l'utilisateur avec `db.login(request)`, qui renvoie un code :

| Code | Signification et réponse de l'API |
|---|---|
| 200 | Login correct, la route continue |
| 401 | Login ou mot de passe incorrect (ou absent) : « Accès non autorisé », code 401 |
| 500 | Impossible de se connecter à la base : « Echec de connexion à la base de données », code 500 |

Ensuite, la route appelle la fonction de `db.py` correspondante et traduit le résultat en réponse HTTP :

- `readOne` renvoie 404 si l'id n'existe pas, et l'API répond « id invalide » avec le code 404.
- Si une requête échoue (code 400), l'API répond « Requête invalide » avec le code 400.
- Un ajout réussi renvoie 201, une modification ou une suppression réussie renvoie 200.

Le GET de tous les étudiants renvoie maintenant bien le code 200 (et non plus 201 comme en v1 et v2).

### Tests Postman

**GET, POST, PUT et DELETE en v4 avec Basic Auth** : tous les tests passent.

![v4 tests OK](images/v4_tests_ok.png)

**Cas d'erreur en v4** (mauvais mot de passe : 401) : les tests échouent car l'accès est refusé, ce qui est le comportement attendu.

![v4 erreur 401](images/v4_erreur_401.png)

---

## 6. Le fichier db.py

Le fichier `db.py` contient la classe `Database`. Son but est de regrouper tout l'accès à la base de données au même endroit. Ainsi, le fichier de l'API reste court et lisible, et si on change de base de données, il n'y a qu'un seul fichier à modifier.

### Le constructeur et la connexion

Le constructeur `__init__` enregistre l'adresse du serveur, l'utilisateur, le mot de passe et le nom de la base. La méthode `connect()` utilise ces informations pour ouvrir une connexion et la renvoyer.

Contrairement aux versions 1 à 3, où la connexion est ouverte une seule fois au lancement, ici chaque méthode ouvre sa propre connexion puis la ferme à la fin. C'est plus propre et cela évite de garder une connexion ouverte inutilement.

### Les méthodes

| Méthode | Ce qu'elle fait | Valeurs renvoyées |
|---|---|---|
| `readAll()` | SELECT de tous les étudiants | La liste des lignes, ou 400 si erreur |
| `readOne(id)` | SELECT d'un étudiant par son id | La ligne, 404 si introuvable, 400 si erreur |
| `create(request)` | INSERT avec les données JSON | 201 si OK, 400 si erreur |
| `update(id, request)` | UPDATE avec les données JSON | 200 si OK, 400 si erreur |
| `delete(id)` | DELETE d'un étudiant | 200 si OK, 400 si erreur |
| `login(request)` | Vérifie le login/mot de passe dans la table `user` | 200, 401 ou 500 |

### Le try / except / finally

Chaque méthode suit la même structure :

```python
connector = self.connect()
cursor = connector.cursor()
try:
    ...  # la requête SQL
    return 200
except:
    return 400
finally:
    connector.close()
```

Le `try` exécute la requête. Si quelque chose ne va pas, le `except` renvoie un code d'erreur au lieu de faire planter le programme. Le `finally` est toujours exécuté, que ça ait marché ou non : il ferme la connexion.

### Détails importants

- Dans `create`, `update` et `delete`, il faut faire `connector.commit()` sinon les changements ne sont pas enregistrés dans la base. J'ai eu ce problème avec `delete` au début : la suppression ne se faisait pas tant que je n'avais pas ajouté le commit.
- Dans `login`, je fais d'abord `conn = None`. Si la connexion échoue, le `finally` ne cherche pas à fermer une connexion qui n'existe pas.

---

## 7. Comparaison des versions

| | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| **Base de données** | Connexion unique dans l'API | Connexion unique dans l'API | Connexion unique dans l'API | Classe `Database` (`db.py`) |
| **Authentification** | Non | Non | Oui (Basic Auth) | Oui (dans `db.py`) |
| **Id inexistant** | Plante | 404 | 404 | 404 |
| **Accès refusé** | - | - | 401 mal placé dans le JSON | Vrai code 401 |
| **Erreur base de données** | Non gérée | Non gérée | Non gérée | Codes 400 / 500 |
| **Code répété** | Beaucoup | Beaucoup | Encore plus | Peu (SQL dans `db.py`) |

On voit que chaque version apporte une amélioration : la v2 gère les erreurs d'id, la v3 protège l'accès, et la v4 organise le code proprement et gère mieux tous les cas d'erreur.

---

## 8. Difficultés et améliorations possibles

### Difficultés rencontrées

- Comprendre pourquoi le DELETE ne supprimait rien : il manquait le commit.
- Bien envoyer le JSON et l'authentification dans Postman (onglets Body en raw JSON et Authorization).
- Bien renvoyer le bon code HTTP, notamment pour le refus d'accès.

### Améliorations possibles

- **Sécurité :** mes requêtes SQL sont construites avec des f-strings, ce qui permet une injection SQL. Il faudrait utiliser des requêtes préparées, par exemple `cursor.execute("SELECT * FROM etudiant WHERE idetudiant = %s", (id,))`.
- Les mots de passe sont stockés en clair dans la table `user`. Il faudrait les hacher (par exemple avec bcrypt).
- Ne pas écrire les identifiants de la base directement dans le code, mais dans un fichier de configuration.
- Vérifier que les champs du JSON existent avant de les utiliser, et renvoyer un message précis en cas de champ manquant.
- Utiliser un décorateur Flask pour l'authentification, afin de ne pas répéter la vérification dans chaque route.

---

## 9. Conclusion

Ce TP m'a permis de comprendre comment fonctionne une API REST : les routes, les méthodes HTTP (GET, POST, PUT, DELETE), les codes de retour et l'échange de données en JSON. J'ai aussi appris à connecter une API à une base MySQL, à gérer les erreurs et à protéger l'accès avec une authentification.

La v4 est la plus aboutie, car le code est mieux organisé grâce à `db.py`. Je sais aussi que mon projet a des points à améliorer, surtout côté sécurité avec les requêtes préparées et le hachage des mots de passe.

Ça a été une bonne expérience. Ce TP m'a aussi permis d'avoir une bonne utilisation de l'IA comme assistant.

---

## 10. Annexes : diagrammes

### Diagramme de classe : la classe `Database`

La classe `Database` du fichier `db.py` contient les informations de connexion (`database`, `host`, `password`, `user`) et les méthodes qui permettent d'accéder à la base de données.

<p align="center">
  <img src="images/diagramme_classe_database.jpg" alt="Diagramme de classe Database" width="260">
</p>
<img width="299" height="285" alt="image" src="https://github.com/user-attachments/assets/4512104d-991c-4858-9bb5-e194916b816f" />

### Diagramme de cas d'utilisation

L'utilisateur peut faire cinq actions avec l'API : lister tous les étudiants, créer un étudiant, récupérer un étudiant par son id, mettre à jour un étudiant et supprimer un étudiant. Chacune de ces actions passe par la base de données.

![Diagramme de cas d'utilisation](images/diagramme_cas_utilisation.jpg)
<img width="785" height="607" alt="image" src="https://github.com/user-attachments/assets/5e88871c-3ac6-4110-ac16-9f70291e10d1" />

