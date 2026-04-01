from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    """Represents a single pet care activity."""

    title: str
    duration_minutes: int
    priority: str
    category: str
    scheduled_time: str
    frequency: str = "daily"
    notes: str = ""
    preferred_time: Optional[str] = None
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def matches_time_preference(self, time_block: str) -> bool:
        """Return whether the task fits a requested time block."""
        if self.preferred_time is None:
            return True
        return self.preferred_time.lower() == time_block.lower()

    def priority_score(self) -> int:
        """Return a numeric score for sorting task priority."""
        return PRIORITY_RANK.get(self.priority.lower(), 0)

    def __str__(self) -> str:
        """Return a readable single-line description for CLI output."""
        status = "done" if self.completed else "pending"
        return (
            f"{self.scheduled_time} | {self.title} "
            f"({self.duration_minutes} min, {self.priority} priority, {status})"
        )


@dataclass
class Pet:
    """Stores pet details and its care tasks."""

    name: str
    species: str
    age: int
    care_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> None:
        """Remove a task by title."""
        self.tasks = [task for task in self.tasks if task.title != task_title]

    def get_pending_tasks(self) -> list[Task]:
        """Return incomplete tasks for this pet."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """Manages pets, available time, and scheduling preferences."""

    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def update_available_time(self, minutes: int) -> None:
        """Change the owner's available care time."""
        self.available_minutes = minutes

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks from every pet owned by this user."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_pending_tasks())
        return all_tasks


class Scheduler:
    """Builds and explains a daily care plan."""

    def create_daily_plan(self, owner: Owner) -> list[Task]:
        """Build a daily task list that fits the owner's constraints."""
        tasks = owner.get_all_tasks()
        prioritized_tasks = self.prioritize_tasks(tasks)
        return self.filter_tasks_by_time(prioritized_tasks, owner.available_minutes)

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by importance and time."""
        return sorted(
            tasks,
            key=lambda task: (-task.priority_score(), task.scheduled_time, task.title.lower()),
        )

    def filter_tasks_by_time(self, tasks: list[Task], available_minutes: int) -> list[Task]:
        """Keep only the tasks that fit within the available time budget."""
        selected_tasks: list[Task] = []
        used_minutes = 0

        for task in tasks:
            if used_minutes + task.duration_minutes <= available_minutes:
                selected_tasks.append(task)
                used_minutes += task.duration_minutes

        return selected_tasks

    def explain_plan(self, selected_tasks: list[Task], owner: Owner) -> str:
        """Explain why the chosen tasks were included in the daily plan."""
        if not selected_tasks:
            return (
                f"No tasks were selected for {owner.name} because none fit within "
                f"the {owner.available_minutes}-minute limit."
            )

        total_minutes = sum(task.duration_minutes for task in selected_tasks)
        task_names = ", ".join(task.title for task in selected_tasks)
        return (
            f"Selected {len(selected_tasks)} task(s) for {owner.name}: {task_names}. "
            f"They fit within {owner.available_minutes} available minutes and were chosen "
            f"by priority first, then by scheduled time. Total planned time: {total_minutes} minutes."
        )
