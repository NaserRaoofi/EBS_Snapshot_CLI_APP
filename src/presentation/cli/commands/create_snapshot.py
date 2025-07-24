import click
from typing import List
from .base import BaseCommand
from ....domain.entities import EC2Instance
from ....application.dtos import CreateSnapshotRequest
from ....application.validation import ValidationService
from ....infrastructure import Container
from ....infrastructure.logging import logger


class CreateSnapshotCommand(BaseCommand):
    def __init__(self, container: Container):
        self._container = container

    def execute(self, instances: List[EC2Instance]) -> None:
        if not instances:
            logger.error("No instances available.")
            return

        logger.info("Available instances:")
        for i, instance in enumerate(instances, 1):
            logger.info(
                f"{i}. {instance.name} ({instance.instance_id}) - {instance.availability_zone}"
            )

        try:
            instance_choice = click.prompt("Select instance", type=int) - 1
            if 0 <= instance_choice < len(instances):
                selected_instance = instances[instance_choice]
                description = click.prompt(
                    "Enter description (optional)", default="", show_default=False
                )

                request = CreateSnapshotRequest(
                    instance_id=selected_instance.instance_id,
                    instance_name=selected_instance.name,
                    description=description if description else None,
                )

                is_valid, validated_request_or_error = (
                    ValidationService.validate_create_snapshot_request(request)
                )

                if not is_valid:
                    logger.error(f"Validation error: {validated_request_or_error}")
                    return

                response = self._container.create_snapshot_use_case().execute(
                    validated_request_or_error
                )

                if response.success:
                    logger.info(response.message)
                else:
                    logger.error(response.message)
            else:
                logger.error("Invalid instance selection.")
        except Exception as e:
            logger.error(f"Error creating snapshot: {str(e)}")
