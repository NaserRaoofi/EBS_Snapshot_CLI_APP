from typing import Optional
from .base import BaseCommand
from .create_snapshot import CreateSnapshotCommand
from .list_snapshots import ListSnapshotsCommand
from .delete_snapshot import DeleteSnapshotCommand
from .restore_snapshot import RestoreSnapshotCommand
from ....infrastructure import Container


class CommandFactory:
    def __init__(self, container: Container):
        self._container = container

    def create_command(self, choice: int) -> Optional[BaseCommand]:
        commands = {
            1: CreateSnapshotCommand,
            2: ListSnapshotsCommand,
            3: DeleteSnapshotCommand,
            4: RestoreSnapshotCommand,
        }

        command_class = commands.get(choice)
        if command_class:
            return command_class(self._container)
        return None
