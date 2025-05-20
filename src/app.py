from flask import Flask
from api.routes import projects_bp


def create_app():
    flask_app = Flask(__name__)
    flask_app.register_blueprint(projects_bp)
    return flask_app

# Create an instance for Gunicorn to find
app = create_app()

if __name__ == "__main__":
    # Run the app with Flask's built-in server for development
    app.run(host="0.0.0.0", debug=True)