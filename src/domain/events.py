"""
Domain Events for AWS EBS Snapshot Management

Domain events represent important business events that other parts of the system
might need to react to. They enable loose coupling and event-driven architecture.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from .value_objects import InstanceId, VolumeId, SnapshotId, AWSRegion


class DomainEvent(ABC):
    """Base class for all domain events."""
    
    def __init__(self):
        self.occurred_at = datetime.utcnow()
        self.event_id = self._generate_event_id()
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """Return the type of the event."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        pass
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        import uuid
        return str(uuid.uuid4())


@dataclass
class SnapshotCreationRequested(DomainEvent):
    """Raised when a snapshot creation is requested."""
    
    instance_id: InstanceId
    volume_id: VolumeId
    description: str
    region: AWSRegion
    tags: Dict[str, str] = field(default_factory=dict)
    
    @property
    def event_type(self) -> str:
        return "SnapshotCreationRequested"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "instance_id": str(self.instance_id),
            "volume_id": str(self.volume_id),
            "description": self.description,
            "region": self.region.value,
            "tags": self.tags
        }


@dataclass
class SnapshotCreationStarted(DomainEvent):
    """Raised when snapshot creation has started in AWS."""
    
    snapshot_id: SnapshotId
    volume_id: VolumeId
    instance_id: InstanceId
    region: AWSRegion
    
    @property
    def event_type(self) -> str:
        return "SnapshotCreationStarted"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "snapshot_id": str(self.snapshot_id),
            "volume_id": str(self.volume_id),
            "instance_id": str(self.instance_id),
            "region": self.region.value
        }


@dataclass
class SnapshotCreationCompleted(DomainEvent):
    """Raised when snapshot creation is completed."""
    
    snapshot_id: SnapshotId
    volume_id: VolumeId
    instance_id: InstanceId
    size_gb: int
    duration_minutes: float
    region: AWSRegion
    
    @property
    def event_type(self) -> str:
        return "SnapshotCreationCompleted"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "snapshot_id": str(self.snapshot_id),
            "volume_id": str(self.volume_id),
            "instance_id": str(self.instance_id),
            "size_gb": self.size_gb,
            "duration_minutes": self.duration_minutes,
            "region": self.region.value
        }


@dataclass
class SnapshotCreationFailed(DomainEvent):
    """Raised when snapshot creation fails."""
    
    volume_id: VolumeId
    instance_id: InstanceId
    error_message: str
    error_code: Optional[str]
    region: AWSRegion
    
    @property
    def event_type(self) -> str:
        return "SnapshotCreationFailed"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "volume_id": str(self.volume_id),
            "instance_id": str(self.instance_id),
            "error_message": self.error_message,
            "error_code": self.error_code,
            "region": self.region.value
        }


@dataclass
class SnapshotDeleted(DomainEvent):
    """Raised when a snapshot is deleted."""
    
    snapshot_id: SnapshotId
    volume_id: VolumeId
    instance_id: InstanceId
    region: AWSRegion
    deleted_by: str
    
    @property
    def event_type(self) -> str:
        return "SnapshotDeleted"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "snapshot_id": str(self.snapshot_id),
            "volume_id": str(self.volume_id),
            "instance_id": str(self.instance_id),
            "region": self.region.value,
            "deleted_by": self.deleted_by
        }


@dataclass
class SnapshotRestoreRequested(DomainEvent):
    """Raised when a snapshot restore is requested."""
    
    snapshot_id: SnapshotId
    target_instance_id: InstanceId
    region: AWSRegion
    requested_by: str
    
    @property
    def event_type(self) -> str:
        return "SnapshotRestoreRequested"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "snapshot_id": str(self.snapshot_id),
            "target_instance_id": str(self.target_instance_id),
            "region": self.region.value,
            "requested_by": self.requested_by
        }


@dataclass
class SnapshotRestoreCompleted(DomainEvent):
    """Raised when snapshot restore is completed."""
    
    snapshot_id: SnapshotId
    new_volume_id: VolumeId
    target_instance_id: InstanceId
    region: AWSRegion
    duration_minutes: float
    
    @property
    def event_type(self) -> str:
        return "SnapshotRestoreCompleted"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "snapshot_id": str(self.snapshot_id),
            "new_volume_id": str(self.new_volume_id),
            "target_instance_id": str(self.target_instance_id),
            "region": self.region.value,
            "duration_minutes": self.duration_minutes
        }


@dataclass
class QuotaLimitApproached(DomainEvent):
    """Raised when approaching AWS service quotas."""
    
    quota_type: str
    current_usage: int
    quota_limit: int
    threshold_percentage: float
    region: AWSRegion
    
    @property
    def event_type(self) -> str:
        return "QuotaLimitApproached"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "quota_type": self.quota_type,
            "current_usage": self.current_usage,
            "quota_limit": self.quota_limit,
            "threshold_percentage": self.threshold_percentage,
            "region": self.region.value
        }


# Event Publisher Interface
class DomainEventPublisher(ABC):
    """Interface for publishing domain events."""
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        pass
    
    @abstractmethod
    def publish_many(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""
        pass


__all__ = [
    "DomainEvent",
    "SnapshotCreationRequested",
    "SnapshotCreationStarted", 
    "SnapshotCreationCompleted",
    "SnapshotCreationFailed",
    "SnapshotDeleted",
    "SnapshotRestoreRequested",
    "SnapshotRestoreCompleted",
    "QuotaLimitApproached",
    "DomainEventPublisher"
]
