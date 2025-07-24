from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities import EC2Instance, EBSVolume, Snapshot


class EC2Repository(ABC):
    @abstractmethod
    def list_running_instances(self, region: Optional[str] = None) -> List[EC2Instance]:
        pass

    @abstractmethod
    def get_instance_volumes(
        self, instance_id: str, region: Optional[str] = None
    ) -> List[EBSVolume]:
        pass

    @abstractmethod
    def get_root_volume(
        self, instance_id: str, region: Optional[str] = None
    ) -> Optional[EBSVolume]:
        pass


class SnapshotRepository(ABC):
    @abstractmethod
    def create_snapshot(
        self, volume_id: str, description: str, tags: dict, region: Optional[str] = None
    ) -> Optional[str]:
        pass

    @abstractmethod
    def list_snapshots(
        self, instance_id: str, region: Optional[str] = None
    ) -> List[Snapshot]:
        pass

    @abstractmethod
    def delete_snapshot(self, snapshot_id: str, region: Optional[str] = None) -> bool:
        pass

    @abstractmethod
    def get_snapshot(
        self, snapshot_id: str, region: Optional[str] = None
    ) -> Optional[Snapshot]:
        pass


class VolumeRepository(ABC):
    @abstractmethod
    def create_volume_from_snapshot(
        self, snapshot_id: str, availability_zone: str, region: Optional[str] = None
    ) -> Optional[str]:
        pass

    @abstractmethod
    def attach_volume(
        self,
        volume_id: str,
        instance_id: str,
        device: str,
        region: Optional[str] = None,
    ) -> bool:
        pass

    @abstractmethod
    def detach_volume(self, volume_id: str, region: Optional[str] = None) -> bool:
        pass
