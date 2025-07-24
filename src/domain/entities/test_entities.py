import pytest
from datetime import datetime
from ..entities import EC2Instance, EBSVolume, Snapshot, SnapshotRequest


class TestEC2Instance:
    def test_ec2_instance_creation(self):
        instance = EC2Instance(
            instance_id="i-1234567890abcdef0",
            name="test-instance",
            availability_zone="us-east-1a",
            state="running",
        )

        assert instance.instance_id == "i-1234567890abcdef0"
        assert instance.name == "test-instance"
        assert instance.availability_zone == "us-east-1a"
        assert instance.state == "running"

    def test_display_name_with_name(self):
        instance = EC2Instance(
            instance_id="i-1234567890abcdef0",
            name="test-instance",
            availability_zone="us-east-1a",
            state="running",
        )

        assert instance.display_name == "test-instance"

    def test_display_name_without_name(self):
        instance = EC2Instance(
            instance_id="i-1234567890abcdef0",
            name="No Name",
            availability_zone="us-east-1a",
            state="running",
        )

        assert instance.display_name == "i-1234567890abcdef0"


class TestEBSVolume:
    def test_ebs_volume_creation(self):
        volume = EBSVolume(
            volume_id="vol-1234567890abcdef0",
            device_name="/dev/sda1",
            instance_id="i-1234567890abcdef0",
            size=8,
            volume_type="gp3",
            is_root=True,
        )

        assert volume.volume_id == "vol-1234567890abcdef0"
        assert volume.device_name == "/dev/sda1"
        assert volume.instance_id == "i-1234567890abcdef0"
        assert volume.size == 8
        assert volume.volume_type == "gp3"
        assert volume.is_root is True


class TestSnapshot:
    def test_snapshot_creation(self):
        start_time = datetime.now()
        snapshot = Snapshot(
            snapshot_id="snap-1234567890abcdef0",
            volume_id="vol-1234567890abcdef0",
            instance_id="i-1234567890abcdef0",
            description="test snapshot",
            start_time=start_time,
            state="completed",
            progress="100%",
            size=8,
        )

        assert snapshot.snapshot_id == "snap-1234567890abcdef0"
        assert snapshot.volume_id == "vol-1234567890abcdef0"
        assert snapshot.instance_id == "i-1234567890abcdef0"
        assert snapshot.description == "test snapshot"
        assert snapshot.start_time == start_time
        assert snapshot.state == "completed"
        assert snapshot.progress == "100%"
        assert snapshot.size == 8

    def test_is_completed_true(self):
        snapshot = Snapshot(
            snapshot_id="snap-1234567890abcdef0",
            volume_id="vol-1234567890abcdef0",
            instance_id="i-1234567890abcdef0",
            description="test snapshot",
            start_time=datetime.now(),
            state="completed",
            progress="100%",
            size=8,
        )

        assert snapshot.is_completed is True

    def test_is_completed_false(self):
        snapshot = Snapshot(
            snapshot_id="snap-1234567890abcdef0",
            volume_id="vol-1234567890abcdef0",
            instance_id="i-1234567890abcdef0",
            description="test snapshot",
            start_time=datetime.now(),
            state="pending",
            progress="50%",
            size=8,
        )

        assert snapshot.is_completed is False


class TestSnapshotRequest:
    def test_snapshot_request_creation(self):
        request = SnapshotRequest(
            instance_id="i-1234567890abcdef0",
            instance_name="test-instance",
            description="test description",
            region="us-east-1",
        )

        assert request.instance_id == "i-1234567890abcdef0"
        assert request.instance_name == "test-instance"
        assert request.description == "test description"
        assert request.region == "us-east-1"

    def test_snapshot_request_optional_fields(self):
        request = SnapshotRequest(
            instance_id="i-1234567890abcdef0", instance_name="test-instance"
        )

        assert request.instance_id == "i-1234567890abcdef0"
        assert request.instance_name == "test-instance"
        assert request.description is None
        assert request.region is None
