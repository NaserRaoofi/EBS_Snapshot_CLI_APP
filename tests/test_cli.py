"""Functional CLI tests for backup and restore commands using Click."""
import os
import pytest
from click.testing import CliRunner
import cli

# Set a region so AWS SDK doesn’t complain
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_create_snapshot(runner, mocker):
    """Test CLI create-snapshot command (simulate menu selection)."""
    # Patch all required dependencies
    mock_create = mocker.patch('cli.create_snapshot', return_value='snap-123')
    mocker.patch('cli.save_instance_ids_to_env')
    mocker.patch('cli.list_ec2_instances', return_value=[{'InstanceId': 'vol-123', 'Name': 'Test'}])
    mock_logger = mocker.patch('cli.logger')

    # Simulate user input: [1. Take snapshot, 1. Choose instance, 'desc']
    result = runner.invoke(cli.cli, input='1\n1\ndesc\n')

    assert result.exit_code == 0
    assert any('snap-123' in str(call) for call in mock_logger.info.call_args_list)
    mock_create.assert_called_once()

def test_cli_restore_snapshot(runner, mocker):
    """Test CLI restore-snapshot command (simulate menu selection)."""
    mock_restore = mocker.patch('cli.restore_snapshot_and_replace_root', return_value='vol-456')
    mocker.patch('cli.save_instance_ids_to_env')
    mocker.patch('cli.list_ec2_instances', return_value=[{'InstanceId': 'vol-123', 'Name': 'Test'}])
    mock_logger = mocker.patch('cli.logger')

    # Simulate user choosing option 4 (restore)
    result = runner.invoke(cli.cli, input='4\n')

    assert result.exit_code == 0
    assert any('vol-456' in str(call) for call in mock_logger.info.call_args_list)
    mock_restore.assert_called_once()
