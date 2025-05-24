from enum import Enum
from pydantic import BaseModel, Field
from services.llm_factory import LLMFactory
from prompts.prompt_manager import PromptManager
from database.database import SessionLocal
from models.project import Project
from sqlalchemy.orm import joinedload
from models.task import Task


class NewProjectInfoRelevance(str, Enum):
    NO_RELEVANCE = "no_relevance"
    WEAK_RELEVANCE = "weak_relevance"
    STRONG_RELEVANCE = "strong_relevance"


class NewProjectInfoAction(str, Enum):
    ADD_TO_PROJECT = "add_to_project"
    EXCLUDE = "exclude"

class Novelty(str, Enum):
    new = "new"
    redundant = "redundant"
    partially_redundant = "partially_redundant"


class NewInfoClassification(BaseModel):
    reasoning: str = Field(description="Explain your reasoning for the response.")
    relevance: NewProjectInfoRelevance
    related_resources: list[str] = Field(
        description="List the related resources from the project tasks that are related to the new information."
    )
    novelty_reasoning: str = Field(
        description="Explain your reasoning for the novelty classification."
    )
    novelty: Novelty = Field(
        description="Is the new information novel, redundant, or partially redundant agains the user project current task resources?"
    )
    action_reasoning: str = Field(description="Explain how you came to the conclusion.")
    action: NewProjectInfoAction = Field(
        description="What action should be taken with the new information?"
    )


class NewProjectInfoEvaluatorPipeline:
    """Pipeline for evaluating the relevance of new information to existing projects."""

    def __init__(self, llm_provider: str = "deepseek"):
        self.llm = LLMFactory(llm_provider)

    def get_project(self, project_id: int):
        """Fetch a single project and its tasks (with resources) from the database by ID."""
        db = SessionLocal()
        try:
            project = (
                db.query(Project)
                .options(joinedload(Project.tasks).joinedload(Task.resources))
                .filter(Project.id == project_id)
                .first()
            )
            if not project:
                raise ValueError(f"Project with id {project_id} not found.")
            return project  # Return the SQLAlchemy model instance directly
        finally:
            db.close()

    def evaluate_new_info(
        self,
        project_id: int,
        user_input: str,
    ) -> NewInfoClassification:
        project = self.get_project(project_id)

        # Display the project in a user-friendly format
        project_str = f"ID: {project.id} | Name: {project.name} | Status: {project.status} | {project.description} | "
        print(f"Project in the database:\n{project_str}")
        print("--" * 50)

        system_prompt = PromptManager.get_prompt(
            "evaluate_new_info_for_project", project=project
        )

        completion = self.llm.create_completion(
            response_model=NewInfoClassification,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )

        return completion
