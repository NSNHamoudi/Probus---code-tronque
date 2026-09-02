from ..app import app
from flask import request, render_template, redirect, url_for, abort
from ..utils.controller import recup_instances
import requests
from datetime import timedelta
from ..models.formulaires import Correction

"""
Ci-dessous se trouvent les différentes routes permettant l'affichage des templates/pages html
et des informations renvoyées par l'API.
"""


# ---------------------------
# ---------------------------
# LES ROUTES DE L'ACCUEIL
# ---------------------------
# ---------------------------
@app.route("/")  # redirige immédiatement sur la page /index ci-dessous
def home():
    return redirect(url_for("index"))  # fait redirection


@app.route("/index")  # page d'accueil du site
def index():
    return render_template("pages/index.html")  # simple render_template


# --------------------------------
# --------------------------------
# LES ROUTES DES DIFFERENTES PAGES
# --------------------------------
# --------------------------------

# ROUTE INSTANCE
# --------------
# (la route principale, et qui a servi de base à toutes les autres)


@app.route("/instance")
def instance():
    # Récupère l'identifiant
    identifiant = request.args.get("string", "")

    # Initialisation des données pour le template
    instance_api = {
        # Champs principaux de l'instance, tous initialisés à NULL par défaut
        "instanceid": "NULL",
        "duration": "NULL",
        "instancetype": "NULL",
        "typevalue" : "NULL",
        "mediatype": "NULL",
        "mediavalue" : "NULL",
        "provenance": "NULL",
        "status": "NULL",
        "duration_conv": "NULL",
        # sections à ajouter/cocher (initialisées à vide) et instanciées comme listes
        "instance_aggregation": [],
        "instance_annotation": [],
        "instance_archivegroup": [],
        "instance_credit": [],
        "instance_event": [],
        "instance_identifier": [],
        "instance_selector": [],
        "instance_text": [],
        "instance_usage": [],
    }

####################################################################
#########SELECTION DE LISTES & DICTIONNAIRES CODES EN DUR###########
####################################################################
    # Liste des entités existantes pour l'ajout d'une relation - codée en dur de façon temporaire
    entites = [
        "aggregation",
        "annotation",
        "archivegroup",
        "credit",
        "event",
        "identifier",
        "selector",
        "text",
        "usage",
    ]

    # Dictionnaire des types de relationtype
    instance_relationtype = {
    }

