from rich.console import Console
from rich.syntax import Syntax
from pipelines.pkm.new_info_evaluator import NewInfoEvaluatorPipeline


def main():
    # Create the pipeline
    pipeline = NewInfoEvaluatorPipeline()

    result = pipeline.evaluate_new_info(
        user_input="I want to start gardening. What do you think?",
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
