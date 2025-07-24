from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class CreateSnapshotRequest:
    instance_id: str
    instance_name: str
    description: Optional[str] = None
    region: Optional[str] = None


@dataclass
class CreateSnapshotResponse:
    snapshot_id: Optional[str]
    success: bool
    message: str


@dataclass
class ListSnapshotsRequest:
    instance_id: str
    region: Optional[str] = None


@dataclass
class SnapshotDTO:
    snapshot_id: str
    volume_id: str
    description: str
    start_time: datetime
    state: str
    progress: str
    size: int


@dataclass
class ListSnapshotsResponse:
    snapshots: List[SnapshotDTO]
    success: bool
    message: str


@dataclass
class DeleteSnapshotRequest:
    snapshot_id: str
    region: Optional[str] = None


@dataclass
class DeleteSnapshotResponse:
    success: bool
    message: str


@dataclass
class InstanceDTO:
    instance_id: str
    name: str
    availability_zone: str
    state: str


@dataclass
class ListInstancesResponse:
    instances: List[InstanceDTO]
    success: bool
    message: str


@dataclass
class RestoreSnapshotRequest:
    instance_id: str
    snapshot_id: str
    region: Optional[str] = None


@dataclass
class RestoreSnapshotResponse:
    success: bool
    message: str
