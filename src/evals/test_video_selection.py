from dotenv import load_dotenv
from typing import List, Literal
from datetime import datetime

from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel, Field

from ..config.langfuse_settings import langFuseSettings
from ..services.llm_factory import LLMFactory
from ..database.database import SessionLocal
from ..models.video_evaluation_dataset import VideoEvaluationDataset

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
    """Load video evaluation data from database to Langfuse dataset."""
    langfuse.create_dataset(
        name="video_summaries",
        description="A dataset containing summaries of YouTube videos for comparison.",
        metadata={"author": "Bruno Resende", "date": "2025-05-31", "type": "benchmark"},
    )

    db = SessionLocal()
    try:
        video_eval_records = db.query(VideoEvaluationDataset).all()
        
        for record in video_eval_records:
            # Create metadata dictionary
            metadata = {
                "selected_video": record.selected_video,
                "model_used": record.model_used,
                "first_video_author": record.first_video_author,
                "second_video_author": record.second_video_author,
            }

            # Create input data
            input_data = {
                "user_background": record.user_background,
                "first_video_summary": record.first_video_summary,
                "second_video_summary": record.second_video_summary,
            }

            # Upload to Langfuse
            langfuse.create_dataset_item(
                id=f"video_summary_{record.id}",
                dataset_name="video_summaries",
                input=input_data,
                expected_output=record.expected_output,
                metadata=metadata,
            )
    finally:
        db.close()


# Example of how to use the new function (optional, can be removed or adapted)
if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Load the video summaries data into the dataset
    load_video_summaries_to_dataset()

    run_experiment(
        experiment_name=f"verify_production_{timestamp}",
        label="production",
    )
    run_experiment(
        experiment_name=f"verify_new_version_{timestamp}",
        label="latest",
    )
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
