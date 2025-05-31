import pathlib

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

root_dir = pathlib.Path(__file__).resolve().parent.parent.parent

env_file_path = root_dir / ".env"

class LangFuseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file_path, env_file_encoding="utf-8", extra="ignore")
    public_key: str = Field(validation_alias="LANGFUSE_PUBLIC_KEY")
    secret_key: str = Field(validation_alias="LANGFUSE_SECRET_KEY")
    host: str = Field(validation_alias="LANGFUSE_HOST")

langFuseSettings = LangFuseSettings()