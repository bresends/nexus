from flask import Blueprint, render_template
from models.project import Project
from database.database import SessionLocal

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
def list_projects():
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        return render_template("projects.html", projects=projects)
    finally:
        db.close()


@projects_bp.route("/project/<int:project_id>")
def project_detail(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return "Project not found", 404
        return render_template("project_detail.html", project=project)
    finally:
        db.close()
