from typing import List, Literal

from langfuse import Langfuse
from langfuse.decorators import observe
from pydantic import BaseModel, Field

from ..config.langfuse_settings import langFuseSettings
from ..services.llm_factory import LLMFactory

langfuse = Langfuse(
    public_key=langFuseSettings.public_key,
    secret_key=langFuseSettings.secret_key,
    host=langFuseSettings.host,
)

llm_factory = LLMFactory(provider="github_models")


class VideoComparisonResponse(BaseModel):
    detailed_analysis: str = Field(
        ...,
        description="A comprehensive analysis of the similarities and differences between the two video summaries.",
    )
    confidence_score: int = Field(
        ...,
        ge=0,
        le=1,
        description="A score from 0 to 1 indicating how similar the two videos are.",
    )
    reasoning: str = Field(
        ...,
        description="A detailed explanation of the reasoning that led to the similarity score.",
    )
    first_video_unique_points: List[str] = Field(
        default_factory=list,
        description="A list of key points or features that are unique to the first video if any.",
    )
    second_video_unique_points: List[str] = Field(
        default_factory=list,
        description="A list of key points or features that are unique to the second video if any.",
    )
    recommendation: str = Field(
        ...,
        description="A recommendation on whether the user should watch both videos or just one, with justification.",
    )
    selected_video: Literal["first_video", "second_video", "both"] = Field(
        ..., description="Indicates which video(s) the user should watch."
    )


@observe()
def get_chat_response(input_data: str, system_prompt: str) -> VideoComparisonResponse:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_data},
    ]

    completion = llm_factory.create_completion(
        response_model=VideoComparisonResponse,
        messages=messages,
    )

    return completion


# we use a very simple eval here, you can use any eval library
# see https://langfuse.com/docs/scores/model-based-evals for details
# you can also use LLM-as-a-judge managed within Langfuse to evaluate the outputs
def simple_evaluation(output, expected_output):
    return output == expected_output


def run_experiment(experiment_name, system_prompt):
    dataset = langfuse.get_dataset("video_summaries")

    for item in dataset.items:
        # item.observe() returns a trace_id that can be used to add custom evaluations later
        # it also automatically links the trace to the experiment run
        with item.observe(run_name=experiment_name) as trace_id:
            # run application, pass input and system prompt
            output = get_chat_response(item.input, system_prompt)

            # optional: add custom evaluation results to the experiment trace
            # we use the previously created example evaluation function
            # Assuming item.expected_output is a string and should be compared against the detailed_analysis.
            # If item.expected_output is structured or another field is more appropriate, this may need adjustment.
            langfuse.score(
                trace_id=trace_id,
                name="exact_match",
                value=simple_evaluation(output.selected_video, item.expected_output),
            )


# Example of how to use the new function (optional, can be removed or adapted)
if __name__ == "__main__":

    prompt = langfuse.get_prompt("youtube-video-compare", label="production")

    print(f"Using prompt: {prompt}")

    # run_experiment(
    #     experiment_name="famous_city",
    #     system_prompt="The user will input countries, respond with the most famous city in this country",
    # )
    # run_experiment(
    #     experiment_name="directly_ask",
    #     system_prompt="What is the capital of the following country?",
    # )
    # run_experiment(
    #     experiment_name="asking_specifically",
    #     system_prompt="The user will input countries, respond with only the name of the capital",
    # )
    # run_experiment(
    #     experiment_name="asking_specifically_2nd_try",
    #     system_prompt="The user will input countries, respond with only the name of the capital. State only the name of the city.",
    # )

    # # Assert that all events were sent to the Langfuse API
    # langfuse_context.flush()
    # langfuse.flush()
