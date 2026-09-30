from pathlib import Path
from urllib.parse import quote

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        frozen=True,
        extra="ignore",
    )

    country_code: str = Field(min_length=2, max_length=2)
    region_code: str = Field(min_length=1)
    source_endpoint: str = Field(min_length=1)

    db_name: str = Field(min_length=1)
    db_user: str = Field(min_length=1)
    db_password: str
    db_host: str = Field(min_length=1)
    db_port: int = Field(ge=1, le=65535)

    output_path: Path

    @field_validator("country_code", mode="before")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip().upper()

        return value

    @field_validator("region_code", mode="before")
    @classmethod
    def normalize_region(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip().upper()

        return value

    @field_validator("country_code")
    @classmethod
    def validate_country(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError(
                "COUNTRY_CODE must contain two letters"
            )

        return value

    @property
    def database_url(self) -> str:
        user = quote(self.db_user, safe="")
        password = quote(self.db_password, safe="")

        return (
            f"postgresql://{user}:{password}"
            f"@{self.db_host}:{self.db_port}"
            f"/{self.db_name}"
        )


def load_settings() -> Settings:
    return Settings()