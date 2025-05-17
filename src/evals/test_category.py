import json
import os
from pydantic import BaseModel, Field
from services.llm_factory import LLMFactory
from enum import Enum
from prompts.prompt_manager import PromptManager



def test_eval():
    class Sentiment(str, Enum):
        positive = "positive"
        neutral = "neutral"
        negative = "negative"

    class Classification(BaseModel):
        sentiment: Sentiment = Field(
            description="The sentiment classification: positive, neutral, or negative."
        )
        reasoning: str = Field(description="Explain your reasoning for the response.")
        response: str = Field(description="Your response to the user.")
        confidence: float = Field(
            description="Your confidence in the classification, from 0 to 1."
        )

    dataset_path = os.path.join(
        os.path.dirname(__file__), "datasets", "sentiment_analysis.json"
    )

    with open(dataset_path, "r") as f:
        data = json.load(f)["data"]

    llm = LLMFactory("github_models")

    for entry in data:
        # Example of using the PromptManager
        prompt = PromptManager.get_prompt(
        "categorization", ticket=entry["text"]
        )

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": entry["text"]},
        ]
        completion = llm.create_completion(
            response_model=Classification,
            messages=messages,
        )
        assert isinstance(completion, Classification)
        assert completion.sentiment.value == entry["label"]
        assert abs(completion.confidence - entry["confidence"]) < 0.15
