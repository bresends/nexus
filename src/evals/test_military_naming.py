from dotenv import load_dotenv


from typing import List, Literal

from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel, Field

from ..config.langfuse_settings import langFuseSettings
from ..services.llm_factory import LLMFactory
from datetime import datetime

load_dotenv()  # take environment variables

langfuse_client = Langfuse(
    public_key=langFuseSettings.public_key,
    secret_key=langFuseSettings.secret_key,
    host=langFuseSettings.host,
)

llm_factory = LLMFactory(provider="github_models")


@observe()
def get_chat_response(
    nome_guerra: str,
    texto: str,
    label: str,
) -> None:
    prompt = langfuse_client.get_prompt("youtube-video-compare", label=label)

    compiled_prompt = prompt.compile(
        nome_guerra=nome_guerra,
        texto=texto,
    )

    completion = llm_factory.create_completion(
        response_model=None,
        messages=compiled_prompt,
    )

    return completion


# we use a very simple eval here, you can use any eval library
# see https://langfuse.com/docs/scores/model-based-evals for details
# you can also use LLM-as-a-judge managed within Langfuse to evaluate the outputs
def simple_evaluation(output, expected_output):
    return output == expected_output


def run_experiment(experiment_name, label):
    dataset = langfuse_client.get_dataset("video_summaries")

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
            langfuse_client.score(
                trace_id=trace_id,
                name="exact_match",
                value=simple_evaluation(
                    output.selected_video, item.expected_output.get("selected_video")
                ),
            )


# Example of how to use the new function (optional, can be removed or adapted)
if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_experiment(
        experiment_name=f"verify_video_summaries_{timestamp}",
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
    langfuse_client.flush()
