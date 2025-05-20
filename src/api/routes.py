from flask import Blueprint, render_template
from models.project import Project
from database.database import SessionLocal

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects')
def list_projects():
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        return render_template('projects.html', projects=projects)
    finally:
        db.close()
