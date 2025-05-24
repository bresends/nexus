import os
from flask import Flask
from api.routes import projects_bp, prompts_bp
from dotenv import load_dotenv


load_dotenv()

def create_app():
    flask_app = Flask(__name__)
    flask_app.register_blueprint(projects_bp)
    flask_app.register_blueprint(prompts_bp)
    return flask_app

# Create an instance for Gunicorn to find
app = create_app()
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")

if __name__ == "__main__":
    # Run the app with Flask's built-in server for development
    app.run(host="0.0.0.0", debug=True)