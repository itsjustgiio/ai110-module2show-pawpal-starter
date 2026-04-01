from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    category: str
    notes: str = ""
    preferred_time: Optional[str] = None
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def matches_time_preference(self, time_block: str) -> bool:
        """Return whether the task fits a requested time block."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    care_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass

    def remove_task(self, task_title: str) -> None:
        """Remove a task by title."""
        pass

    def get_pending_tasks(self) -> list[Task]:
        """Return incomplete tasks for this pet."""
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        pass

    def update_available_time(self, minutes: int) -> None:
        """Change the owner's available care time."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks from every pet owned by this user."""
        pass


class Scheduler:
    def create_daily_plan(self, owner: Owner) -> list[Task]:
        """Build a daily task list that fits the owner's constraints."""
        pass

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by importance and urgency."""
        pass

    def filter_tasks_by_time(self, tasks: list[Task], available_minutes: int) -> list[Task]:
        """Keep only the tasks that fit within the available time budget."""
        pass

    def explain_plan(self, selected_tasks: list[Task], owner: Owner) -> str:
        """Explain why the chosen tasks were included in the daily plan."""
        pass
