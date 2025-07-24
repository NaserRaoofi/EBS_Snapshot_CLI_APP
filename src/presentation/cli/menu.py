import click
from ...infrastructure.logging import logger


class MenuService:
    def show_main_menu(self) -> int:
        logger.info("EC2 Snapshot Tool")
        logger.info("1. Take snapshot")
        logger.info("2. List snapshots")
        logger.info("3. Delete a snapshot")
        logger.info("4. Restore from snapshot")

        return click.prompt("Select an option", type=int)
