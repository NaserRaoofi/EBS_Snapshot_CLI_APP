"""Integration test for EC2 snapshot and volume using moto."""
import boto3
import pytest
from moto import mock_ec2
import os

@mock_ec2
def test_integration_snapshot_and_restore():
    """Integration test: create and restore EC2 snapshot using moto."""
    ec2 = boto3.resource('ec2', region_name='us-east-1')
    volume = ec2.create_volume(Size=8, AvailabilityZone='us-east-1a')
    snapshot = volume.create_snapshot(Description='test snap')
    assert snapshot.snapshot_id is not None
    new_volume = ec2.create_volume(SnapshotId=snapshot.snapshot_id, AvailabilityZone='us-east-1a')
    assert new_volume.volume_id is not None
