import os
import sys
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.routes import projects_bp


load_dotenv()

def create_app():
    flask_app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(flask_app)
    
    flask_app.register_blueprint(projects_bp)
    return flask_app

# Create an instance for Gunicorn to find
app = create_app()
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")

if __name__ == "__main__":
    # Run the app with Flask's built-in server for development
    app.run(host="0.0.0.0", debug=True)