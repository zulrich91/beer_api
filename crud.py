# Import flask
from typing import List
from flask import Flask, request
from flask import json
from flask.helpers import make_response, url_for
from flask.json import jsonify
from flask_mysqldb import MySQL
from werkzeug.exceptions import abort

app = Flask(__name__)

# configuration a la connection mysql
app.config['MYSQL_HOST'] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config['MYSQL_PASSWORD'] = "xxxxxxxx"
app.config['MYSQL_DB'] = "beer"

mysql = MySQL(app)

# route pour ajoute une biere dans ma bdd
@app.route('/articles', methods=['POST'])
def create_article():
    if not request.json and not "nom_article" in request.json:
        abort(404)
    try:
        # creer les champs de ma nouvelle tache
        nom_article = request.json.get('nom_article','')
        prix_achat = request.json.get("prix_achat",0)
        volume = request.json.get("prix_achat", 33)
        # creer ma connection et envoyer a ma bdd
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO article(id_article, nom_article, prix_achat, volume) VALUES(%s,%s, %s, %s)", (3923, nom_article, prix_achat,int(volume)))
        mysql.connection.commit()
        cur.close()
        return jsonify({'is':True})
    except Exception as e:
        print(e)
        return jsonify ({'is':False})

# route pour recuperer la liste des bierre de ma bdd
@app.route('/articles', methods=['GET'])
def get_articles():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM article")
        reponse = cur.fetchall()
        cur.close()
        bieres = []
        for biere in reponse:
            biere = make_article(biere)
            bieres.append(biere)
        return jsonify([make_public_article(biere) for biere in bieres])
    except Exception as e:
        print(e)
        abort(404)

# route pour recuperer un article de ma bdd
@app.route('/articles/<int:article_id>', methods=['GET'])
def get_article_by_id(article_id):
    print(article_id)
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM article WHERE id_article=%s", (str(article_id)))
        reponse = cur.fetchone()
        print(reponse)
        cur.close()
        return jsonify(make_public_article(make_article(reponse)))
    except Exception as e:
        print(e)
        abort(404)

# fonction pour creer une biere a partir d'une base de donnees
def make_article(biere_bdd):
    list_bieres = list(biere_bdd)
    new_biere = {}
    new_biere["id_article"] = int(list_bieres[0])
    new_biere["nom_article"] = str(list_bieres[1])
    new_biere["prix_achat"] = float(list_bieres[2])
    new_biere["volume"] = int(list_bieres[3])
    new_biere["titrage"] = float(list_bieres[4])  if type(list_bieres[4]) == float else None
    new_biere["ID_MARQUE"] = int(list_bieres[5]) if type(list_bieres[5]) == int else None
    new_biere["ID_Couleur"] = int(list_bieres[6]) if type(list_bieres[6]) == int else None
    new_biere["ID_Type"] = int(list_bieres[7]) if type(list_bieres[7]) == int else None
    return new_biere

# fonction pour creer une url de facon dynamique a partir d'une tache
def make_public_article(article):
    public_article = {}
    for argument in article:
        if argument == "id_article":
            public_article['url'] = url_for('get_article_by_id', article_id = article['id_article'], _external=True)
        else:
            public_article[argument] = article[argument]
    return public_article


# route pour modifier un article precise de ma bdd
@app.route('/articles/<int:article_id>', methods=['PUT'])
def update_article_by_id(article_id):
    article = get_article_by_id(article_id)
    if not request.json:
        abort(400)
    if "nom_article" not in request.json or type(request.json['nom_article']) != str:
        abort(400)
    if "prix_achat" in request.json and type(request.json['prix_achat']) != float:
        abort(400)
    if "volume" in request.json and type(request.json['volume']) is not int:
        abort(400)
    try:
        nom_article = request.json.get('nom_article', article.json['nom_article'])
        prix_achat = request.json.get('prix_achat', article.json['prix_achat'])
        volume = request.json.get('volume', article.json['volume'])
        cur = mysql.connection.cursor()
        cur.execute("UPDATE article SET nom_article=%s, prix_achat=%s, volume=%s WHERE id_article=%s", (nom_article, prix_achat,volume,str(article_id)))
        mysql.connection.commit()
        cur.close()
        return jsonify({'is':True })
    except Exception as e:
        print(e)
        return jsonify({'is':False})

# route pour supprimer une biere de ma bdd
@app.route('/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    article = get_article_by_id(article_id)
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM article WHERE id_article=%s", (str(article_id)))
        mysql.connection.commit()
        cur.close()
        return article
    except Exception as e:
        print(e)
        return jsonify({'is':False})



# annotation app.route('URL')
@app.route('/', methods=['GET'])
def index():
    return "Hello world!"

# lancer mon application
if __name__ == "__main__":
    app.run(debug=True)