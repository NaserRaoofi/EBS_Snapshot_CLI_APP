"""Unit tests for create_snapshot in backup.py."""
import unittest
from unittest.mock import patch, MagicMock
from backup import create_snapshot

class TestCreateSnapshot(unittest.TestCase):
    """Unit test for create_snapshot function."""
    @patch('backup.boto3.client')
    def test_create_snapshot_success(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.create_snapshot.return_value = {'SnapshotId': 'snap-123'}
        result = create_snapshot('vol-123', 'desc')
        assert result == 'snap-123'
        ec2_mock.create_snapshot.assert_called_once_with(VolumeId='vol-123', Description='desc')

    @patch('backup.boto3.client')
    def test_create_snapshot_failure(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.create_snapshot.side_effect = Exception('error')
        try:
            create_snapshot('vol-123', 'desc')
        except Exception as e:
            assert str(e) == 'error'

if __name__ == '__main__':
    unittest.main()
