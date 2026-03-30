from dataclasses import dataclass, field
from typing import List, Literal


@dataclass
class Task:
    title: str
    duration: int  # in minutes
    priority: Literal["low", "medium", "high"]
    frequency: Literal["daily", "weekly", "as-needed"] = "daily"
    completed: bool = False

    def priority_value(self) -> int:
        """Return numeric priority so tasks can be sorted (higher = more urgent)."""
        return {"low": 1, "medium": 2, "high": 3}[self.priority]

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def __repr__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"{self.title} ({self.duration} min, {self.priority}, {self.frequency}, {status})"


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def get_info(self) -> str:
        """Return a readable summary of this pet."""
        return f"{self.name} ({self.species})"

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def get_info(self) -> str:
        """Return a readable summary of the owner and their pets."""
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "no pets"
        return f"{self.name} (pets: {pet_names})"

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Collect and return all tasks across every pet."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_all_pending_tasks(self) -> List[Task]:
        """Collect and return only incomplete tasks across every pet."""
        pending = []
        for pet in self.pets:
            pending.extend(pet.get_pending_tasks())
        return pending


class Scheduler:
    def __init__(self, owner: Owner, available_minutes: int = 480):
        self.owner = owner
        self.available_minutes = available_minutes  # default: 8 hours

    def generate_schedule(self) -> List[Task]:
        """Sort all pending tasks by priority and return those that fit within available_minutes."""
        pending = self.owner.get_all_pending_tasks()
        sorted_tasks = sorted(pending, key=lambda t: t.priority_value(), reverse=True)

        scheduled = []
        time_remaining = self.available_minutes
        for task in sorted_tasks:
            if task.duration <= time_remaining:
                scheduled.append(task)
                time_remaining -= task.duration

        return scheduled

    def explain_schedule(self) -> str:
        """Return a plain-language explanation of the generated schedule."""
        scheduled = self.generate_schedule()
        if not scheduled:
            return "No tasks could be scheduled. Either all tasks are complete or none fit within the available time."

        total = sum(t.duration for t in scheduled)
        lines = [
            f"Schedule for {self.owner.name} ({self.available_minutes} min available):",
            "",
        ]
        for i, task in enumerate(scheduled, start=1):
            lines.append(f"  {i}. {task.title} — {task.duration} min [{task.priority} priority]")

        lines += [
            "",
            f"Total time: {total} min | Remaining: {self.available_minutes - total} min",
            "Tasks are ordered highest-priority first. Lower-priority tasks are dropped if time runs out.",
        ]
        return "\n".join(lines)
