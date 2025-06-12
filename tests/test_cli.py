"""Functional CLI tests for backup and restore commands using Click."""
import pytest
from click.testing import CliRunner
import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_create_snapshot(runner, mocker):
    """Test CLI create-snapshot command."""
    mock_create = mocker.patch('backup.create_snapshot', return_value='snap-123')
    result = runner.invoke(cli.cli, ['create-snapshot', '--volume-id', 'vol-123', '--description', 'desc'])
    assert result.exit_code == 0
    assert 'snap-123' in result.output
    mock_create.assert_called_once_with('vol-123', 'desc')

def test_cli_restore_snapshot(runner, mocker):
    """Test CLI restore-snapshot command."""
    mock_restore = mocker.patch('restore.restore_snapshot', return_value='vol-456')
    result = runner.invoke(cli.cli, ['restore-snapshot', '--snapshot-id', 'snap-123', '--az', 'us-east-1a'])
    assert result.exit_code == 0
    assert 'vol-456' in result.output
    mock_restore.assert_called_once_with('snap-123', 'us-east-1a')
