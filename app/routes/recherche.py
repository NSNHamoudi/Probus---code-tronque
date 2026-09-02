from ..app import app
from ..models.formulaires import Recherche
from flask import request, render_template
from ..utils.controller import recup_instances
import requests
from datetime import timedelta


# Route pour la recherche (simple)
@app.route("/recherche", methods=["GET", "POST"])
def recherche():
    form = Recherche()  # Instancie le formulaire (cf. formulaires.py)

    # Initialisation des variables
    resultats = {}
    requete = ""

    #  Gestion de la requête
    if request.method == "POST" and form.validate_on_submit():
        requete = form.string.data  # Récupère la valeur du formulaire

    else:
        requete = request.args.get("string", "")  # Pré-remplit le formulaire
        form.string.data = requete

    #  Initialisation des résultats (NULL par défaut)
    resultats = {
        # Les id
        "aggregationid": ["NULL"],
        "annotationid": ["NULL"],
        "archivegroupid": ["NULL"],
        "creditid": ["NULL"],
        "eventid": ["NULL"],
        "instanceid": ["NULL"],
        "selectorid": ["NULL"],
        "usageid": ["NULL"],
        "textid": ["NULL"],
        # Les infos plus précises (surtout pour clarifier l'affichage)
        "startDate": ["NULL"], # à potentiellement retoucher pour ranger dans event ?
        "endDate": ["NULL"], # re ?
        "type": ["NULL"],
        "texts": [{"id": "NULL", "type": "NULL"}],
        "aggregations": [{"id": "NULL", "value": "NULL"}],
        "annotations": [{"id":"NULL","value": "NULL","concept":"NULL"}],
        "archivegroups": [{"id": "NULL", "value": "NULL", "groupe" : "NULL"}],
        "credits": [{"id": "NULL", "role": "NULL", "agent" : "NULL"}],
        "usages": [{"id": "NULL", "value": "NULL"}],
        "selectors": [{"id": "NULL", "type": "NULL"}],
    }

    carte = {
        # Les informations nécessaires à la carte d'identité
        "instance": ["NULL"],
        "event": ["NULL"],
        "text": ["NULL"],
        "archivegroup" : ["NULL"],
    }
    #  Appel à l'API si une requête est effectuée
    if requete:
        try:
            response = recup_instances(requete)
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:  # Si non-vide
                instance = data[0]  # Récupère la première instance

                # instanceid
                if instance.get("id"):
                    resultats["instanceid"] = [instance["id"]]

                # Puis on boucle sur les suivants pour déceller tous ceux présents dans l'API
                # (id pour permettre de lier les pages entre elles + les diverses infos demandées à l'affichage)

                # aggregationid
                if instance.get("aggregations"):
                    agg_liste = []
                    for agg in instance.get("aggregations", []):
                        agg_data = agg.get("aggregation", {})
                        for agg_texts in agg_data.get("texts", []) :
                            agg_text = agg_texts.get("text",{})
                            for typetexts in agg_data.get("type",{}).get("texts",[]) :
                                    text = typetexts.get("text",{})
                                    if typetexts.get("type") != "ARBO" and agg_texts.get("type") == "ARBO" and agg_text.get("lang") == "fre":
                                        agg_liste.append(
                                            {   "id": agg_data.get("id", "NULL"),
                                                "value": text.get("value", "NULL"),
                                                "corpus" : agg_text.get("value","NULL")
                                            }
                                        )
                                    
                            resultats["aggregations"] = (
                                agg_liste if agg_liste else [{"id":"NULL","value": "NULL"}]
                            )

                # annotationid
                if instance.get("annotations"):
                    ant_liste = []
                    for ant in instance.get("annotations", []):
                        ant_data = ant.get("annotation", {})
                        for typetexts in ant_data.get("type",{}).get("texts",[]) :
                                text = typetexts.get("text",{})
                                for concepts in ant_data.get("concepts",[]) :
                                    for texts in concepts.get("concept",{}).get("texts",[]) :
                                        txt = texts.get("text",{})
                                        if typetexts.get("type") != "ARBO" and texts.get("type") == "LIBPREFA" and txt.get("lang") == "fre":
                                            ant_liste.append(
                                                {   "id": ant_data.get("id", "NULL"),
                                                    "value": text.get("value", "NULL"),
                                                    "concept": txt.get("value", "NULL")
                                                }
                                            )
                        
                    resultats["annotations"] = (
                        ant_liste if ant_liste else [{"id":"NULL","value": "NULL","concept":"NULL"}]
                    )

                # archivegroupid
                if instance.get("archivegroups"):
                    ar_liste = []
                    for ar in instance.get("archivegroups", []):
                        ar_data = ar.get("archivegroup", {})
                        for texts in ar_data.get("type",{}).get("texts",[]) :
                                txt = texts.get("text",{})
                                for ar_texts in ar_data.get("texts", []) :
                                    ar_txt = ar_texts.get("text",{})
                                    if texts.get("type") != "ARBO" and ar_texts.get("type") == "LIB":
                                        ar_liste.append(
                                            {
                                                "id": ar_data.get("id", "NULL"),
                                                "value": txt.get("value", "NULL"),
                                                "groupe" : ar_txt.get("value", "NULL")
                                            }
                                        )
                        resultats["archivegroups"] = (
                            ar_liste if ar_liste else [{"id":"NULL","value": "NULL", "groupe" : "NULL"}]
                        )

                # creditid
                if instance.get("credits"):
                    cr_liste = []
                    for cr in instance.get("credits", []):
                        cr_data = cr.get("credit", {})
                        for agents in cr_data.get("agents",[]) :
                            agent = ()
                            role = () # On instancie à vide pour contourner les bugs
                            for texts in agents.get("agent",{}).get("texts",[]) :
                                txt = texts.get("text",{})
                                if texts.get("type") == "LIBPREFA" :
                                    agent = txt.get("value", "NULL")
                        for concepts in cr_data.get("concepts", []) :
                            for texts in concepts.get("concept",{}).get("texts",[]) :
                                txt = texts.get("text",{})
                                if texts.get("type") == "LIBPREFA" and txt.get("lang") == "fre" and concepts.get("type") == "ROLE" :
                                    role = txt.get("value", "NULL")

                                    cr_liste.append(
                                    {   "id": cr_data.get("id", "NULL"),
                                        "role": role,
                                        "agent": agent,
                                    }
                                )
                    
                                    resultats["credits"] = (
                                        cr_liste if cr_liste else [{"id":"NULL","role": "NULL","agent":"NULL"}]
                                    )

                # eventid
                if instance.get("events"):
                    event_liste = [
                        event.get("event", {}).get("id")
                        for event in instance.get("events", [])
                        if event.get("event", {}).get("id")
                    ]
                    resultats["eventid"] = event_liste if event_liste else ["NULL"]

                    # Pour l'affichage des dates dans le template

                    startdate_event = [
                        event.get("event", {}).get("startDate")
                        for event in instance.get("events", [])
                        if event.get("event", {}).get("startDate")
                    ]
                    resultats["startDate"] = (
                        startdate_event if startdate_event else ["NULL"]
                    )

                    enddate_event = [
                        event.get("event", {}).get("endDate")
                        for event in instance.get("events", [])
                        if event.get("event", {}).get("endDate")
                    ]
                    resultats["endDate"] = enddate_event if enddate_event else ["NULL"]

    
                # selectorid
                if instance.get("selectors"):
                    sl_liste = []
                    for sl in instance.get("selectors", []):
                        sl_data = sl.get("selector", {})
                        if sl_data.get("id"):
                            sl_liste.append(
                                {
                                    "id": sl_data.get("id", "NULL"),
                                    "type": sl.get("type", "NULL"),
                                }
                            )
                    resultats["selectors"] = (
                        sl_liste if sl_liste else [{"id": "NULL", "type": "NULL"}]
                    )

                # usageid
                if instance.get("usages"):
                    us_liste = []
                    for us in instance.get("usages", []):
                        us_data = us.get("usage", {})
                        for texts in us_data.get("type",{}).get("texts",[]) :
                                txt = texts.get("text",{})
                                if texts.get("type") != "ARBO" :
                                    us_liste.append(
                                        {
                                            "id": us_data.get("id", "NULL"),
                                            "value": txt.get("value", "NULL"),
                                        }
                                    )
                        resultats["usages"] = (
                            us_liste if us_liste else [{"id": "NULL", "value": "NULL"}]
                        )

                # textid
                if instance.get("texts"):
                    text_liste = []
                    for txt in instance.get("texts", []):
                        text_data = txt.get("text", {})
                        if text_data.get("id"):
                            text_liste.append(
                                {
                                    "id": text_data.get("id", "NULL"),
                                    "type": txt.get(
                                        "type", "NULL"
                                    ),  # appelle type également pour l'affichage du template
                                }
                            )
                    resultats["texts"] = (
                        text_liste if text_liste else [{"id": "NULL", "type": "NULL"}]
                    )

                # Puis les infos nécessaires pour la carte d'identité de l'archive

                # instance
                for typetexts in instance.get("type", {}).get("texts", []) :
                        typetxt = typetexts.get("text",{})
                        for texts in instance.get("media", {}).get("texts", {}) :
                            txt = texts.get("text",{})
                            if typetexts.get("type") == "LIBPREFA" and texts.get("type", []) == "LIBPREFA":
                                carte["instance"].append(
                                    {
                                        "instanceid": instance.get("id", "NULL"),
                                        "provenance": instance.get("provenance", "NULL"),
                                        "instancetype": typetxt.get("value", "NULL"),
                                        "mediatype": txt.get("value", "NULL")
                                    }
                                )
                            duration = instance.get("duration", "NULL")
                            if duration:
                                try:

                                    carte['instance'][-1]['duration'] = str(timedelta(milliseconds=int(duration))) # [-1] pour accéder au dernier élément de la liste (dict.)
                                except (ValueError, TypeError):
                                    carte["instance"][-1]["duration"] = "NULL"
                            else:
                                carte["instance"][-1]["duration"] = "NULL"

                # event
                for events in instance.get("events", []):
                    evt = events.get("event", {})
                    if evt.get("type", {}).get("businessid") == "EVD" :
                        carte["event"].append(
                            {
                                "startdate": evt.get("startDate", "NULL"),
                                "enddate": evt.get("endDate", "NULL"),
                                "provenance": evt.get("provenance", "NULL"),
                            }
                        )

                        for agt in evt.get("agents", []):
                            agent = agt.get("agent", {})
                            for texts in agent.get("texts", []):
                                if texts.get("type") == "LIBPREFA":
                                    carte["event"][-1]["chaine"] = texts.get( # Bricolage pour récupérer la chaîne de diffusion
                                        "text", {}
                                    ).get("value", "NULL")

                # text
                for texts in instance.get("texts", []):
                    txt = texts.get("text", {})
                    if texts.get("type") == "TI":
                        carte["text"].append({"textvalue": txt.get("value", "NULL")})

                # archivegroup
                for archivegroups in instance.get("archivegroups", []):
                        archivegroup = archivegroups.get("archivegroup", {})
                        for texts in archivegroup.get("texts", []) :
                            if texts.get("type") == "LIB" :
                                txt = texts.get("text",{})
                                carte["archivegroup"].append({"value" : txt.get("value", "NULL")})


        except requests.RequestException as re:
            print(f"Erreur lors de l'appel à l'API: {re}")
            # Vérifie l'attribut de l'erreur
            if hasattr(re, "response") and re.response is not None:
                status = re.response.status_code
                if status == 404:
                    return render_template("erreurs/404.html"), 404
                elif status == 408:
                    return render_template("erreurs/408.html"), 408
                elif status == 500:
                    return render_template("erreurs/500.html"), 500
                elif status == 503:
                    return render_template("erreurs/503.html"), 503
            else:
                return render_template("erreurs/500.html"), 500

        print(f"Requête: {requete}")
        print(f"Résultats: {resultats}")
        print(f"Informations de l'archive: {resultats}")

    #  Rendu du template
    return render_template(
        "pages/resultats_recherche.html",
        form=form,
        carte=carte,
        resultats=resultats,
        requete=requete,
    )
