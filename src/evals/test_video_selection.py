from dotenv import load_dotenv
import csv
import os
import json


from typing import List, Literal

from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel, Field

from ..config.langfuse_settings import langFuseSettings
from ..services.llm_factory import LLMFactory
from datetime import datetime

load_dotenv()  # take environment variables

langfuse = Langfuse(
    public_key=langFuseSettings.public_key,
    secret_key=langFuseSettings.secret_key,
    host=langFuseSettings.host,
)


llm_factory = LLMFactory(provider="github_models")


class VideoComparisonResponse(BaseModel):
    detailed_analysis: str = Field(
        description="A comprehensive analysis of the similarities and differences between the two video summaries.",
    )
    reasoning: str = Field(
        description="A detailed explanation of the reasoning that led to the similarity score.",
    )
    first_video_unique_points: List[str] = Field(
        description="A list of key points or features that are unique to the first video if any.",
    )
    second_video_unique_points: List[str] = Field(
        description="A list of key points or features that are unique to the second video if any.",
    )
    similarity_score: float = Field(
        ge=0,
        le=1,
        description="A score from 0 to 1 indicating how similar the two videos are.",
    )
    recommendation: str = Field(
        description="A recommendation on whether the user should watch both videos or just one, with justification.",
    )
    selected_video: Literal["first_video", "second_video", "both"] = Field(
        description="Indicates which video(s) the user should watch."
    )


@observe()
def get_chat_response(
    user_background: str,
    first_video_summary: str,
    second_video_summary: str,
    label: str,
) -> VideoComparisonResponse:
    prompt = langfuse.get_prompt("youtube-video-compare", label=label)

    compiled_prompt = prompt.compile(
        user_background=user_background,
        first_video_summary=first_video_summary,
        second_video_summary=second_video_summary,
    )

    completion = llm_factory.create_completion(
        response_model=VideoComparisonResponse,
        messages=compiled_prompt,
    )

    return completion


# we use a very simple eval here, you can use any eval library
# see https://langfuse.com/docs/scores/model-based-evals for details
# you can also use LLM-as-a-judge managed within Langfuse to evaluate the outputs
def simple_evaluation(output, expected_output):
    return output == expected_output


def run_experiment(experiment_name, label):
    dataset = langfuse.get_dataset("video_summaries")

    for item in dataset.items:
        # item.observe() returns a trace_id that can be used to add custom evaluations later
        # it also automatically links the trace to the experiment run
        with item.observe(run_name=experiment_name) as trace_id:
            # run application, pass input and system prompt
            output = get_chat_response(
                user_background=item.input.get("user_background"),
                first_video_summary=item.input.get("first_video_summary"),
                second_video_summary=item.input.get("second_video_summary"),
                label=label,
            )

            # optional: add custom evaluation results to the experiment trace
            # we use the previously created example evaluation function
            # Assuming item.expected_output is a string and should be compared against the detailed_analysis.
            # If item.expected_output is structured or another field is more appropriate, this may need adjustment.
            langfuse.score(
                trace_id=trace_id,
                name="exact_match",
                value=simple_evaluation(
                    output.selected_video, item.expected_output.get("selected_video")
                ),
            )


def load_video_summaries_to_dataset():
    langfuse.create_dataset(
        name="video_summaries",
        description="A dataset containing summaries of YouTube videos for comparison.",
        metadata={"author": "Bruno Resende", "date": "2025-05-31", "type": "benchmark"},
    )

    csv_path = os.path.join(
        os.path.dirname(__file__), "datasets", "video_summaries.csv"
    )

    with open(csv_path, "r", encoding="latin-1") as file:
        csv_reader = csv.DictReader(file)
        for idx, row in enumerate(csv_reader, 1):
            # Convert the metadata string to a dictionary if it exists
            try:
                metadata = json.loads(row.get("metadata"))
            except json.JSONDecodeError:
                print(
                    f"Warning: Could not parse metadata for row {idx}, using empty dict"
                )
                metadata = {}

            # Add the selected video to the metadata
            metadata["selected_video"] = row["selected_video"]

            # Create input and expected output dictionaries
            input_data = {
                "user_background": row["user_background"],
                "first_video_summary": row["first_video_summary"],
                "second_video_summary": row["second_video_summary"],
            }

            try:
                expected_output = json.loads(row.get("output"))
            except json.JSONDecodeError:
                print(
                    f"Warning: Could not parse expected_output for row {idx}, using empty dict"
                )
                expected_output = {}

            # Upload to Langfuse
            langfuse.create_dataset_item(
                id=f"video_summary_{idx}",
                dataset_name="video_summaries",
                input=input_data,
                expected_output=expected_output,
                metadata=metadata,
            )


# Example of how to use the new function (optional, can be removed or adapted)
if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Load the video summaries data into the dataset
    load_video_summaries_to_dataset()

    run_experiment(
        experiment_name=f"verify_video_summaries_{timestamp}",
        label="production",
    )
    # run_experiment(
    #     experiment_name=f"verify_new_version_{timestamp}",
    #     label="latest",
    # )
    # run_experiment(
    #     experiment_name="asking_specifically",
    #     label="The user will input countries, respond with only the name of the capital",
    # )
    # run_experiment(
    #     experiment_name="asking_specifically_2nd_try",
    #     label="The user will input countries, respond with only the name of the capital. State only the name of the city.",
    # )

    # Assert that all events were sent to the Langfuse API
    langfuse_context.flush()
    langfuse.flush()
