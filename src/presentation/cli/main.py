import click
from typing import Optional

from ...application.dtos import (
    CreateSnapshotRequest,
    ListSnapshotsRequest,
    DeleteSnapshotRequest,
    RestoreSnapshotRequest,
)
from ...application.use_cases import (
    CreateSnapshotUseCase,
    ListSnapshotsUseCase,
    DeleteSnapshotUseCase,
    ListInstancesUseCase,
    RestoreSnapshotUseCase,
)
from ...application.validation import ValidationService
from ...infrastructure import Container
from ...infrastructure.logging import logger


class SnapshotCLI:
    def __init__(self, container: Container):
        self._container = container

    def run(self) -> None:
        instances_response = self._container.list_instances_use_case().execute()

        if not instances_response.success or not instances_response.instances:
            logger.error("No running EC2 instances found.")
            return

        logger.info("EC2 Snapshot Tool")
        logger.info("1. Take snapshot")
        logger.info("2. List snapshots")
        logger.info("3. Delete a snapshot")
        logger.info("4. Restore from snapshot")

        try:
            choice = click.prompt("Select an option", type=int)

            if choice == 1:
                self._handle_create_snapshot(instances_response.instances)
            elif choice == 2:
                self._handle_list_snapshots(instances_response.instances)
            elif choice == 3:
                self._handle_delete_snapshot(instances_response.instances)
            elif choice == 4:
                self._handle_restore_snapshot(instances_response.instances)
            else:
                logger.warning("Invalid option selected.")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")

    def _handle_create_snapshot(self, instances) -> None:
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

    def _handle_list_snapshots(self, instances) -> None:
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

    def _handle_delete_snapshot(self, instances) -> None:
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

    def _handle_restore_snapshot(self, instances) -> None:
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
                        click.prompt("Select snapshot to restore", type=int) - 1
                    )
                    if 0 <= snapshot_choice < len(list_response.snapshots):
                        selected_snapshot = list_response.snapshots[snapshot_choice]

                        if click.confirm(
                            f"Are you sure you want to restore {selected_instance.name} from {selected_snapshot.snapshot_id}?"
                        ):
                            restore_request = RestoreSnapshotRequest(
                                instance_id=selected_instance.instance_id,
                                snapshot_id=selected_snapshot.snapshot_id,
                            )

                            is_valid, validated_request_or_error = (
                                ValidationService.validate_restore_snapshot_request(
                                    restore_request
                                )
                            )

                            if not is_valid:
                                logger.error(
                                    f"Validation error: {validated_request_or_error}"
                                )
                                return

                            restore_response = (
                                self._container.restore_snapshot_use_case().execute(
                                    validated_request_or_error
                                )
                            )

                            if restore_response.success:
                                logger.info(restore_response.message)
                            else:
                                logger.error(restore_response.message)
                    else:
                        logger.error("Invalid snapshot selection.")
                else:
                    logger.info("No snapshots found for this instance.")
            else:
                logger.error("Invalid instance selection.")
        except Exception as e:
            logger.error(f"Error restoring snapshot: {str(e)}")


@click.command()
def main() -> None:
    container = Container()
    cli = SnapshotCLI(container)
    cli.run()


if __name__ == "__main__":
    main()
