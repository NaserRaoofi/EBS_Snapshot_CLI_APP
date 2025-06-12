"""Functional CLI tests for backup and restore commands using Click."""
import pytest
from click.testing import CliRunner
import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_create_snapshot(runner, mocker):
    """Test CLI create-snapshot command (simulate menu selection)."""
    mock_create = mocker.patch('backup.create_snapshot', return_value='snap-123')
    mocker.patch('cli.save_instance_ids_to_env')
    mocker.patch('cli.list_ec2_instances', return_value=[{'InstanceId': 'vol-123', 'Name': 'Test'}])
    result = runner.invoke(cli.cli, input='1\n1\ndesc\n')
    assert result.exit_code == 0
    assert 'snap-123' in result.output
    mock_create.assert_called_once()

def test_cli_restore_snapshot(runner, mocker):
    """Test CLI restore-snapshot command (simulate menu selection)."""
    mock_restore = mocker.patch('restore.restore_snapshot_and_replace_root', return_value='vol-456')
    mocker.patch('cli.save_instance_ids_to_env')
    mocker.patch('cli.list_ec2_instances', return_value=[{'InstanceId': 'vol-123', 'Name': 'Test'}])
    result = runner.invoke(cli.cli, input='4\n')
    assert result.exit_code == 0
    assert 'vol-456' in result.output
    mock_restore.assert_called_once()
