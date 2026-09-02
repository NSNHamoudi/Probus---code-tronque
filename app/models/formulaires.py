from ..app import app
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import Optional
from wtforms.validators import DataRequired


class Recherche(FlaskForm):
    string = StringField(
        "Recherche", validators=[Optional()]
    )  # Je devrais pas le mettre en required ?


class Correction(FlaskForm):
    """
    Formulaire pour modifier le relationtype d'une relation.
    """

    # Champ pour le nouveau relationtype
    new_relationtype = StringField(
        "Nouveau type de relation",
        validators=[DataRequired(message="Le type de relation est obligatoire.")],
    )

    # Champ caché pour stocker l'id de l'instance sur laquelle on agit
    instanceid = HiddenField(
        "Identifiant technique de l'instance", validators=[DataRequired()]
    )

    # Champ caché pour stocker l'ID de la relation à modifier
    relationtype = HiddenField("ID de la relation", validators=[DataRequired()])

    # Champ caché pour stocker l'entité liée à la relation (ex: "event" pour "instance_event", etc...)
    relation = HiddenField("Type de relation", validators=[DataRequired()])

    # Champ caché pour stocker l'id de la relation à ajouter
    relationid = HiddenField("Id de la relation", validators=[DataRequired()])
