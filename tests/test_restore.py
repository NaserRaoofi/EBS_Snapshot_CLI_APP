"""Unit tests for restore_snapshot in restore.py."""
import unittest
from unittest.mock import patch, MagicMock
from restore import restore_snapshot

class TestRestoreSnapshot(unittest.TestCase):
    """Unit test for restore_snapshot function."""
    @patch('restore.boto3.client')
    def test_restore_snapshot_success(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.create_volume.return_value = {'VolumeId': 'vol-456'}
        result = restore_snapshot('snap-123', 'us-east-1a')
        assert result == 'vol-456'
        ec2_mock.create_volume.assert_called_once_with(SnapshotId='snap-123', AvailabilityZone='us-east-1a')

    @patch('restore.boto3.client')
    def test_restore_snapshot_failure(self, mock_boto_client):
        ec2_mock = MagicMock()
        mock_boto_client.return_value = ec2_mock
        ec2_mock.create_volume.side_effect = Exception('fail')
        try:
            restore_snapshot('snap-123', 'us-east-1a')
        except Exception as e:
            assert str(e) == 'fail'

if __name__ == '__main__':
    unittest.main()
