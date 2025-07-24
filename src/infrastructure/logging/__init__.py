import logging
from typing import Optional


class Logger:
    def __init__(
        self,
        name: str = "ebs-snapshot",
        level: str = "INFO",
        log_file: Optional[str] = None,
    ):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper()))

        if not self._logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def debug(self, message: str) -> None:
        self._logger.debug(message)


logger = Logger()
