from typing import Any, Dict, List, Literal, Type

import instructor
import tiktoken
from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from config.llm_settings import get_settings

type LLMProviders = Literal["openai", "anthropic", "deepseek", "github_models", "llama"]


class LLMFactory:
    def __init__(self, provider: LLMProviders) -> None:
        self.provider: LLMProviders = provider
        self.settings = getattr(get_settings(), provider)
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        client_initializers = {
            "openai": lambda settings: instructor.from_openai(OpenAI(api_key=settings.api_key)),
            "github_models": lambda settings: instructor.from_openai(
                OpenAI(
                    api_key=settings.api_key,
                    base_url=settings.base_url,
                )
            ),
            "anthropic": lambda settings: instructor.from_anthropic(
                Anthropic(api_key=settings.api_key)
            ),
            "deepseek": lambda settings: instructor.from_openai(
                OpenAI(
                    api_key=settings.api_key,
                    base_url=settings.base_url,
                )
            ),
            "llama": lambda settings: instructor.from_openai(
                OpenAI(base_url=settings.base_url, api_key=settings.api_key),
                mode=instructor.Mode.JSON,
            ),
        }

        initializer = client_initializers.get(self.provider)
        if initializer:
            return initializer(self.settings)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def create_completion(
        self, response_model: Type[BaseModel], messages: List[Dict[str, str]], **kwargs
    ) -> Any:
        # Log token count before making the LLM call
        self._log_token_count(messages)
        model = kwargs.get("model", self.settings.default_model)
        completion_params = {
            "model": model,
            "temperature": kwargs.get("temperature", self.settings.temperature),
            "max_retries": kwargs.get("max_retries", self.settings.max_retries),
            "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
            "response_model": response_model,
            "messages": messages,
        }
        return self.client.chat.completions.create(**completion_params)

    def _log_token_count(self, messages: List[Dict[str, str]]):
        console = Console()
        try:

            enc = tiktoken.encoding_for_model("gpt-4-1106-preview")
            tokens_per_message = 3
            num_tokens = 0
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Role", style="cyan", no_wrap=True)
            table.add_column("Content", style="white")
            table.add_column("Tokens", style="green")
            for message in messages:
                role = message.get("role", "-")
                content = message.get("content", str(message))
                token_count = tokens_per_message
                for key, value in message.items():
                    token_count += len(enc.encode(value))
                num_tokens += token_count
                if role == "system":
                    # Syntax highlight HTML for system prompt
                    syntax = Syntax(content, "html", theme="dracula", word_wrap=True)
                    table.add_row(role, syntax, str(token_count))
                elif role == "user":
                    preview = content[:80] + ("..." if len(content) > 80 else "")
                    table.add_row(role, preview, str(token_count))
            num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
            panel = Panel(
                table,
                title=f"[tiktoken] Estimated input tokens: [bold yellow]{num_tokens}[/]",
                border_style="bright_blue",
                padding=(1, 2),
            )
            console.print(panel)
            return num_tokens
        except Exception as e:
            console.print(
                Panel(
                    f"Error counting tokens: {e}",
                    title="[red]Token Count Error",
                    border_style="red",
                )
            )
            return None
