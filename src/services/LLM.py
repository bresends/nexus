from openai import OpenAI
from typing import Dict
import json
class LLMService:
    def __init__(self, env_vars: Dict[str, str]):
        self.client = OpenAI(
            api_key=env_vars["LLM_API_KEY"],
            base_url=env_vars["LLM_BASE_URL"]
        )

    def get_response(self, query: str) -> str:
        response = self.client.chat.completions.create(
            model="openai/gpt-4.1-mini",
            messages=[
                {"role": "system", "content": """
                You are a helpful customer care assistant that classify incomming messages and create a reply.
                Always respond in the following JSON format {"content": <response>, "category": <classification>}.
                Available categories are: 'general', 'order', 'billing'
                Return the JSON object only, no other text or comments. Don't use markdown. Only valid JSON is accepted.
                """
                },
                {"role": "user", "content": query}
            ]
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")