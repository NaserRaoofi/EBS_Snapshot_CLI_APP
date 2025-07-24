from typing import List, Optional
from ..entities import EC2Instance, EBSVolume, Snapshot, SnapshotRequest
from ..repositories import EC2Repository, SnapshotRepository, VolumeRepository


class EC2Service:
    def __init__(self, ec2_repo: EC2Repository):
        self._ec2_repo = ec2_repo

    def list_running_instances(self, region: Optional[str] = None) -> List[EC2Instance]:
        return self._ec2_repo.list_running_instances(region)

    def get_instance_volumes(
        self, instance_id: str, region: Optional[str] = None
    ) -> List[EBSVolume]:
        return self._ec2_repo.get_instance_volumes(instance_id, region)

    def get_root_volume(
        self, instance_id: str, region: Optional[str] = None
    ) -> Optional[EBSVolume]:
        return self._ec2_repo.get_root_volume(instance_id, region)


class SnapshotService:
    def __init__(self, ec2_repo: EC2Repository, snapshot_repo: SnapshotRepository):
        self._ec2_repo = ec2_repo
        self._snapshot_repo = snapshot_repo

    def create_instance_snapshot(self, request: SnapshotRequest) -> Optional[str]:
        root_volume = self._ec2_repo.get_root_volume(
            request.instance_id, request.region
        )
        if not root_volume:
            return None

        description = (
            request.description or f"Automated snapshot for {request.instance_name}"
        )
        tags = {"instance-id": request.instance_id, "Name": request.instance_name}

        return self._snapshot_repo.create_snapshot(
            root_volume.volume_id, description, tags, request.region
        )

    def list_instance_snapshots(
        self, instance_id: str, region: Optional[str] = None
    ) -> List[Snapshot]:
        return self._snapshot_repo.list_snapshots(instance_id, region)

    def delete_snapshot(self, snapshot_id: str, region: Optional[str] = None) -> bool:
        return self._snapshot_repo.delete_snapshot(snapshot_id, region)

    def get_snapshot(
        self, snapshot_id: str, region: Optional[str] = None
    ) -> Optional[Snapshot]:
        return self._snapshot_repo.get_snapshot(snapshot_id, region)


class RestoreService:
    def __init__(
        self,
        ec2_repo: EC2Repository,
        snapshot_repo: SnapshotRepository,
        volume_repo: VolumeRepository,
    ):
        self._ec2_repo = ec2_repo
        self._snapshot_repo = snapshot_repo
        self._volume_repo = volume_repo

    def restore_instance_from_snapshot(
        self, instance_id: str, snapshot_id: str, region: Optional[str] = None
    ) -> bool:
        snapshot = self._snapshot_repo.get_snapshot(snapshot_id, region)
        if not snapshot or not snapshot.is_completed:
            return False

        instances = self._ec2_repo.list_running_instances(region)
        instance = next((i for i in instances if i.instance_id == instance_id), None)
        if not instance:
            return False

        current_root = self._ec2_repo.get_root_volume(instance_id, region)
        if not current_root:
            return False

        new_volume_id = self._volume_repo.create_volume_from_snapshot(
            snapshot_id, instance.availability_zone, region
        )
        if not new_volume_id:
            return False

        if not self._volume_repo.detach_volume(current_root.volume_id, region):
            return False

        if not self._volume_repo.attach_volume(
            new_volume_id, instance_id, current_root.device_name, region
        ):
            self._volume_repo.attach_volume(
                current_root.volume_id, instance_id, current_root.device_name, region
            )
            return False

        return True


__all__ = ["EC2Service", "SnapshotService", "RestoreService"]
