from typing import List
from ...application.dtos import ListInstancesResponse
from ...infrastructure import Container
from ...infrastructure.logging import logger
from .menu import MenuService
from .commands import CommandFactory


class CLIApplication:
    def __init__(self, container: Container):
        self._container = container
        self._menu_service = MenuService()
        self._command_factory = CommandFactory(container)

    def run(self) -> None:
        try:
            instances_response = self._container.list_instances_use_case().execute()

            if not instances_response.success or not instances_response.instances:
                logger.error("No running EC2 instances found.")
                return

            self._run_main_loop(instances_response)

        except Exception as e:
            logger.error(f"Application error: {str(e)}")

    def _run_main_loop(self, instances_response: ListInstancesResponse) -> None:
        choice = self._menu_service.show_main_menu()
        command = self._command_factory.create_command(choice)

        if command:
            command.execute(instances_response.instances)
        else:
            logger.warning("Invalid option selected.")
