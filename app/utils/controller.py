from base64 import b64encode
import os
import requests
import json
from .activites import get_activity_action


def recup_headers() -> dict[str, str]:
    username = os.getenv("EXTERNAL_API_USERNAME")
    password = os.getenv("EXTERNAL_API_PASSWORD")
    # Authorization token: we need to base 64 encode it
    # and then decode it to acsii as python 3 stores it as a byte string
    token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")

    return {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {token}",
    }


# --------------------------------
# Tout ce qui agit sur l'instance
# --------------------------------


# Pas de GET mais un POST structuré via body ci dessous
def recup_instances(
    identifiant: str,
) -> requests.Response: 
    url = os.getenv("EXTERNAL_API_URL") + os.getenv("INSTANCE")

    payload = {  # La requête API
        "identifier": {
            "entity": "instance",
            "type": "identifiant technique",
            "id": [identifiant],
        },
        "schema": {
            "instances": {},
            "texts": {},
            "aggregations": {
                "schema": {
                    "texts": {},
                    "identifiers": {},
                    "concepts": {
                        "schema": {
                            "texts": {}
                        }
                    }
                }
            },
            "annotations": {
                "schema": {
                    "concepts": {
                        "schema": {
                            "texts": {}
                        }
                    },
                    "agents": {
                        "schema": {
                            "texts": {}
                        }
                    }
                }
            },
            "archivegroups": {
                "schema": {
                    "concepts": {
                        "schema": {
                            "texts": {}
                        }
                    },
                    "texts": {},
                    "identifiers": {}
                }
            },
            "credits": {
                "schema": {
                    "texts": {},
                    "agents": {
                        "schema": {
                            "texts": {}
                        }
                    },
                    "concepts": {
                        "schema": {
                            "texts": {}
                        }
                    }
                }
            },
            "selectors": {
                "schema": {
                    "concepts": {
                        "schema": {
                            "texts": {}
                        }
                    },
                    "segments": {
                        "schema": {
                            "texts": {
                                "schema": "identifiers"
                            }
                        }
                    }
                }
            },
            "usages": {
                "schema": {
                    "agents": {
                        "schema": {
                            "texts": {}
                        }
                    }
                }
            },
            "events": {
                "schema": {
                    "texts": {},
                    "agents": {
                        "schema": {
                            "texts": {}
                        }
                    },
                    "concepts": {
                        "schema": {
                            "texts": {}
                        }
                    },
                    "selector": {
                        "schema": {
                            "item": {}
                        }
                    }
                }
            }
        }
    }

    headers = recup_headers()
    return requests.post(
        url, json=payload, headers=headers
    )


# Patch de modification des relationtype
def patch_relation(
    instanceid: str,
    relation: str,
    relationid: str,
    relationtype: str,
    new_relationtype: str,
) -> requests.Response:
    """Envoie une requête PATCH à l'API externe pour mettre à jour le relationtype

    Args:
        instanceid (str) : ID de l'instance en question
        relation (str) : Entitée liée (ex: "event" pour "instance_event")
        relationid (str): ID de la relation liée
        relationtype (str): ID de la relation à modifier
        new_relationtype (str): Nouvelle valeur de relationtype
    Returns:
        requests.Response: Réponse de l'API."""

    url = os.getenv("EXTERNAL_API_URL") + "majFragments/"

    # Variables dynamiques
    type_relation = (
        f"{relation.split('_')[1]}id"  # Ex: "instance_annotation" -> "annotationid"
    )
    relation = f"{relation.split('_')[1]}"  # attribue la bonne valeur au "relation" susmentionné

    payload = {
        "actions": [
            {
                "data": [
                    {
                        "instanceid": instanceid,
                        type_relation: relationid,
                        "relationtype": relationtype,
                    }
                ],
                "action": "unset",
                "type": relation,
                "targetentity": "instance",
            },
            {
                "data": [
                    {
                        "instanceid": instanceid,
                        type_relation: relationid,
                        "relationtype": new_relationtype,
                    }
                ],
                "action": "set",
                "type": relation,
                "targetentity": "instance",
            },
            get_activity_action("instance", instanceid),
        ]
    }

    headers = {"Content-Type": "application/json", **recup_headers()}

    print(
        json.dumps(payload, indent=2)
    )  # print le payload dans le terminal en s'assurant qu'il a des guillemets doubles (sans quoi, renvoie une erreur 503)

    response = requests.patch(url, json=payload, headers=headers, verify=False)
    return response


# Suppression
def suppr_relation(
    instanceid: str, relation: str, relationid: str, relationtype: str
) -> requests.Response:
    """Envoie une requête PATCH à l'API externe pour supprimer le relationtype
     (même logique que ci-dessus)

    Args:
        instanceid (str) : ID de l'instance en question
        relation (str) : Entité liée (ex: "event" pour "instance_event")
        relationid (str): ID de la relation liée
        relationtype (str): ID de la relation à supprimer
    Returns:
        requests.Response: Réponse de l'API."""

    url = os.getenv("EXTERNAL_API_URL") + os.getenv("PATCH")

    # Variables dynamiques
    type_relation = (
        f"{relation.split('_')[1]}id"  # Ex: "instance_annotation" -> "annotationid"
    )
    relation = f"{relation.split('_')[1]}"  # attribue la bonne valeur au "relation" susmentionné

    payload = {
        "actions": [
            {
                "data": [
                    {
                        "instanceid": instanceid,
                        type_relation: relationid,
                        "relationtype": relationtype,
                    }
                ],
                "action": "unset",
                "type": relation,
                "targetentity": "instance",
            },
            get_activity_action("instance", instanceid),
        ]
    }

    headers = {"Content-Type": "application/json", **recup_headers()}

    print(
        json.dumps(payload, indent=2)
    )  # print le payload dans le terminal en s'assurant qu'il a des guillemets doubles (sans quoi, renvoie une erreur 503)

    response = requests.patch(url, json=payload, headers=headers, verify=False)
    return response


# Ajout
def ajout_relation (instanceid: str, relation: str, relationid: str, relationtype: str) -> requests.Response:
    """ Envoie une requête PATCH à l'API externe pour supprimer le relationtype
     (même logique que ci-dessus)

    Args:
        instanceid (str) : ID de l'instance en question
        relation (str) : Entité liée (ex: "event" pour "instance_event")
        relationid (str): ID de la relation liée
        relationtype (str): ID de la relation à ajouter
    Returns:
        requests.Response: Réponse de l'API."""
    
    url = os.getenv("EXTERNAL_API_URL") + os.getenv("PATCH")

    # Variables dynamiques
    relation = f"{relation}" # attribue la bonne valeur au "relation" susmentionné
    type_relation = f"{relation}id"  # Ex: "instance_annotation" -> "annotationid"

    payload = {
            "actions": [
                {
                "data": [
                    {
                    "instanceid": instanceid,
                    type_relation: relationid,
                    "relationtype": relationtype
                    }
                ],
                "action": "set",
                "type": relation,
                "targetentity": "instance"
                },
                get_activity_action("instance", instanceid),
            ]
        }

    headers = {
            "Content-Type": "application/json",
            **recup_headers()
    }

    print(json.dumps(payload, indent=2)) # print le payload dans le terminal en s'assurant qu'il a des guillemets doubles (sans quoi, renvoie une erreur 503)

    response = requests.patch(url, json=payload, headers=headers, verify=False)

    return response