from pydantic import BaseModel, Field
from services.llm_factory import LLMFactory
from prompts.prompt_manager import PromptManager


def main():

    class CompletionModel(BaseModel):
        reasoning: str = Field(description="Explain your reasoning for the response.")
        response: str = Field(description="Your response to the user.")

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user","content": "Hi there, I have a question about my bill. Can you help me?"},
    ]

    llm = LLMFactory("github_models")

    completion = llm.create_completion(
        response_model=CompletionModel,
        messages=messages,
    )
    assert isinstance(completion, CompletionModel)

    print(f"Reasoning: {completion.reasoning}")
    print(f"Response: {completion.response}\n")

    # Example of using the PromptManager
    example_prompt = PromptManager.get_prompt(
        "mneumonics", topic="Anterior e Posterior"
    )


if __name__ == "__main__":
    main()
