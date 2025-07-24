from abc import ABC, abstractmethod
from typing import List
from ....domain.entities import EC2Instance


class BaseCommand(ABC):
    @abstractmethod
    def execute(self, instances: List[EC2Instance]) -> None:
        pass
