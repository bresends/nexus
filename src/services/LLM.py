from openai import OpenAI
from typing import Dict

class LLMService:
    def __init__(self, env_vars: Dict[str, str]):
        self.client = OpenAI(
            api_key=env_vars["LLM_API_KEY"],
            base_url=env_vars["LLM_BASE_URL"]
        )

    def get_response(self, query: str) -> str:
        response = self.client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        )

        return response.choices[0].message.content