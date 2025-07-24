import click
from typing import List
from .base import BaseCommand
from ....domain.entities import EC2Instance
from ....application.dtos import ListSnapshotsRequest
from ....infrastructure import Container
from ....infrastructure.logging import logger


class ListSnapshotsCommand(BaseCommand):
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

                request = ListSnapshotsRequest(
                    instance_id=selected_instance.instance_id
                )
                response = self._container.list_snapshots_use_case().execute(request)

                if response.success:
                    if response.snapshots:
                        logger.info(f"Snapshots for {selected_instance.name}:")
                        for snapshot in response.snapshots:
                            logger.info(
                                f"  {snapshot.snapshot_id} - {snapshot.description} - {snapshot.start_time} - {snapshot.state}"
                            )
                    else:
                        logger.info("No snapshots found for this instance.")
                else:
                    logger.error(response.message)
            else:
                logger.error("Invalid instance selection.")
        except Exception as e:
            logger.error(f"Error listing snapshots: {str(e)}")
