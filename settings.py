from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    catalog_base_url: AnyHttpUrl = Field(
        validation_alias="CATALOG_BASE_URL"
    )
    payment_base_url: AnyHttpUrl = Field(
        validation_alias="PAYMENT_BASE_URL"
    )
    payment_callback_url: AnyHttpUrl = Field(
        validation_alias="PAYMENT_CALLBACK_URL"
    )
    api_token: SecretStr = Field(
        validation_alias="API_TOKEN"
    )

    database_url: str = Field(
        validation_alias="POSTGRES_CONNECTION_STRING"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
