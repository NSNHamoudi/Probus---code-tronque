from flask import Flask
from .config import Config

app = Flask(__name__, template_folder="templates", static_folder="statics")

app.config.from_object(Config)


# Vérification que l'url API est bien défininie
if not Config.EXTERNAL_API_URL:
    raise ValueError("EXTERNAL_API_URL n'est pas défini")

# Import des routes
from .routes import generales, erreurs, patch, recherche
