from typing import Union, Tuple
from pydantic import ValidationError
from ..application.dtos import (
    CreateSnapshotRequest,
    DeleteSnapshotRequest,
    RestoreSnapshotRequest,
)
from ..infrastructure.config.models import (
    CreateSnapshotRequestModel,
    DeleteSnapshotRequestModel,
    RestoreSnapshotRequestModel,
)


class ValidationService:
    @staticmethod
    def validate_create_snapshot_request(
        request: CreateSnapshotRequest,
    ) -> Tuple[bool, Union[CreateSnapshotRequest, str]]:
        try:
            validated_model = CreateSnapshotRequestModel(
                instance_id=request.instance_id,
                instance_name=request.instance_name,
                description=request.description,
                region=request.region,
            )

            return True, CreateSnapshotRequest(
                instance_id=validated_model.instance_id,
                instance_name=validated_model.instance_name,
                description=validated_model.description,
                region=validated_model.region,
            )
        except ValidationError as e:
            return False, str(e)

    @staticmethod
    def validate_delete_snapshot_request(
        request: DeleteSnapshotRequest,
    ) -> Tuple[bool, Union[DeleteSnapshotRequest, str]]:
        try:
            validated_model = DeleteSnapshotRequestModel(
                snapshot_id=request.snapshot_id, region=request.region
            )

            return True, DeleteSnapshotRequest(
                snapshot_id=validated_model.snapshot_id, region=validated_model.region
            )
        except ValidationError as e:
            return False, str(e)

    @staticmethod
    def validate_restore_snapshot_request(
        request: RestoreSnapshotRequest,
    ) -> Tuple[bool, Union[RestoreSnapshotRequest, str]]:
        try:
            validated_model = RestoreSnapshotRequestModel(
                instance_id=request.instance_id,
                snapshot_id=request.snapshot_id,
                region=request.region,
            )

            return True, RestoreSnapshotRequest(
                instance_id=validated_model.instance_id,
                snapshot_id=validated_model.snapshot_id,
                region=validated_model.region,
            )
        except ValidationError as e:
            return False, str(e)
