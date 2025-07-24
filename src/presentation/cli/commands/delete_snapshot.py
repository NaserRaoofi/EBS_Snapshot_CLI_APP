import click
from typing import List
from .base import BaseCommand
from ....domain.entities import EC2Instance
from ....application.dtos import ListSnapshotsRequest, DeleteSnapshotRequest
from ....application.validation import ValidationService
from ....infrastructure import Container
from ....infrastructure.logging import logger


class DeleteSnapshotCommand(BaseCommand):
    def __init__(self, container: Container):
        self._container = container

    def execute(self, instances: List[EC2Instance]) -> None:
        if not instances:
            logger.error("No instances available.")
            return

        logger.info("Available instances:")
        for i, instance in enumerate(instances, 1):
            logger.info(f"{i}. {instance.name} ({instance.instance_id})")

        try:
            instance_choice = click.prompt("Select instance", type=int) - 1
            if 0 <= instance_choice < len(instances):
                selected_instance = instances[instance_choice]

                list_request = ListSnapshotsRequest(
                    instance_id=selected_instance.instance_id
                )
                list_response = self._container.list_snapshots_use_case().execute(
                    list_request
                )

                if list_response.success and list_response.snapshots:
                    logger.info("Available snapshots:")
                    for i, snapshot in enumerate(list_response.snapshots, 1):
                        logger.info(
                            f"{i}. {snapshot.snapshot_id} - {snapshot.description}"
                        )

                    snapshot_choice = (
                        click.prompt("Select snapshot to delete", type=int) - 1
                    )
                    if 0 <= snapshot_choice < len(list_response.snapshots):
                        selected_snapshot = list_response.snapshots[snapshot_choice]

                        if click.confirm(
                            f"Are you sure you want to delete {selected_snapshot.snapshot_id}?"
                        ):
                            delete_request = DeleteSnapshotRequest(
                                snapshot_id=selected_snapshot.snapshot_id
                            )

                            is_valid, validated_request_or_error = (
                                ValidationService.validate_delete_snapshot_request(
                                    delete_request
                                )
                            )

                            if not is_valid:
                                logger.error(
                                    f"Validation error: {validated_request_or_error}"
                                )
                                return

                            delete_response = (
                                self._container.delete_snapshot_use_case().execute(
                                    validated_request_or_error
                                )
                            )

                            if delete_response.success:
                                logger.info(delete_response.message)
                            else:
                                logger.error(delete_response.message)
                    else:
                        logger.error("Invalid snapshot selection.")
                else:
                    logger.info("No snapshots found for this instance.")
            else:
                logger.error("Invalid instance selection.")
        except Exception as e:
            logger.error(f"Error deleting snapshot: {str(e)}")
