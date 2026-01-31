# Import object of Flask class
from flask import Flask

from app.views import views

# Create application factory embedded in run.py
def create_app():
    app = Flask(__name__)  # Create Flask application instance

    app.register_blueprint(views)

    return app