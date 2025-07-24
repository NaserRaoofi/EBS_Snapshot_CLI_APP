from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class AWSConfigModel(BaseModel):
    region: Optional[str] = Field(None, description="AWS Region")
    profile: Optional[str] = Field(None, description="AWS Profile")

    @field_validator("region")
    @classmethod
    def validate_region(cls, v):
        if v and len(v) < 2:
            raise ValueError("AWS region must be at least 2 characters")
        return v


class AppSettings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    aws_region: Optional[str] = Field(None, json_schema_extra={"env": "AWS_REGION"})
    aws_profile: Optional[str] = Field(None, json_schema_extra={"env": "AWS_PROFILE"})
    log_level: str = Field("INFO", json_schema_extra={"env": "LOG_LEVEL"})
    log_file: str = Field("backup.log", json_schema_extra={"env": "LOG_FILE"})

    @property
    def aws_config(self) -> AWSConfigModel:
        return AWSConfigModel(region=self.aws_region, profile=self.aws_profile)


class CreateSnapshotRequestModel(BaseModel):
    instance_id: str = Field(..., min_length=10, description="EC2 Instance ID")
    instance_name: str = Field(..., min_length=1, description="Instance Name")
    description: Optional[str] = Field(
        None, max_length=255, description="Snapshot Description"
    )
    region: Optional[str] = Field(None, description="AWS Region")

    @field_validator("instance_id")
    @classmethod
    def validate_instance_id(cls, v):
        if not v.startswith("i-"):
            raise ValueError('Instance ID must start with "i-"')
        return v


class DeleteSnapshotRequestModel(BaseModel):
    snapshot_id: str = Field(..., min_length=12, description="Snapshot ID")
    region: Optional[str] = Field(None, description="AWS Region")

    @field_validator("snapshot_id")
    @classmethod
    def validate_snapshot_id(cls, v):
        if not v.startswith("snap-"):
            raise ValueError('Snapshot ID must start with "snap-"')
        return v


class RestoreSnapshotRequestModel(BaseModel):
    instance_id: str = Field(..., min_length=10, description="EC2 Instance ID")
    snapshot_id: str = Field(..., min_length=12, description="Snapshot ID")
    region: Optional[str] = Field(None, description="AWS Region")

    @field_validator("instance_id")
    @classmethod
    def validate_instance_id(cls, v):
        if not v.startswith("i-"):
            raise ValueError('Instance ID must start with "i-"')
        return v

    @field_validator("snapshot_id")
    @classmethod
    def validate_snapshot_id(cls, v):
        if not v.startswith("snap-"):
            raise ValueError('Snapshot ID must start with "snap-"')
        return v
