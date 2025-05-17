import json
from pipelines.pkm.new_info_evaluator import NewInfoEvaluatorPipeline


def main():
    # Create the pipeline
    pipeline = NewInfoEvaluatorPipeline()

    # Get the projects
    projects = pipeline.get_projects()
    print("Available projects:")
    for project in projects:
        print(f"- {project['name']}: {project['description']}")

    print("\nEvaluating new information...")
    # Evaluate new information
    result = pipeline.evaluate_new_info(
        user_input="I want to start gardening. What do you think?",
    )

    # Print the result
    print(json.dumps(result.model_dump(), indent=4))


if __name__ == "__main__":
    main()