####################################################################
##################RECUPERATION DES DONNEES##########################
####################################################################
    if identifiant:  # Si id appelé existe via appel API
        try:
            reponse = recup_instances(
                identifiant
            )  # Pour le cas de l'appel d'API via "/instances"
            reponse.raise_for_status()
            data = reponse.json()

            if (
                data and len(data) > 0
            ):  # si data contient plus de 0 élément (i.e. au moins 1)
                instance = data[
                    0
                ]  # récupère le premier élément qui s'affiche dans la réponse API (i.e. la même valeur que l'identifiant technique de l'instance)

                #  Remplissage des champs ==> Structure suivant celle renvoyée par l'API
                instance_api["instanceid"] = instance.get("id", "NULL")
                instance_api["provenance"] = instance.get("provenance", "NULL")
                instance_api["instancetype"] = instance.get("type", {}).get(
                    "businessid", "NULL"
                )
                instance_api["mediatype"] = instance.get("media", {}).get(
                    "businessid", "NULL"
                )
                instance_api["duration"] = instance.get("duration", "NULL")

                #  Données de duration converties au format HH:MM:SS
                duration_conv = instance.get("duration", "NULL")
                if duration_conv:
                    try:
                        instance_api["duration_conv"] = str(
                            timedelta(milliseconds=int(duration_conv)) # en millisecondes car c'est ce que renvoie les Fragments
                        )
                    except (ValueError, TypeError):
                        instance_api["duration_conv"] = "NULL"
                else:
                    instance_api["duration_conv"] = "NULL"

                # Récupération du LIBPREFA du type de media
                media = instance.get("media",{})
                for mediatexts in media.get("texts", {}) :
                    if mediatexts.get("type") == "LIBPREFA" :
                        mediatext = mediatexts.get("text",{})
                        instance_api["mediavalue"] = mediatext.get("value", "NULL")

                # Idem pour le type d'instance
                type = instance.get("type",{})
                for typetexts in type.get("texts", {}) :
                    if typetexts.get("type") == "LIBPREFA" :
                        typetext = typetexts.get("text",{})
                        instance_api["typevalue"] = typetext.get("value", "NULL")
                
                # ----------------------------------------------------------
                #  Remplissage des sections "ajouts"
                # ===> i.e. toutes les routes, mais relativement à instance
                # (toujours avec la même logique)

                # instance_annotation
                for annotations in instance.get(
                    "annotations", []
                ):  # On appelle 'annotations' tout ce qui découle de la liste 'annotations' renvoyée par l'api
                    ann = annotations.get(
                        "annotation", {}
                    )  # Dans cette liste 'annotations' se trouve un dictionnaire 'annotation' qu'on vient appeler 'ann'
                    instance_api["instance_annotation"].append(
                        {  # On attrivue à 'instance_annotation' précedemment instanciée
                            "instanceid": instance_api[
                                "instanceid"
                            ],  # instanceid pré définie
                            "annotationid": ann.get(
                                "id", "NULL"
                            ),  # la valeur de "id" renvoyée par l'API, renommée 'annotationid', trouvable dans le dictionnaire renommée 'ann'
                            "provenance": ann.get("provenance", "NULL"),  # même logique
                            "relationtype": annotations.get(
                                "type", "NULL"
                            ),  # valeur "type" renommée 'relationtype', depuis liste 'annotations'
                            "relationtype_id": annotations.get(
                                "typeid", "NULL"
                            ),  # idem, pour l'id de type
                            "rang": "NULL",  # pour l'instant, car pas trouvé dans le renvoi API
                        }
                    )

                # instance_aggregation
                for aggregations in instance.get("aggregations", []):
                    agg = aggregations.get("aggregation", {})
                    instance_api["instance_aggregation"].append(
                        {
                            "instanceid": instance_api["instanceid"],
                            "aggregationid": agg.get("id", "NULL"),
                            "relationtype": aggregations.get("type", "NULL"),
                            "relationtype_id": aggregations.get("typeid", "NULL"),
                            "provenance": agg.get("provenance", "NULL"),
                        }
                    )

                # instance_archivegroup
                for archivegroups in instance.get("archivegroups", []):
                    ar = archivegroups.get("archivegroup", {})
                    instance_api["instance_archivegroup"].append(
                        {
                            "instanceid": instance_api["instanceid"],
                            "archivegroupid": ar.get("id", "NULL"),
                            "relationtype": archivegroups.get("type", "NULL"),
                            "relationtype_id": archivegroups.get("typeid", "NULL"),
                            "provenance": ar.get("provenance", "NULL"),
                        }
                    )

                # instance_credit
                for credits in instance.get("credits", []):
                    cr = credits.get("credit", {})
                    type = cr.get("type", {})
                    for agents in cr.get("agents",[]) :
                        agent = () # On instancie à vide pour contourner les bugs
                        for texts in agents.get("agent",{}).get("texts",[]) :
                            txt = texts.get("text",{})
                            if texts.get("type") == "LIBPREFA" :
                                agent = txt.get("value", "NULL")
                        for typetexts in type.get("texts", []):
                            if typetexts.get("type") == "LIBPREFA" :
                                    typetext = typetexts.get("text", {})  
                                    instance_api["instance_credit"].append(
                                        {
                                            "instanceid": instance_api["instanceid"],
                                            "creditid": cr.get("id", "NULL"),
                                            "relationtype": credits.get("type", "NULL"),
                                            "relationtype_id": credits.get("typeid", "NULL"),
                                            "agent": agent,
                                            "typevalue" : typetext.get("value", "NULL")
                                        }
                                    )

                # instance_event
                for events in instance.get("events", []):
                    evt = events.get("event", {})
                    instance_api["instance_event"].append(
                        {
                            "instanceid": instance_api["instanceid"],
                            "eventid": evt.get("id", "NULL"),
                            "relationtype": events.get("type", "NULL"),
                            "relationtype_id": events.get("typeid", "NULL"),
                            "provenance": evt.get("provenance", "NULL"),
                        }
                    )

                # instance_selector
                for selectors in instance.get("selectors", []):
                    sl = selectors.get("selector", {})
                    instance_api["instance_selector"].append(
                        {
                            "instanceid": instance_api["instanceid"],
                            "selectorid": sl.get("id", "NULL"),
                            "relationtype": selectors.get("type", "NULL"),
                            "relationtype_id": selectors.get("typeid", "NULL"),
                            "provenance": sl.get("provenance", "NULL"),
                        }
                    )

                # instance_text
                for texts in instance.get("texts", []):
                    txt = texts.get("text", {})
                    instance_api["instance_text"].append(
                        {
                            "instanceid": instance_api["instanceid"],
                            "textid": txt.get("id", "NULL"),
                            "relationtype": texts.get("type", "NULL"),
                            "relationtype_id": texts.get("typeid", "NULL"),
                            "provenance": txt.get("provenance", "NULL"),
                        }
                    )

                # instance_usage
                for usages in instance.get("usages", []):
                    us = usages.get("usage", {})
                    instance_api["instance_usage"].append(
                        {
                            "instanceid": instance_api["instanceid"],
                            "usageid": us.get("id", "NULL"),
                            "relationtype": usages.get("type", "NULL"),
                            "relationtype_id": usages.get("typeid", "NULL"),
                            "provenance": us.get("provenance", "NULL"),
                            "startdate": us.get("startdate", "NULL"),
                        }
                    )

        # Gestion des erreurs
        except (
            requests.RequestException
        ) as e:  # Si erreur dans la requête/instanceid introuvable/...
            print(
                f"Erreur lors de l'appel à l'API pour l'instance: {e}"
            )  # Affiche un message d'erreur dans le terminal

    form = Correction()

    # Passe toutes les données au template (rend la page html)
    return render_template(
        "pages/instance.html",
        **instance_api,  # Fait passer tout le dictionnaire éponyme sans avoir à le réécrire dans son intégralité ici
        instance_relationtype=instance_relationtype,  # Prise en compte du dictionnaire des référentiels
        entites=entites,  # la liste des entités
        requete=identifiant,  # requête affichée dans la barre de recherche = instanceid (même valeur par définition)
        form=form,  # Passe le formulaire au template
    )


