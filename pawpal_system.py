from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    name: str
    species: str

    def get_info(self) -> str:
        pass


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def get_info(self) -> str:
        pass


@dataclass
class Task:
    title: str
    duration: int  # in minutes
    priority: str  # "low", "medium", or "high"

    def priority_value(self) -> int:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def generate_schedule(self) -> List[Task]:
        pass

    def explain_schedule(self) -> str:
        pass
