from ..app import app
from flask import render_template


@app.errorhandler(404)
def not_found_error(error):
    return render_template("erreurs/404.html"), 404


@app.errorhandler(408)
def timeout_error(error):
    return render_template("erreurs/408.html"), 408


@app.errorhandler(500)
def internal_error(error):
    return render_template("erreurs/500.html"), 500


@app.errorhandler(503)
def service_error(error):
    return render_template("erreurs/500.html"), 500


# routes
@app.route("/erreur")  # page d'erreur
@app.route("/erreur/404")  # page de l'erreur 404
def erreur_404():
    return render_template("erreurs/404.html")


@app.route("/erreur/408")  # page de l'erreur 408
def erreur_408():
    return render_template("erreurs/408.html")


@app.route("/erreur/500")  # page de l'erreur 500
def erreur_500():
    return render_template("erreurs/500.html")


@app.route("/erreur/503")  # page de l'erreur 503
def erreur_503():
    return render_template("erreurs/503.html")