# TOUTES LES AUTRES ROUTES
# ------------------------
# (qui ont en plus des concepts et agents)

# credit
@app.route("/credit")
def credit():
    instanceid = request.args.get("instanceid", "") # instanceid qui est la base de toute requête
    creditid = request.args.get("creditid", "") # creditid renvoyé par l'appel API
    requete = request.args.get("string", "") # requête faite dans la barre de recherche (i.e. l'instance id)

    credit_api = {
        "creditid": "NULL",
        "credittype": "NULL",
        "credittype_id": "NULL",
        "status": "NULL",
        # Puis ce qu'on va récupérer de l'API relativement à l'arborescence du controller/de la réponse à l'appel
        "type_text": [],
        "agent": [],
        "agent_type": [],
        "texts_agent": [],
        "concept": [],
        "conceptscheme": [],
        "concept_type": [],
        "texts_concept": [],
        "idcard" : []
    }

    if instanceid and creditid:
        try:
            reponse = recup_instances(instanceid)
            reponse.raise_for_status()
            data = reponse.json()

            if data and len(data) > 0:
                instance = data[0]

                # D'abord ce que les credits renvoient par défaut :
                #  creditid
                for cr in instance.get("credits", []):
                    if cr.get("credit", {}).get("id") == creditid:
                        credit = cr.get("credit", {})
                        credit_api["creditid"] = credit.get("id", "NULL")

                        # type de credit
                        credit_type = credit.get("type", {})
                        credit_api["credittype"] = credit_type.get("businessid", "NULL")
                        credit_api["credittype_id"] = credit_type.get("id", "NULL")

                        # Détails du type de credit
                        for type in credit.get("type", {}):
                            type = credit.get("type", {})
                            for texts in type.get("texts"):
                                if texts.get("text"):
                                    txt = texts.get("text", {})
                                    if texts.get("type") != "ARBO" : # Arborescence exclue, à la demande de Qualité
                                        credit_api["type_text"].append(
                                            {
                                                "credittype": type.get(
                                                    "businessid", "NULL"
                                                ),
                                                "credittypeid": type.get("id", "NULL"),
                                                "type": texts.get("type", "NULL"),
                                                "provenance": txt.get("provenance", "NULL"),
                                                "id": txt.get("id", "NULL"),
                                                "texttype": txt.get("type", "NULL"),
                                                "lang": txt.get("lang", "NULL"),
                                                "value": txt.get("value", "NULL"),
                                            }
                                        )

                        # Puis ce qui est relatif aux agents des credits
                        for agents in credit.get("agents", []):
                            agent = agents.get("agent", {})
                            agenttype = agent.get("type", {})
                            agentid = agent.get("id", "NULL")

                            (
                                credit_api["agent"].append(
                                    {
                                        "agentid": agentid,
                                        "provenance": agent.get("provenance", "NULL"),
                                        "agenttype": agenttype.get(
                                            "businessid", "NULL"
                                        ),
                                        "agenttype_id": agenttype.get("id", "NULL"),
                                        "relationtype": agents.get("type", "NULL"),
                                        "relationtype_id": agents.get("typeid", "NULL"),
                                    }
                                ),
                            )

                            # type des agents
                            for texts in agenttype.get("texts"):
                                if texts.get("type") != "ARBO" and texts.get("text"):
                                    txt = texts.get("text", {})
                                    credit_api["agent_type"].append(
                                        {
                                            "agentid": agentid,
                                            "credittype": agenttype.get(
                                                "businessid", "NULL"
                                            ),
                                            "credittypeid": agenttype.get("id", "NULL"),
                                            "type": texts.get("type", "NULL"),
                                            "provenance": txt.get("provenance", "NULL"),
                                            "id": txt.get("id", "NULL"),
                                            "texttype": txt.get("type", "NULL"),
                                            "lang": txt.get("lang", "NULL"),
                                            "value": txt.get("value", "NULL"),
                                        }
                                    )

                            # texts des agents
                            for texts in agent.get("texts"):
                                text = texts.get("text", {})
                                credit_api["texts_agent"].append(
                                    {
                                        "agentid": agentid,
                                        "type": texts.get("type", "NULL"),
                                        "typeid": texts.get("typeid", "NULL"),
                                        "id": text.get("id", "NULL"),
                                        "value": text.get("value", "NULL"),
                                        "lang": text.get("lang", "NULL"),
                                        "texttype": text.get("type", "NULL"),
                                        "provenance" : text.get("provenance", "NULL")
                                    }
                                )

                                # idcard pour le nom qui s'affiche en haut de la page par soucis de clarté
                                # (renvoie le libellé préférentiel de ce qui a été crédité)
                                if texts.get("type") == "LIBPREFA" :
                                    credit_api["idcard"].append(
                                        {
                                            "agentid": agentid,
                                            "namevalue": text.get("value", "NULL"),
                                        }
                                    )
                            
                            

                        # Concepts des credits
                        for concepts in credit.get("concepts", []):
                            concept = concepts.get("concept", {})
                            scheme = concept.get("conceptscheme", {})
                            conceptid = concept.get("id", "NULL")
                            concepttype = concept.get("type", {})

                            (
                                credit_api["concept"].append(
                                    {
                                        "conceptid": conceptid,
                                        "provenance": concept.get("provenance", "NULL"),
                                        "relationtype": concepts.get("type", "NULL"),
                                        "relationtype_id": concepts.get(
                                            "typeid", "NULL"
                                        ),
                                    }
                                ),
                            )

                            # type de concept
                            for texts in concepttype.get("texts"):
                                if texts.get("type") != "ARBO" and texts.get("text"):
                                    txt = texts.get("text", {})
                                    credit_api["concept_type"].append(
                                        {
                                            "conceptid": conceptid,
                                            "concepttype": concepttype.get(
                                                "businessid", "NULL"
                                            ),
                                            "credittypeid": concepttype.get("id", "NULL"),
                                            "type": texts.get("type", "NULL"),
                                            "provenance": txt.get("provenance", "NULL"),
                                            "id": txt.get("id", "NULL"),
                                            "texttype": txt.get("type", "NULL"),
                                            "lang": txt.get("lang", "NULL"),
                                            "value": txt.get("value", "NULL"),
                                        }
                                    )                           

                            # conceptscheme
                            txt = scheme.get("text", {})
                            credit_api["conceptscheme"].append(
                                {
                                    "conceptid": conceptid,
                                    "id": scheme.get("id", "NULL"),
                                    "provenance": txt.get("provenance", "NULL"),
                                    "textid": txt.get("id", "NULL"),
                                    "texttype": txt.get("type", "NULL"),
                                    "lang": txt.get("lang", "NULL"),
                                    "value": txt.get("value", "NULL"),
                                    "text_relationtype": texts.get(
                                        "type", "NULL"
                                    ),      
                                }
                            )

                            # texts des concepts
                            for texts in concept.get("texts", []):
                                if texts.get("type") != "ARBO" :
                                    text = texts.get("text", {})
                                    credit_api["texts_concept"].append(
                                        {
                                            "conceptid": conceptid,
                                            "type": texts.get("type", "NULL"),
                                            "typeid": texts.get("typeid", "NULL"),
                                            "id": text.get("id", "NULL"),
                                            "value": text.get("value", "NULL"),
                                            "lang": text.get("lang", "NULL"),
                                            "texttype": text.get("type", "NULL"),
                                            "provenance" : text.get("provenance", "NULL")
                                        }
                                    )

        except requests.RequestException as re:
            print(f"Erreur lors de l'appel à l'API pour credit: {re}")

    form = Correction()

    return render_template(
        "pages/credit.html", **credit_api, requete=requete, form=form
    )

