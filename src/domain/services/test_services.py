import pytest
from unittest.mock import Mock
from ...domain.entities import EC2Instance, SnapshotRequest
from ...domain.repositories import EC2Repository, SnapshotRepository
from .. import EC2Service, SnapshotService


class TestEC2Service:
    def setup_method(self):
        self.mock_ec2_repo = Mock(spec=EC2Repository)
        self.service = EC2Service(self.mock_ec2_repo)

    def test_list_running_instances(self):
        expected_instances = [
            EC2Instance("i-123", "test1", "us-east-1a", "running"),
            EC2Instance("i-456", "test2", "us-east-1b", "running"),
        ]
        self.mock_ec2_repo.list_running_instances.return_value = expected_instances

        result = self.service.list_running_instances("us-east-1")

        assert result == expected_instances
        self.mock_ec2_repo.list_running_instances.assert_called_once_with("us-east-1")

    def test_get_root_volume(self):
        from ...domain.entities import EBSVolume

        expected_volume = EBSVolume("vol-123", "/dev/sda1", "i-123", 8, "gp3", True)
        self.mock_ec2_repo.get_root_volume.return_value = expected_volume

        result = self.service.get_root_volume("i-123", "us-east-1")

        assert result == expected_volume
        self.mock_ec2_repo.get_root_volume.assert_called_once_with("i-123", "us-east-1")


class TestSnapshotService:
    def setup_method(self):
        self.mock_ec2_repo = Mock(spec=EC2Repository)
        self.mock_snapshot_repo = Mock(spec=SnapshotRepository)
        self.service = SnapshotService(self.mock_ec2_repo, self.mock_snapshot_repo)

    def test_create_instance_snapshot_success(self):
        from ...domain.entities import EBSVolume

        root_volume = EBSVolume("vol-123", "/dev/sda1", "i-123", 8, "gp3", True)
        self.mock_ec2_repo.get_root_volume.return_value = root_volume
        self.mock_snapshot_repo.create_snapshot.return_value = "snap-123"

        request = SnapshotRequest(
            "i-123", "test-instance", "test snapshot", "us-east-1"
        )
        result = self.service.create_instance_snapshot(request)

        assert result == "snap-123"
        self.mock_ec2_repo.get_root_volume.assert_called_once_with("i-123", "us-east-1")
        self.mock_snapshot_repo.create_snapshot.assert_called_once()

    def test_create_instance_snapshot_no_root_volume(self):
        self.mock_ec2_repo.get_root_volume.return_value = None

        request = SnapshotRequest(
            "i-123", "test-instance", "test snapshot", "us-east-1"
        )
        result = self.service.create_instance_snapshot(request)

        assert result is None
        self.mock_snapshot_repo.create_snapshot.assert_not_called()

    def test_delete_snapshot(self):
        self.mock_snapshot_repo.delete_snapshot.return_value = True

        result = self.service.delete_snapshot("snap-123", "us-east-1")

        assert result is True
        self.mock_snapshot_repo.delete_snapshot.assert_called_once_with(
            "snap-123", "us-east-1"
        )
