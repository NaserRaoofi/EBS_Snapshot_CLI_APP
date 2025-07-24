from typing import Optional
from ..dtos import (
    CreateSnapshotRequest,
    CreateSnapshotResponse,
    ListSnapshotsRequest,
    ListSnapshotsResponse,
    SnapshotDTO,
    DeleteSnapshotRequest,
    DeleteSnapshotResponse,
    ListInstancesResponse,
    InstanceDTO,
    RestoreSnapshotRequest,
    RestoreSnapshotResponse,
)
from ...domain.services import SnapshotService, EC2Service, RestoreService
from ...domain.entities import SnapshotRequest


class CreateSnapshotUseCase:
    def __init__(self, snapshot_service: SnapshotService):
        self._snapshot_service = snapshot_service

    def execute(self, request: CreateSnapshotRequest) -> CreateSnapshotResponse:
        try:
            snapshot_request = SnapshotRequest(
                instance_id=request.instance_id,
                instance_name=request.instance_name,
                description=request.description,
                region=request.region,
            )

            snapshot_id = self._snapshot_service.create_instance_snapshot(
                snapshot_request
            )

            if snapshot_id:
                return CreateSnapshotResponse(
                    snapshot_id=snapshot_id,
                    success=True,
                    message=f"Snapshot created successfully: {snapshot_id}",
                )
            else:
                return CreateSnapshotResponse(
                    snapshot_id=None, success=False, message="Failed to create snapshot"
                )
        except Exception as e:
            return CreateSnapshotResponse(
                snapshot_id=None,
                success=False,
                message=f"Error creating snapshot: {str(e)}",
            )


class ListSnapshotsUseCase:
    def __init__(self, snapshot_service: SnapshotService):
        self._snapshot_service = snapshot_service

    def execute(self, request: ListSnapshotsRequest) -> ListSnapshotsResponse:
        try:
            snapshots = self._snapshot_service.list_instance_snapshots(
                request.instance_id, request.region
            )

            snapshot_dtos = [
                SnapshotDTO(
                    snapshot_id=s.snapshot_id,
                    volume_id=s.volume_id,
                    description=s.description,
                    start_time=s.start_time,
                    state=s.state,
                    progress=s.progress,
                    size=s.size,
                )
                for s in snapshots
            ]

            return ListSnapshotsResponse(
                snapshots=snapshot_dtos,
                success=True,
                message=f"Found {len(snapshot_dtos)} snapshots",
            )
        except Exception as e:
            return ListSnapshotsResponse(
                snapshots=[],
                success=False,
                message=f"Error listing snapshots: {str(e)}",
            )


class DeleteSnapshotUseCase:
    def __init__(self, snapshot_service: SnapshotService):
        self._snapshot_service = snapshot_service

    def execute(self, request: DeleteSnapshotRequest) -> DeleteSnapshotResponse:
        try:
            success = self._snapshot_service.delete_snapshot(
                request.snapshot_id, request.region
            )

            if success:
                return DeleteSnapshotResponse(
                    success=True,
                    message=f"Snapshot {request.snapshot_id} deleted successfully",
                )
            else:
                return DeleteSnapshotResponse(
                    success=False, message="Failed to delete snapshot"
                )
        except Exception as e:
            return DeleteSnapshotResponse(
                success=False, message=f"Error deleting snapshot: {str(e)}"
            )


class ListInstancesUseCase:
    def __init__(self, ec2_service: EC2Service):
        self._ec2_service = ec2_service

    def execute(self, region: Optional[str] = None) -> ListInstancesResponse:
        try:
            instances = self._ec2_service.list_running_instances(region)

            instance_dtos = [
                InstanceDTO(
                    instance_id=i.instance_id,
                    name=i.name,
                    availability_zone=i.availability_zone,
                    state=i.state,
                )
                for i in instances
            ]

            return ListInstancesResponse(
                instances=instance_dtos,
                success=True,
                message=f"Found {len(instance_dtos)} running instances",
            )
        except Exception as e:
            return ListInstancesResponse(
                instances=[],
                success=False,
                message=f"Error listing instances: {str(e)}",
            )


class RestoreSnapshotUseCase:
    def __init__(self, restore_service: RestoreService):
        self._restore_service = restore_service

    def execute(self, request: RestoreSnapshotRequest) -> RestoreSnapshotResponse:
        try:
            success = self._restore_service.restore_instance_from_snapshot(
                request.instance_id, request.snapshot_id, request.region
            )

            if success:
                return RestoreSnapshotResponse(
                    success=True, message="Instance restored successfully from snapshot"
                )
            else:
                return RestoreSnapshotResponse(
                    success=False, message="Failed to restore instance from snapshot"
                )
        except Exception as e:
            return RestoreSnapshotResponse(
                success=False, message=f"Error restoring snapshot: {str(e)}"
            )


__all__ = [
    "CreateSnapshotUseCase",
    "ListSnapshotsUseCase",
    "DeleteSnapshotUseCase",
    "ListInstancesUseCase",
    "RestoreSnapshotUseCase",
]
