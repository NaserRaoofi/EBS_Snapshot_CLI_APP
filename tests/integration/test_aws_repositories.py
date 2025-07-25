import pytest
from unittest.mock import Mock, patch
from src.domain.entities import EC2Instance, EBSVolume, Snapshot
from src.domain.repositories import EC2Repository, SnapshotRepository, VolumeRepository
from src.infrastructure.aws import AWSEC2Repository, AWSSnapshotRepository, AWSVolumeRepository


class TestAWSEC2Repository:
    def setup_method(self):
        self.repository = AWSEC2Repository(default_region="us-east-1")

    @patch("boto3.client")
    def test_list_running_instances_success(self, mock_boto_client):
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        mock_client.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "State": {"Name": "running"},
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "Tags": [{"Key": "Name", "Value": "test-instance"}],
                        }
                    ]
                }
            ]
        }

        instances = self.repository.list_running_instances()

        assert len(instances) == 1
        assert instances[0].instance_id == "i-1234567890abcdef0"
        assert instances[0].name == "test-instance"
        assert instances[0].availability_zone == "us-east-1a"
        assert instances[0].state == "running"

    @patch("boto3.client")
    def test_list_running_instances_no_name_tag(self, mock_boto_client):
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        mock_client.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "State": {"Name": "running"},
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "Tags": [],
                        }
                    ]
                }
            ]
        }

        instances = self.repository.list_running_instances()

        assert len(instances) == 1
        assert instances[0].name == "No Name"

    @patch("boto3.client")
    def test_get_root_volume_success(self, mock_boto_client):
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        mock_client.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "RootDeviceName": "/dev/sda1",
                            "BlockDeviceMappings": [
                                {
                                    "DeviceName": "/dev/sda1",
                                    "Ebs": {"VolumeId": "vol-1234567890abcdef0"},
                                }
                            ],
                        }
                    ]
                }
            ]
        }

        mock_client.describe_volumes.return_value = {
            "Volumes": [{"Size": 8, "VolumeType": "gp3"}]
        }

        volume = self.repository.get_root_volume("i-1234567890abcdef0")

        assert volume is not None
        assert volume.volume_id == "vol-1234567890abcdef0"
        assert volume.is_root is True


class TestAWSSnapshotRepository:
    def setup_method(self):
        self.repository = AWSSnapshotRepository(default_region="us-east-1")

    @patch("boto3.client")
    def test_create_snapshot_success(self, mock_boto_client):
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        mock_client.create_snapshot.return_value = {
            "SnapshotId": "snap-1234567890abcdef0"
        }

        snapshot_id = self.repository.create_snapshot(
            "vol-1234567890abcdef0",
            "test description",
            {"instance-id": "i-1234567890abcdef0", "Name": "test-instance"},
        )

        assert snapshot_id == "snap-1234567890abcdef0"
        mock_client.create_snapshot.assert_called_once()

    @patch("boto3.client")
    def test_delete_snapshot_success(self, mock_boto_client):
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        result = self.repository.delete_snapshot("snap-1234567890abcdef0")

        assert result is True
        mock_client.delete_snapshot.assert_called_once_with(
            SnapshotId="snap-1234567890abcdef0"
        )


class TestAWSVolumeRepository:
    def setup_method(self):
        self.repository = AWSVolumeRepository(default_region="us-east-1")

    @patch("boto3.client")
    def test_create_volume_from_snapshot_success(self, mock_boto_client):
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        mock_client.create_volume.return_value = {"VolumeId": "vol-new1234567890abcdef"}

        volume_id = self.repository.create_volume_from_snapshot(
            "snap-1234567890abcdef0", "us-east-1a"
        )

        assert volume_id == "vol-new1234567890abcdef"
        mock_client.create_volume.assert_called_once_with(
            SnapshotId="snap-1234567890abcdef0", AvailabilityZone="us-east-1a"
        )

    @patch("boto3.client")
    def test_attach_volume_success(self, mock_boto_client):
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        result = self.repository.attach_volume(
            "vol-1234567890abcdef0", "i-1234567890abcdef0", "/dev/sda1"
        )

        assert result is True
        mock_client.attach_volume.assert_called_once_with(
            VolumeId="vol-1234567890abcdef0",
            InstanceId="i-1234567890abcdef0",
            Device="/dev/sda1",
        )
