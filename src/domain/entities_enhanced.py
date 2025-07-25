"""
Enhanced Domain Entities using Value Objects and Strong Typing

These entities represent the core business objects with improved validation,
type safety, and business logic encapsulation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from .value_objects import (
    InstanceId, VolumeId, SnapshotId, VolumeSize, SnapshotDescription,
    DeviceName, AWSRegion, InstanceState, SnapshotState, VolumeType
)
from .exceptions import (
    InstanceNotRunningError, SnapshotNotCompletedError, ValidationError
)


@dataclass(frozen=True)
class EC2Instance:
    """
    Represents an AWS EC2 Instance with strong typing and business logic.
    
    This is an immutable entity that encapsulates EC2 instance data and behavior.
    """
    instance_id: InstanceId
    name: str
    availability_zone: str
    state: InstanceState
    region: AWSRegion
    tags: dict[str, str] = field(default_factory=dict)
    
    @property
    def display_name(self) -> str:
        """Get a user-friendly display name for the instance."""
        return self.name if self.name and self.name != "No Name" else str(self.instance_id)
    
    @property
    def is_running(self) -> bool:
        """Check if the instance is in running state."""
        return self.state == InstanceState.RUNNING
    
    @property
    def is_terminated(self) -> bool:
        """Check if the instance is terminated."""
        return self.state == InstanceState.TERMINATED
    
    @property
    def can_create_snapshot(self) -> bool:
        """Check if snapshot creation is allowed for this instance."""
        return self.state in [InstanceState.RUNNING, InstanceState.STOPPED]
    
    def validate_snapshot_creation(self) -> None:
        """Validate that snapshot creation is allowed."""
        if not self.can_create_snapshot:
            raise InstanceNotRunningError(str(self.instance_id), self.state.value)
    
    def get_tag(self, key: str) -> Optional[str]:
        """Get a tag value by key."""
        return self.tags.get(key)
    
    def has_tag(self, key: str, value: Optional[str] = None) -> bool:
        """Check if instance has a specific tag."""
        if key not in self.tags:
            return False
        if value is None:
            return True
        return self.tags[key] == value


@dataclass(frozen=True)
class EBSVolume:
    """
    Represents an AWS EBS Volume with validation and business logic.
    
    Encapsulates volume properties and behavior related to snapshot operations.
    """
    volume_id: VolumeId
    device_name: DeviceName
    instance_id: InstanceId
    size: VolumeSize
    volume_type: VolumeType
    region: AWSRegion
    is_root: bool = False
    is_encrypted: bool = False
    tags: dict[str, str] = field(default_factory=dict)
    
    @property
    def is_attachable(self) -> bool:
        """Check if volume can be attached to instances."""
        return True  # All volumes are attachable unless in error state
    
    @property
    def supports_encryption(self) -> bool:
        """Check if volume type supports encryption."""
        return self.volume_type in [VolumeType.GP2, VolumeType.GP3, VolumeType.IO1, VolumeType.IO2]
    
    @property
    def is_high_performance(self) -> bool:
        """Check if this is a high-performance volume type."""
        return self.volume_type in [VolumeType.IO1, VolumeType.IO2, VolumeType.GP3]
    
    def estimate_snapshot_time(self) -> int:
        """Estimate snapshot creation time in minutes based on volume size."""
        # Rough estimation: larger volumes take longer
        base_time = 5  # Base time in minutes
        size_factor = max(1, self.size.gib // 100)  # Additional time per 100GB
        return base_time + size_factor
    
    def validate_encryption_requirements(self, require_encryption: bool = False) -> None:
        """Validate encryption requirements."""
        if require_encryption and not self.is_encrypted:
            raise ValidationError(f"Volume {self.volume_id} must be encrypted")


@dataclass(frozen=True)
class Snapshot:
    """
    Represents an AWS EBS Snapshot with state management and validation.
    
    Encapsulates snapshot properties and behavior for backup and restore operations.
    """
    snapshot_id: SnapshotId
    volume_id: VolumeId
    instance_id: InstanceId
    description: SnapshotDescription
    start_time: datetime
    state: SnapshotState
    progress: str
    size: VolumeSize
    region: AWSRegion
    is_encrypted: bool = False
    tags: dict[str, str] = field(default_factory=dict)
    
    @property
    def is_completed(self) -> bool:
        """Check if snapshot creation is completed."""
        return self.state == SnapshotState.COMPLETED
    
    @property
    def is_pending(self) -> bool:
        """Check if snapshot is still being created."""
        return self.state == SnapshotState.PENDING
    
    @property
    def has_error(self) -> bool:
        """Check if snapshot creation failed."""
        return self.state == SnapshotState.ERROR
    
    @property
    def completion_percentage(self) -> int:
        """Get completion percentage as integer."""
        try:
            # Progress is typically "100%" or "50%" format
            return int(self.progress.rstrip('%'))
        except (ValueError, AttributeError):
            return 0 if self.is_pending else 100
    
    @property
    def age_days(self) -> int:
        """Get age of snapshot in days."""
        return (datetime.utcnow() - self.start_time).days
    
    def validate_for_restore(self) -> None:
        """Validate that snapshot can be used for restore operations."""
        if not self.is_completed:
            raise SnapshotNotCompletedError(str(self.snapshot_id), self.state.value)
    
    def validate_for_deletion(self) -> None:
        """Validate that snapshot can be safely deleted."""
        # Add any business rules for deletion
        pass
    
    def is_older_than(self, days: int) -> bool:
        """Check if snapshot is older than specified days."""
        return self.age_days > days
    
    def get_display_name(self) -> str:
        """Get a user-friendly display name for the snapshot."""
        return f"{self.snapshot_id} ({self.description})"


@dataclass
class SnapshotRequest:
    """
    Represents a request to create a snapshot with validation.
    
    This is a mutable entity that represents a snapshot creation request.
    """
    instance_id: InstanceId
    instance_name: str
    description: Optional[SnapshotDescription] = None
    region: Optional[AWSRegion] = None
    tags: dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the request after initialization."""
        if not self.instance_name.strip():
            raise ValidationError("Instance name cannot be empty")
    
    @property
    def effective_description(self) -> SnapshotDescription:
        """Get the effective description for the snapshot."""
        if self.description:
            return self.description
        return SnapshotDescription(f"Automated snapshot for {self.instance_name}")
    
    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the request."""
        self.tags[key] = value
    
    def add_default_tags(self) -> None:
        """Add default tags for the snapshot."""
        self.add_tag("instance-id", str(self.instance_id))
        self.add_tag("instance-name", self.instance_name)
        self.add_tag("created-by", "ebs-snapshot-tool")
        self.add_tag("created-at", datetime.utcnow().isoformat())


__all__ = [
    "EC2Instance", 
    "EBSVolume", 
    "Snapshot", 
    "SnapshotRequest"
]
