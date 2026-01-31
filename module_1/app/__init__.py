"""
This Python script is used to configure a Flask application which
contains URL routes within a 'views' blueprint.
"""
from flask import Flask # Import object of Flask class
from app.views import views # Import views blueprint

"""
This function Create Flask application with routes via a blueprint.
"""
def create_app():
    app = Flask(__name__)  # Create Flask app instance

    app.register_blueprint(views)   # Register the blueprint routes

    return app