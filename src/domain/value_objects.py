"""
Domain Value Objects for AWS EBS Snapshot Management

Value objects are immutable objects that are defined by their attributes rather than identity.
They encapsulate domain concepts and provide validation and behavior.
"""

from dataclasses import dataclass
from typing import ClassVar
import re
from enum import Enum


class AWSRegion(str, Enum):
    """AWS Regions enum for type safety and validation."""
    US_EAST_1 = "us-east-1"
    US_EAST_2 = "us-east-2" 
    US_WEST_1 = "us-west-1"
    US_WEST_2 = "us-west-2"
    EU_WEST_1 = "eu-west-1"
    EU_WEST_2 = "eu-west-2"
    EU_CENTRAL_1 = "eu-central-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"
    AP_SOUTHEAST_2 = "ap-southeast-2"
    AP_NORTHEAST_1 = "ap-northeast-1"

    @classmethod
    def from_string(cls, region: str) -> "AWSRegion":
        """Create AWSRegion from string with validation."""
        try:
            return cls(region)
        except ValueError:
            raise ValueError(f"Invalid AWS region: {region}")


class InstanceState(str, Enum):
    """EC2 Instance states."""
    PENDING = "pending"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting-down"
    TERMINATED = "terminated"
    STOPPING = "stopping"
    STOPPED = "stopped"


class SnapshotState(str, Enum):
    """EBS Snapshot states."""
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"


class VolumeType(str, Enum):
    """EBS Volume types."""
    GP2 = "gp2"
    GP3 = "gp3"
    IO1 = "io1"
    IO2 = "io2"
    ST1 = "st1"
    SC1 = "sc1"
    STANDARD = "standard"


@dataclass(frozen=True)
class InstanceId:
    """Value object for EC2 Instance ID with validation."""
    
    value: str
    _PATTERN: ClassVar[str] = r"^i-[0-9a-f]{8,17}$"
    
    def __post_init__(self):
        if not re.match(self._PATTERN, self.value):
            raise ValueError(f"Invalid EC2 Instance ID format: {self.value}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class VolumeId:
    """Value object for EBS Volume ID with validation."""
    
    value: str
    _PATTERN: ClassVar[str] = r"^vol-[0-9a-f]{8,17}$"
    
    def __post_init__(self):
        if not re.match(self._PATTERN, self.value):
            raise ValueError(f"Invalid EBS Volume ID format: {self.value}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True) 
class SnapshotId:
    """Value object for EBS Snapshot ID with validation."""
    
    value: str
    _PATTERN: ClassVar[str] = r"^snap-[0-9a-f]{8,17}$"
    
    def __post_init__(self):
        if not re.match(self._PATTERN, self.value):
            raise ValueError(f"Invalid EBS Snapshot ID format: {self.value}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class VolumeSize:
    """Value object for EBS Volume size with validation."""
    
    gib: int  # Size in GiB
    
    def __post_init__(self):
        if self.gib < 1:
            raise ValueError("Volume size must be at least 1 GiB")
        if self.gib > 64000:  # AWS EBS limit
            raise ValueError("Volume size cannot exceed 64,000 GiB")
    
    @property
    def bytes(self) -> int:
        """Size in bytes."""
        return self.gib * 1024 * 1024 * 1024
    
    @property
    def mb(self) -> int:
        """Size in MB."""
        return self.gib * 1024
    
    def __str__(self) -> str:
        return f"{self.gib} GiB"


@dataclass(frozen=True)
class SnapshotDescription:
    """Value object for snapshot description with validation."""
    
    value: str
    MAX_LENGTH: ClassVar[int] = 255
    
    def __post_init__(self):
        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"Description cannot exceed {self.MAX_LENGTH} characters")
        if not self.value.strip():
            raise ValueError("Description cannot be empty")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class DeviceName:
    """Value object for device name with validation."""
    
    value: str
    _VALID_PATTERNS: ClassVar[list] = [
        r"^/dev/sd[a-z]$",      # /dev/sda, /dev/sdb, etc.
        r"^/dev/xvd[a-z]$",     # /dev/xvda, /dev/xvdb, etc.
        r"^/dev/nvme\d+n\d+$"   # /dev/nvme0n1, etc.
    ]
    
    def __post_init__(self):
        if not any(re.match(pattern, self.value) for pattern in self._VALID_PATTERNS):
            raise ValueError(f"Invalid device name format: {self.value}")
    
    def __str__(self) -> str:
        return self.value
