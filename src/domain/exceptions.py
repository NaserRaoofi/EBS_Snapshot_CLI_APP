"""
Domain Exceptions for AWS EBS Snapshot Management

Domain exceptions represent business rule violations and domain-specific error conditions.
They should be meaningful to business stakeholders and help enforce domain invariants.
"""

from typing import Optional


class DomainError(Exception):
    """Base class for all domain errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class ValidationError(DomainError):
    """Raised when domain validation rules are violated."""
    pass


class BusinessRuleViolationError(DomainError):
    """Raised when business rules are violated."""
    pass


# EC2 Instance related exceptions
class InstanceNotFoundError(DomainError):
    """Raised when an EC2 instance cannot be found."""
    
    def __init__(self, instance_id: str):
        super().__init__(
            f"EC2 instance not found: {instance_id}",
            error_code="INSTANCE_NOT_FOUND"
        )
        self.instance_id = instance_id


class InstanceNotRunningError(BusinessRuleViolationError):
    """Raised when trying to perform operations on a non-running instance."""
    
    def __init__(self, instance_id: str, current_state: str):
        super().__init__(
            f"Instance {instance_id} is not running (current state: {current_state})",
            error_code="INSTANCE_NOT_RUNNING"
        )
        self.instance_id = instance_id
        self.current_state = current_state


class InstanceHasNoVolumesError(BusinessRuleViolationError):
    """Raised when an instance has no attached volumes."""
    
    def __init__(self, instance_id: str):
        super().__init__(
            f"Instance {instance_id} has no attached volumes",
            error_code="NO_VOLUMES_ATTACHED"
        )
        self.instance_id = instance_id


# Volume related exceptions
class VolumeNotFoundError(DomainError):
    """Raised when an EBS volume cannot be found."""
    
    def __init__(self, volume_id: str):
        super().__init__(
            f"EBS volume not found: {volume_id}",
            error_code="VOLUME_NOT_FOUND"
        )
        self.volume_id = volume_id


class VolumeNotAttachedError(BusinessRuleViolationError):
    """Raised when trying to snapshot a volume that's not attached."""
    
    def __init__(self, volume_id: str):
        super().__init__(
            f"Volume {volume_id} is not attached to any instance",
            error_code="VOLUME_NOT_ATTACHED"
        )
        self.volume_id = volume_id


# Snapshot related exceptions
class SnapshotNotFoundError(DomainError):
    """Raised when a snapshot cannot be found."""
    
    def __init__(self, snapshot_id: str):
        super().__init__(
            f"EBS snapshot not found: {snapshot_id}",
            error_code="SNAPSHOT_NOT_FOUND"
        )
        self.snapshot_id = snapshot_id


class SnapshotNotCompletedError(BusinessRuleViolationError):
    """Raised when trying to use an incomplete snapshot."""
    
    def __init__(self, snapshot_id: str, current_state: str):
        super().__init__(
            f"Snapshot {snapshot_id} is not completed (current state: {current_state})",
            error_code="SNAPSHOT_NOT_COMPLETED"
        )
        self.snapshot_id = snapshot_id
        self.current_state = current_state


class SnapshotInProgressError(BusinessRuleViolationError):
    """Raised when trying to delete a snapshot that's still in progress."""
    
    def __init__(self, snapshot_id: str):
        super().__init__(
            f"Cannot delete snapshot {snapshot_id} while creation is in progress",
            error_code="SNAPSHOT_IN_PROGRESS"
        )
        self.snapshot_id = snapshot_id


class ConcurrentSnapshotLimitExceededError(BusinessRuleViolationError):
    """Raised when the concurrent snapshot limit is exceeded."""
    
    def __init__(self, current_count: int, limit: int):
        super().__init__(
            f"Concurrent snapshot limit exceeded: {current_count}/{limit}",
            error_code="CONCURRENT_SNAPSHOT_LIMIT"
        )
        self.current_count = current_count
        self.limit = limit


# Region related exceptions
class InvalidRegionError(ValidationError):
    """Raised when an invalid AWS region is specified."""
    
    def __init__(self, region: str):
        super().__init__(
            f"Invalid AWS region: {region}",
            error_code="INVALID_REGION"
        )
        self.region = region


class CrossRegionOperationError(BusinessRuleViolationError):
    """Raised when trying to perform cross-region operations that aren't allowed."""
    
    def __init__(self, operation: str, source_region: str, target_region: str):
        super().__init__(
            f"Cross-region {operation} not allowed from {source_region} to {target_region}",
            error_code="CROSS_REGION_NOT_ALLOWED"
        )
        self.operation = operation
        self.source_region = source_region
        self.target_region = target_region


# Permission related exceptions
class InsufficientPermissionsError(DomainError):
    """Raised when the user lacks necessary permissions."""
    
    def __init__(self, operation: str, resource: str):
        super().__init__(
            f"Insufficient permissions to {operation} on {resource}",
            error_code="INSUFFICIENT_PERMISSIONS"
        )
        self.operation = operation
        self.resource = resource


# Quota related exceptions
class QuotaExceededError(BusinessRuleViolationError):
    """Raised when AWS quotas are exceeded."""
    
    def __init__(self, quota_type: str, current: int, limit: int):
        super().__init__(
            f"{quota_type} quota exceeded: {current}/{limit}",
            error_code="QUOTA_EXCEEDED"
        )
        self.quota_type = quota_type
        self.current = current
        self.limit = limit
