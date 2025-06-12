import logging
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), "backup.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ec2_backup_tool")
