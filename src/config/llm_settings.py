from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class LLMProviderSettings(BaseSettings):
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    max_retries: int = 3


class GithubOpenAISettings(LLMProviderSettings):
    api_key: str = Field(validation_alias="GITHUB_MODELS_API_KEY")
    default_model: str = "openai/gpt-4.1-mini"
    base_url: str = "https://models.github.ai/inference"


class DeepSeekSettings(LLMProviderSettings):
    api_key: str = Field(validation_alias="DEEPSEEK_API_KEY")
    default_model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"


class OpenAISettings(LLMProviderSettings):
    api_key: str = Field(validation_alias="OPENAI_API_KEY")
    default_model: str = "gpt-4o"


class AnthropicSettings(LLMProviderSettings):
    api_key: str = Field(validation_alias="ANTHROPIC_API_KEY")
    default_model: str = "claude-3-5-sonnet-20240620"
    max_tokens: Optional[int] = 1024


class LlamaSettings(LLMProviderSettings):
    api_key: str = "key"  # required, but not used
    default_model: str = "llama3"
    base_url: str = "http://localhost:11434/v1"


class Settings(BaseSettings):
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    llama: LlamaSettings = Field(default_factory=LlamaSettings)
    github_models: GithubOpenAISettings = Field(default_factory=GithubOpenAISettings)
    deepseek: DeepSeekSettings = Field(default_factory=DeepSeekSettings)


@lru_cache
def get_settings() -> Settings:
    return Settings()
