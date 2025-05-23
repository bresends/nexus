from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models.project import Project
from models.task import Task
from database.database import SessionLocal
from sqlalchemy import exc, func
from utils.markdown_helper import md_to_html
from models.resource import Resource

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
def list_projects():
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        return render_template("projects/projects.html", projects=projects)
    finally:
        db.close()


@projects_bp.route("/projects/new", methods=["GET"])
def new_project():
    return render_template("projects/create_project.html")


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
            priority=request.form.get("priority", "Medium"),
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


@projects_bp.route("/projects/<int:project_id>")
def project_detail(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return "Project not found", 404
        # Fetch tasks related to the project, ordered by order field
        tasks = (
            db.query(Task)
            .filter(Task.project_id == project_id)
            .order_by(Task.sort_order)
            .all()
        )

        # Convert markdown to HTML
        description_html = md_to_html(project.description)
        purpose_html = md_to_html(project.purpose)
        desired_outcome_html = md_to_html(project.desired_outcome)

        return render_template(
            "projects/project_detail.html",
            project=project,
            tasks=tasks,
            description_html=description_html,
            purpose_html=purpose_html,
            desired_outcome_html=desired_outcome_html,
        )
    finally:
        db.close()


@projects_bp.route("/projects/<int:project_id>/edit", methods=["GET"])
def edit_project(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return "Project not found", 404
        return render_template("projects/edit_project.html", project=project)
    finally:
        db.close()


@projects_bp.route("/projects/<int:project_id>/update", methods=["POST"])
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


@projects_bp.route("/projects/<int:project_id>/delete", methods=["GET"])
def delete_project(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return "Project not found", 404

        status_modifiers = {
            "Planning": "planning",
            "In Progress": "in-progress",
            "Completed": "completed",
            "On Hold": "on-hold",
        }

        return render_template(
            "projects/delete_project.html",
            project=project,
            status_modifiers=status_modifiers,
        )
    finally:
        db.close()


@projects_bp.route("/projects/<int:project_id>/delete/confirm", methods=["POST"])
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


@projects_bp.route("/projects/<int:project_id>/tasks/add", methods=["POST"])
def add_task(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            flash("Project not found.", "danger")
            return redirect(url_for("projects.list_projects"))

        task_name = request.form.get("name")
        task_description = request.form.get("description")
        task_context = request.form.get("context")
        task_priority = request.form.get("priority", "Medium")
        task_due_date_str = request.form.get("due_date")

        # Get the highest order number for this project's tasks
        max_order = (
            db.query(func.max(Task.sort_order))
            .filter(Task.project_id == project_id)
            .scalar()
            or -1
        )
        next_order = max_order + 1

        if not task_name:
            flash("Task name is required.", "warning")
            return redirect(url_for("projects.new_task_page", project_id=project_id))

        task_due_date = None
        if task_due_date_str:
            try:
                task_due_date = datetime.strptime(task_due_date_str, "%Y-%m-%d")
            except ValueError:
                flash(
                    f"Invalid due date format for task '{task_name}'. Please use YYYY-MM-DD.",
                    "warning",
                )
                return redirect(
                    url_for("projects.new_task_page", project_id=project_id)
                )

        new_task = Task(
            project_id=project_id,
            name=task_name,
            description=task_description,
            context=task_context,
            priority=task_priority,
            status="todo",  # Default status
            due_date=task_due_date,
            sort_order=next_order,  # Set the order to be last
        )

        db.add(new_task)
        db.commit()
        flash(
            f"Task '{new_task.name}' added successfully to project '{project.name}'.",
            "success",
        )
    except exc.SQLAlchemyError as e:
        db.rollback()
        flash(f"Error adding task: {str(e)}", "danger")
    finally:
        db.close()
    return redirect(url_for("projects.project_detail", project_id=project_id))


@projects_bp.route("/projects/<int:project_id>/tasks/new", methods=["GET"])
def new_task_page(project_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            flash("Project not found.", "danger")
            return redirect(url_for("projects.list_projects"))
        return render_template(
            "tasks/create_task.html", project_id=project_id, project_name=project.name
        )
    finally:
        db.close()


@projects_bp.route(
    "/projects/<int:project_id>/tasks/<int:task_id>/edit", methods=["GET"]
)
def edit_task_page(project_id, task_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        task = (
            db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )
        if not project:
            flash("Project not found.", "danger")
            return redirect(url_for("projects.list_projects"))
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for("projects.project_detail", project_id=project_id))
        return render_template(
            "tasks/edit_task.html",
            project_id=project_id,
            project_name=project.name,
            task=task,
        )
    finally:
        db.close()


@projects_bp.route(
    "/projects/<int:project_id>/tasks/<int:task_id>/update", methods=["POST"]
)
def update_task(project_id, task_id):
    db = SessionLocal()
    try:
        task = (
            db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for("projects.project_detail", project_id=project_id))

        task_name = request.form.get("name")
        task_description = request.form.get("description")
        task_context = request.form.get("context")
        task_status = request.form.get("status")
        task_priority = request.form.get("priority")
        task_due_date_str = request.form.get("due_date")

        if not task_name:
            flash("Task name is required.", "warning")
            return redirect(
                url_for(
                    "projects.edit_task_page", project_id=project_id, task_id=task_id
                )
            )

        task.name = task_name
        task.description = task_description
        task.context = task_context
        task.status = task_status
        task.priority = task_priority

        if task_due_date_str:
            try:
                task.due_date = datetime.strptime(task_due_date_str, "%Y-%m-%d")
            except ValueError:
                flash(
                    f"Invalid due date format for task '{task_name}'. Please use YYYY-MM-DD.",
                    "warning",
                )
                return redirect(
                    url_for(
                        "projects.edit_task_page",
                        project_id=project_id,
                        task_id=task_id,
                    )
                )
        else:
            task.due_date = None

        db.commit()
        flash(f"Task '{task.name}' updated successfully.", "success")
    except exc.SQLAlchemyError as e:
        db.rollback()
        flash(f"Error updating task: {str(e)}", "danger")
    finally:
        db.close()
    return redirect(url_for("projects.project_detail", project_id=project_id))


@projects_bp.route(
    "/projects/<int:project_id>/tasks/<int:task_id>/delete", methods=["GET"]
)
def delete_task_page(project_id, task_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        task = (
            db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )
        if not project:
            flash("Project not found.", "danger")
            return redirect(url_for("projects.list_projects"))
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for("projects.project_detail", project_id=project_id))
        return render_template(
            "tasks/delete_task.html",
            project_id=project_id,
            project_name=project.name,
            task=task,
        )
    finally:
        db.close()


@projects_bp.route(
    "/projects/<int:project_id>/tasks/<int:task_id>/delete/confirm", methods=["POST"]
)
def delete_task_confirm(project_id, task_id):
    db = SessionLocal()
    try:
        task = (
            db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for("projects.project_detail", project_id=project_id))

        task_name = task.name  # Save for flash message
        db.delete(task)
        db.commit()
        flash(f"Task '{task_name}' has been permanently deleted.", "success")
    except exc.SQLAlchemyError as e:
        db.rollback()
        flash(f"Error deleting task: {str(e)}", "danger")
    finally:
        db.close()
    return redirect(url_for("projects.project_detail", project_id=project_id))


@projects_bp.route("/projects/<int:project_id>/tasks/reorder", methods=["POST"])
def reorder_tasks(project_id):
    db = SessionLocal()
    try:
        data = request.get_json()
        task_orders = data.get("taskOrders", [])  # List of {taskId: int, order: int}

        # Update each task's order
        for task_order in task_orders:
            task_id = task_order.get("taskId")
            new_order = task_order.get("order")
            if task_id is not None and new_order is not None:
                task = (
                    db.query(Task)
                    .filter(Task.id == task_id, Task.project_id == project_id)
                    .first()
                )
                if task:
                    task.sort_order = new_order

        db.commit()
        return {"status": "success"}, 200
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}, 500
    finally:
        db.close()


@projects_bp.route("/projects/<int:project_id>/tasks/<int:task_id>")
def task_detail(project_id, task_id):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        task = (
            db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )
        if not project:
            flash("Project not found.", "danger")
            return redirect(url_for("projects.list_projects"))
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for("projects.project_detail", project_id=project_id))

        # Convert markdown to HTML
        description_html = md_to_html(task.description)
        context_html = md_to_html(task.context)

        return render_template(
            "tasks/task_detail.html",
            task=task,
            project=project,
            description_html=description_html,
            context_html=context_html,
        )
    finally:
        db.close()


@projects_bp.route("/resources/<int:resource_id>", methods=["GET"])
def resource_detail(resource_id):
    db = SessionLocal()
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            flash("Resource not found.", "danger")
            return redirect(url_for("projects.list_projects"))
        return render_template("resources/resource_detail.html", resource=resource)
    finally:
        db.close()


@projects_bp.route("/resources/<int:resource_id>/update", methods=["POST"])
def update_resource(resource_id):
    db = SessionLocal()
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            flash("Resource not found.", "danger")
            return redirect(url_for("projects.list_projects"))
        resource.title = request.form.get("title")
        resource.url = request.form.get("url")
        resource.type = request.form.get("type")
        resource.notes = request.form.get("notes")
        resource.is_consumed = bool(request.form.get("is_consumed"))
        db.commit()
        flash("Resource updated successfully.", "success")
        return redirect(url_for("projects.task_detail", project_id=resource.task.project_id, task_id=resource.task.id))
    except exc.SQLAlchemyError as e:
        db.rollback()
        flash(f"Error updating resource: {str(e)}", "danger")
        return redirect(url_for("projects.resource_detail", resource_id=resource_id))
    finally:
        db.close()


@projects_bp.route("/projects/<int:project_id>/tasks/<int:task_id>/resources/new", methods=["GET"])
def new_resource_page(project_id, task_id):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for("projects.project_detail", project_id=project_id))
        return render_template("resources/create_resource.html", task=task, project_id=project_id)
    finally:
        db.close()


@projects_bp.route("/projects/<int:project_id>/tasks/<int:task_id>/resources/create", methods=["POST"])
def create_resource(project_id, task_id):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for("projects.project_detail", project_id=project_id))
        title = request.form.get("title")
        url_ = request.form.get("url")
        type_ = request.form.get("type")
        notes = request.form.get("notes")
        if not title or not url_ or not type_:
            flash("Title, URL, and Type are required.", "warning")
            return redirect(url_for("projects.new_resource_page", project_id=project_id, task_id=task_id))
        new_resource = Resource(
            title=title,
            url=url_,
            type=type_,
            notes=notes,
            is_consumed=False,
            task_id=task_id
        )
        db.add(new_resource)
        db.commit()
        flash("Resource added successfully.", "success")
        return redirect(url_for("projects.task_detail", project_id=project_id, task_id=task_id))
    except exc.SQLAlchemyError as e:
        db.rollback()
        flash(f"Error adding resource: {str(e)}", "danger")
        return redirect(url_for("projects.new_resource_page", project_id=project_id, task_id=task_id))
    finally:
        db.close()


@projects_bp.route("/resources/<int:resource_id>/delete", methods=["POST"])
def delete_resource(resource_id):
    db = SessionLocal()
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            flash("Resource not found.", "danger")
            return redirect(url_for("projects.list_projects"))
        project_id = resource.task.project_id
        task_id = resource.task.id
        db.delete(resource)
        db.commit()
        flash("Resource deleted successfully.", "success")
        return redirect(url_for("projects.task_detail", project_id=project_id, task_id=task_id))
    except exc.SQLAlchemyError as e:
        db.rollback()
        flash(f"Error deleting resource: {str(e)}", "danger")
        return redirect(url_for("projects.resource_detail", resource_id=resource_id))
    finally:
        db.close()
