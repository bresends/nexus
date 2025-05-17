from enum import Enum
from pydantic import BaseModel, Field
from services.llm_factory import LLMFactory
from prompts.prompt_manager import PromptManager
from typing import List, Dict


class NewInfoRelevance(str, Enum):
    NO_RELEVANCE = "no_relevance"
    WEAK_RELEVANCE = "weak_relevance"
    STRONG_RELEVANCE = "strong_relevance"

class NewInfoAction(str, Enum):
    ADD_TO_PROJECT = "add_to_project"
    EXCLUDE = "exclude"


class NewInfoClassification(BaseModel):
    reasoning: str = Field(description="Explain your reasoning for the response.")
    relevance: NewInfoRelevance
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Your confidence score for the relevance classification between 0 and 1.",
    )
    confidence_explanation: str = Field(description="Explain your confidence score.")
    action: NewInfoAction = Field(description="What action should be taken with the new information?")


class NewInfoEvaluatorPipeline:
    """Pipeline for evaluating the relevance of new information to existing projects."""

    def __init__(self, llm_provider: str = "github_models"):
        self.llm = LLMFactory(llm_provider)

    def get_projects(self) -> List[Dict[str, str]]:
        SAMPLE_PROJECTS = [
            {
                "name": "AI Research",
                "description": "Researching new AI models and their applications.",
            },
            {
                "name": "Personal Finance",
                "description": "Tracking and optimizing personal expenses and investments.",
            },
            {
                "name": "Fitness Goals",
                "description": "Improving health through regular exercise and nutrition.",
            },
        ]
        return SAMPLE_PROJECTS

    def evaluate_new_info(
        self,
        user_input: str,
    ) -> NewInfoClassification:
        projects = self.get_projects()

        system_prompt = PromptManager.get_prompt("evaluate_new_info", projects=projects)

        completion = self.llm.create_completion(
            response_model=NewInfoClassification,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )

        return completion
