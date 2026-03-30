from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Literal, Optional


@dataclass
class Task:
    title: str
    duration: int  # in minutes
    priority: Literal["low", "medium", "high"]
    frequency: Literal["daily", "weekly", "as-needed"] = "daily"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def priority_value(self) -> int:
        """Return numeric priority so tasks can be sorted (higher = more urgent)."""
        return {"low": 1, "medium": 2, "high": 3}[self.priority]

    def mark_complete(self) -> Optional[Task]:
        """Mark this task done and return a new Task for the next occurrence, or None if as-needed."""
        self.completed = True
        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(weeks=1)
        else:
            return None  # "as-needed" tasks do not recur automatically
        return Task(
            title=self.title,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            due_date=next_due,
        )

    def __repr__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"{self.title} ({self.duration} min, {self.priority}, {self.frequency}, due {self.due_date}, {status})"


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

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and automatically queue the next recurrence if applicable."""
        next_task = task.mark_complete()
        if next_task:
            self.tasks.append(next_task)
        return next_task


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

    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the pet with the given name."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.tasks
        return []

    def get_tasks_by_priority(self, priority: Literal["low", "medium", "high"]) -> List[Task]:
        """Return all tasks across every pet that match the given priority level."""
        return [t for t in self.get_all_tasks() if t.priority == priority]


class Scheduler:
    def __init__(self, owner: Owner, available_minutes: int = 480):
        self.owner = owner
        self.available_minutes = available_minutes  # default: 8 hours

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by duration ascending — shortest task first."""
        return sorted(tasks, key=lambda t: t.duration)

    def filter_by_status(self, tasks: List[Task], completed: bool) -> List[Task]:
        """Return only tasks whose completed flag matches the given value."""
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks (complete or not) belonging to a specific pet by name."""
        return self.owner.get_tasks_for_pet(pet_name)

    def generate_schedule(self) -> List[Task]:
        """Sort pending tasks by priority then duration, return those that fit within available_minutes."""
        pending = self.owner.get_all_pending_tasks()
        # Primary sort: highest priority first. Tiebreaker: shortest duration first.
        sorted_tasks = sorted(pending, key=lambda t: (-t.priority_value(), t.duration))

        scheduled = []
        time_remaining = self.available_minutes
        for task in sorted_tasks:
            if task.duration <= time_remaining:
                scheduled.append(task)
                time_remaining -= task.duration

        return scheduled

    def get_dropped_tasks(self) -> List[Task]:
        """Return pending tasks that were not scheduled because they exceeded remaining time."""
        scheduled = self.generate_schedule()
        scheduled_titles = {t.title for t in scheduled}
        return [t for t in self.owner.get_all_pending_tasks() if t.title not in scheduled_titles]

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
