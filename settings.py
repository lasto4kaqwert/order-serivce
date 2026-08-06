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
    notification_base_url: AnyHttpUrl = Field(
        validation_alias="NOTIFICATION_BASE_URL"
    )
    api_token: SecretStr = Field(
        validation_alias="API_TOKEN"
    )

    database_url: str = Field(
        validation_alias="POSTGRES_CONNECTION_STRING"
    )

    kafka_bootstrap_servers: str = Field(
        validation_alias="KAFKA_BOOTSTRAP_SERVERS"
    )
    kafka_order_events_topic: str = Field(
        validation_alias="KAFKA_ORDER_EVENTS_TOPIC"
    )
    kafka_shipment_events_topic: str = Field(
        validation_alias="KAFKA_SHIPMENT_EVENTS_TOPIC"
    )
    kafka_consumer_group: str = Field(
        validation_alias="KAFKA_CONSUMER_GROUP"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
