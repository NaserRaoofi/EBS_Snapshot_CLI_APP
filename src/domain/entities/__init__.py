from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class EC2Instance:
    instance_id: str
    name: str
    availability_zone: str
    state: str

    @property
    def display_name(self) -> str:
        return self.name if self.name != "No Name" else self.instance_id


@dataclass(frozen=True)
class EBSVolume:
    volume_id: str
    device_name: str
    instance_id: str
    size: int
    volume_type: str
    is_root: bool = False


@dataclass(frozen=True)
class Snapshot:
    snapshot_id: str
    volume_id: str
    instance_id: str
    description: str
    start_time: datetime
    state: str
    progress: str
    size: int

    @property
    def is_completed(self) -> bool:
        return self.state == "completed"


@dataclass
class SnapshotRequest:
    instance_id: str
    instance_name: str
    description: Optional[str] = None
    region: Optional[str] = None


__all__ = ["EC2Instance", "EBSVolume", "Snapshot", "SnapshotRequest"]
