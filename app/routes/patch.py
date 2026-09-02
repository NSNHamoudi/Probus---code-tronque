from flask import request, jsonify
from ..app import app
from ..utils.controller import patch_relation, suppr_relation, ajout_relation

"""
Routes permettants différents PATCHs de modification des données de l'API
"""

# *****************************************
# *****************************************
# ** ROUTES AGISSANT SUR LE RELATIONTYPE **
# *****************************************
# *****************************************


# ROUTE DE MODIFICATION DU RELATIONTYPE
# -------------------------------------
@app.route("/patch_relation", methods=["PATCH"])
def patch_relation_route():

    if not request.is_json:
        return jsonify({"error": "Le Content-Type doit être application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    # Récupération des données depuis le frontend -- explications cf. controller.py
    # instanceid = data.get('instanceid')
    # relation = data.get('relation')
    # relationid = data.get('relationid')
    # relationtype = data.get('relationtype')
    # new_relationtype = data.get('new_relationtype')

    try:
        instanceid = data["instanceid"]
        relation = data["relation"]
        relationid = data["relationid"]
        relationtype = data["relationtype"]
        new_relationtype = data["new_relationtype"]
    except KeyError as e:
        return jsonify({"error": f"Champ manquant: {e}"}), 400

    # Appel fonction existante
    try:
        response = patch_relation(
            instanceid, relation, relationid, relationtype, new_relationtype
        )

    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

    # Vérifie si la réponse est du JSON valide
    try:
        response_data = response.json()
    except ValueError:
        # Si ce n'est pas du JSON, retournez une erreur avec le texte brut
        return jsonify(
            {
                "error": f"Réponse non-JSON de l'API externe: {response.text[:200]}...",
                "status_code": response.status_code,
            }
        ), 502

    # Retour de la réponse de l'API externe
    return jsonify(response_data), response.status_code


# ROUTE DE SUPPRESSION DU RELATIONTYPE
# ------------------------------------
@app.route("/suppr_relation", methods=["PATCH"])
def suppr_relation_route():

    if not request.is_json:
        return jsonify({"error": "Le Content-Type doit être application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    # Récupération des données depuis le frontend -- explications cf. controller.py
    # instanceid = data.get('instanceid')
    # relation = data.get('relation')
    # relationid = data.get('relationid')
    # relationtype = data.get('relationtype')

    try:
        instanceid = data["instanceid"]
        relation = data["relation"]
        relationid = data["relationid"]
        relationtype = data["relationtype"]
    except KeyError as e:
        return jsonify({"error": f"Champ manquant: {e}"}), 400

    # Appel fonction existante
    try:
        response = suppr_relation(instanceid, relation, relationid, relationtype)

    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

    # Vérifie si la réponse est du JSON valide
    try:
        response_data = response.json()
    except ValueError:
        # Si ce n'est pas du JSON, retournez une erreur avec le texte brut
        return jsonify(
            {
                "error": f"Réponse non-JSON de l'API externe: {response.text[:200]}...",
                "status_code": response.status_code,
            }
        ), 502

    # Retour de la réponse de l'API externe
    return jsonify(response_data), response.status_code


# ROUTE D'AJOUT D'UNE RELATION
# ------------------------------------
@app.route("/ajout_relation", methods=["PATCH"])
def ajout_relation_route():

    if not request.is_json:
        return jsonify({"error": "Le Content-Type doit être application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    # Récupération des données depuis le frontend -- explications cf. controller.py

    print(data)
    try:
        instanceid = data["instanceid"]
        relation = data["relation"]
        relationid = data["relationid"]
        relationtype = data["relationtype"]
    except KeyError as e:
        print (e)
        return jsonify({"error": f"Champ manquant: {e}"}), 400

    # Appel fonction existante
    try:
        response = ajout_relation(instanceid, relation, relationid, relationtype)

    except Exception as e:
        print (e)
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

    # Vérifie si la réponse est du JSON valide
    try:
        response_data = response.json()
    except ValueError as e:
        print (e)
        # Sinon retourne une erreur
        return jsonify(
            {
                "error": f"Réponse non-JSON de l'API externe: {response.text[:200]}...",
                "status_code": response.status_code,
            }
        ), 502

    # Retour de la réponse de l'API externe
    return jsonify(response_data), response.status_code
