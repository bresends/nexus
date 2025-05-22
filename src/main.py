from rich.console import Console
from rich.syntax import Syntax
from pipelines.pkm.new_info_for_project_evaluator import NewProjectInfoEvaluatorPipeline
from database.database import SessionLocal
from models.project import Project


def main():
    # List all projects and let the user select one
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        if not projects:
            print("No projects found in the database.")
            return
        print("Available Projects:")
        for project in projects:
            print(f"  [{project.id}] {project.name} (Status: {project.status})")
        project_id = None
        while project_id is None:
            try:
                user_input_id = input("Enter the ID of the project you want to use: ")
                project_id = int(user_input_id)
                if not any(p.id == project_id for p in projects):
                    print("Invalid project ID. Please try again.")
                    project_id = None
            except ValueError:
                print("Please enter a valid integer project ID.")
    finally:
        db.close()

    pipeline = NewProjectInfoEvaluatorPipeline()

    # Read user input from input.txt in the root folder
    input_file_path = "input.txt"
    try:
        with open(input_file_path, "r", encoding="utf-8") as f:
            user_input = f.read().strip()
    except FileNotFoundError:
        print(
            f"File '{input_file_path}' not found. Please create it in the root folder."
        )
        return

    result = pipeline.evaluate_new_info(
        project_id=project_id,
        user_input=user_input,
    )

    # Print the result with monokai theme and word wrap
    console = Console()
    json_str = result.model_dump_json(indent=4)
    syntax = Syntax(
        json_str, "json", theme="monokai", line_numbers=False, word_wrap=True
    )
    console.print(syntax)


if __name__ == "__main__":
    main()
