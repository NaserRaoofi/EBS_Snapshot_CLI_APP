"""Unit tests for create_snapshot in backup.py."""
import unittest
from unittest.mock import patch, MagicMock, ANY
from backup import create_snapshot, get_root_volume_id, list_snapshots, delete_snapshot, list_ec2_instances

class TestCreateSnapshot(unittest.TestCase):
    """Unit test for create_snapshot function."""
    @patch('backup.boto3.client')
    def test_create_snapshot_success(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.create_snapshot.return_value = {'SnapshotId': 'snap-123'}
        result = create_snapshot('vol-123', 'desc')
        assert result == 'snap-123'
        ec2_mock.create_snapshot.assert_called_once_with(
            VolumeId=ANY,
            Description='Automated snapshot',
            TagSpecifications=[
                {
                    'ResourceType': 'snapshot',
                    'Tags': [
                        {'Key': 'instance-id', 'Value': 'vol-123'},
                        {'Key': 'Name', 'Value': 'desc'}
                    ]
                }
            ]
        )

    @patch('backup.boto3.client')
    def test_create_snapshot_failure(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.create_snapshot.side_effect = Exception('error')
        try:
            create_snapshot('vol-123', 'desc')
        except Exception as e:
            assert str(e) == 'error'

class TestBackupFunctions(unittest.TestCase):
    """Unit tests for other backup functions."""

    @patch('backup.boto3.client')
    def test_get_root_volume_id_success(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.describe_instances.return_value = {
            'Reservations': [{
                'Instances': [{
                    'BlockDeviceMappings': [{
                        'Ebs': {'VolumeId': 'vol-abc'}
                    }]
                }]
            }]
        }
        result = get_root_volume_id('i-123')
        assert result == 'vol-abc'
        ec2_mock.describe_instances.assert_called_once_with(InstanceIds=['i-123'])

    @patch('backup.boto3.client')
    def test_get_root_volume_id_failure(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.describe_instances.side_effect = Exception('fail')
        result = get_root_volume_id('i-123')
        assert result is None

    @patch('backup.boto3.client')
    def test_list_snapshots_success(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.describe_snapshots.return_value = {
            'Snapshots': [
                {'SnapshotId': 'snap-1', 'StartTime': 2},
                {'SnapshotId': 'snap-2', 'StartTime': 1}
            ]
        }
        result = list_snapshots('i-123')
        assert [s['SnapshotId'] for s in result] == ['snap-1', 'snap-2']
        ec2_mock.describe_snapshots.assert_called_once()

    @patch('backup.boto3.client')
    def test_list_snapshots_failure(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.describe_snapshots.side_effect = Exception('fail')
        result = list_snapshots('i-123')
        assert result == []

    @patch('backup.boto3.client')
    def test_delete_snapshot_success(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.delete_snapshot.return_value = None
        result = delete_snapshot('snap-123')
        assert result is True
        ec2_mock.delete_snapshot.assert_called_once_with(SnapshotId='snap-123')

    @patch('backup.boto3.client')
    def test_delete_snapshot_failure(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.delete_snapshot.side_effect = Exception('fail')
        result = delete_snapshot('snap-123')
        assert result is False

    @patch('backup.boto3.client')
    def test_list_ec2_instances_success(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.describe_instances.return_value = {
            'Reservations': [
                {'Instances': [
                    {'InstanceId': 'i-1', 'Tags': [{'Key': 'Name', 'Value': 'Test'}], 'Placement': {'AvailabilityZone': 'us-east-1a'}},
                    {'InstanceId': 'i-2', 'Tags': [], 'Placement': {'AvailabilityZone': 'us-east-1b'}}
                ]}
            ]
        }
        result = list_ec2_instances()
        assert result == [
            {'InstanceId': 'i-1', 'Name': 'Test', 'AZ': 'us-east-1a'},
            {'InstanceId': 'i-2', 'Name': 'No Name', 'AZ': 'us-east-1b'}
        ]
        ec2_mock.describe_instances.assert_called_once()

    @patch('backup.boto3.client')
    def test_list_ec2_instances_failure(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.describe_instances.side_effect = Exception('fail')
        result = list_ec2_instances()
        assert result == []

if __name__ == '__main__':
    unittest.main()
