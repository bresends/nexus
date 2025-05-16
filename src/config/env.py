from dotenv import load_dotenv
import os
from typing import Dict

def load_environment_variables() -> Dict[str, str]:
    """
    Load and validate required environment variables.
    Returns a dictionary of validated environment variables.
    Raises ValueError if any required variables are missing.
    """
    load_dotenv()  # Load environment variables from .env file

    # Define required environment variables
    required_vars = [
        "LLM_API_KEY",
        "LLM_BASE_URL"
    ]

    env_vars = {}
    missing_vars = []

    # Check for required environment variables
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            env_vars[var] = value

    # Raise error if any required variables are missing
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return env_vars