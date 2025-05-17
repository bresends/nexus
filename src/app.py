from flask import Flask
from api.routes import projects_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(projects_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", debug=True)