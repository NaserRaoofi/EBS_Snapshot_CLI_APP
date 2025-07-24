import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from .models import AppSettings, AWSConfigModel

load_dotenv()


@dataclass
class AWSConfig:
    region: Optional[str] = None
    profile: Optional[str] = None

    @classmethod
    def from_env(cls) -> "AWSConfig":
        return cls(region=os.getenv("AWS_REGION"), profile=os.getenv("AWS_PROFILE"))

    @classmethod
    def from_pydantic(cls, model: AWSConfigModel) -> "AWSConfig":
        return cls(region=model.region, profile=model.profile)


@dataclass
class AppConfig:
    aws: AWSConfig
    log_level: str = "INFO"
    log_file: str = "backup.log"

    @classmethod
    def load(cls) -> "AppConfig":
        settings = AppSettings()
        return cls(
            aws=AWSConfig.from_pydantic(settings.aws_config),
            log_level=settings.log_level,
            log_file=settings.log_file,
        )
