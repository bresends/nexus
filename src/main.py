import json
from pipelines.pkm.new_info_evaluator import NewInfoEvaluatorPipeline


def main():
    # Create the pipeline
    pipeline = NewInfoEvaluatorPipeline()

    
    result = pipeline.evaluate_new_info(
        user_input="I want to start gardening. What do you think?",
    )

    # Print the result
    print(json.dumps(result.model_dump(), indent=4))


if __name__ == "__main__":
    main()
