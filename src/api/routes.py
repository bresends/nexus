from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models.project import Project
from database.database import SessionLocal
from sqlalchemy import exc

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
def list_projects():
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        return render_template("projects.html", projects=projects)
    finally:
        db.close()
        
        
@projects_bp.route("/projects/new", methods=["GET"])
def new_project():
    return render_template("create_project.html")


@projects_bp.route("/projects/create", methods=["POST"])
def create_project():
    db = SessionLocal()
    try:
        # Create a new project from form data
        new_project = Project(
            name=request.form.get("name", ""),
            description=request.form.get("description", ""),
            purpose=request.form.get("purpose", ""),
            desired_outcome=request.form.get("desired_outcome", ""),
            status=request.form.get("status", "Planning"),
            priority=request.form.get("priority", "Medium")
        )
        
        # Handle deadline (could be empty)
        deadline_str = request.form.get("deadline")
        if deadline_str:
            new_project.deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            
        # Add and commit to DB
        db.add(new_project)
        db.commit()
        
        flash(f"Project '{new_project.name}' was successfully created.", "success")
        return redirect(url_for("projects.project_detail", project_id=new_project.id))
    except exc.SQLAlchemyError as e:
        db.rollback()
        flash(f"Error creating project: {str(e)}", "danger")
        return redirect(url_for("projects.new_project"))
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


@projects_bp.route("/project/<int:project_id>/edit", methods=["GET"])
def edit_project(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return "Project not found", 404
        return render_template("edit_project.html", project=project)
    finally:
        db.close()


@projects_bp.route("/project/<int:project_id>/update", methods=["POST"])
def update_project(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            flash("Project not found", "danger")
            return redirect(url_for("projects.list_projects"))
            
        # Update project attributes from form data
        project.name = request.form.get("name")
        project.description = request.form.get("description")
        project.purpose = request.form.get("purpose")
        project.desired_outcome = request.form.get("desired_outcome")
        project.status = request.form.get("status")
        project.priority = request.form.get("priority")
        
        # Handle deadline (could be empty)
        deadline_str = request.form.get("deadline")
        if deadline_str:
            project.deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        else:
            project.deadline = None
        
        db.commit()
        flash(f"Project '{project.name}' updated successfully!", "success")
        return redirect(url_for("projects.project_detail", project_id=project.id))
    except exc.SQLAlchemyError as e:
        db.rollback()
        flash(f"Error updating project: {str(e)}", "danger")
        return redirect(url_for("projects.edit_project", project_id=project_id))
    finally:
        db.close()


@projects_bp.route("/project/<int:project_id>/delete", methods=["GET"])
def delete_project(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return "Project not found", 404
            
        status_modifiers = {
            'Planning': 'planning',
            'In Progress': 'in-progress',
            'Completed': 'completed',
            'On Hold': 'on-hold'
        }
        
        return render_template("delete_project.html", project=project, status_modifiers=status_modifiers)
    finally:
        db.close()


@projects_bp.route("/project/<int:project_id>/delete/confirm", methods=["POST"])
def delete_project_confirm(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            flash("Project not found", "danger")
            return redirect(url_for("projects.list_projects"))
            
        project_name = project.name  # Save name before deletion for message
        db.delete(project)
        db.commit()
        
        flash(f"Project '{project_name}' has been permanently deleted.", "success")
        return redirect(url_for("projects.list_projects"))
    except exc.SQLAlchemyError as e:
        db.rollback()
        flash(f"Error deleting project: {str(e)}", "danger")
        return redirect(url_for("projects.delete_project", project_id=project_id))
    finally:
        db.close()
