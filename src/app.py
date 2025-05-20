from flask import Flask
from api.routes import projects_bp


def create_app():
    flask_app = Flask(__name__)
    flask_app.register_blueprint(projects_bp)
    return flask_app

# Create an instance for Gunicorn to find
app = create_app()