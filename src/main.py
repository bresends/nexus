from config.env import load_environment_variables
from services.LLM import LLMService

def main():
    env_vars = load_environment_variables()

    llm_service = LLMService(env_vars)

    query = "Explain to me how AI works"
    response = llm_service.get_response(query)

    print(response)


if __name__ == "__main__":
    main()
