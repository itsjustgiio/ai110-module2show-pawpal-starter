from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
PRIORITY_BADGES = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
CATEGORY_ICONS = {
    "exercise": "🐕",
    "feeding": "🍽️",
    "medication": "💊",
    "enrichment": "🧩",
    "grooming": "🪮",
}


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
    due_date: date = field(default_factory=date.today)

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

    def priority_badge(self) -> str:
        """Return a display-friendly priority label."""
        return PRIORITY_BADGES.get(self.priority.lower(), self.priority.title())

    def category_icon(self) -> str:
        """Return an emoji for the task category."""
        return CATEGORY_ICONS.get(self.category.lower(), "📌")

    def status_badge(self) -> str:
        """Return a display-friendly completion label."""
        return "✅ Done" if self.completed else "⏳ Pending"

    def next_occurrence(self) -> Optional[Task]:
        """Create the next recurring task instance after completion."""
        frequency = self.frequency.lower()
        if frequency == "daily":
            next_due_date = self.due_date + timedelta(days=1)
        elif frequency == "weekly":
            next_due_date = self.due_date + timedelta(weeks=1)
        else:
            return None

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            scheduled_time=self.scheduled_time,
            frequency=self.frequency,
            notes=self.notes,
            preferred_time=self.preferred_time,
            due_date=next_due_date,
        )

    def __str__(self) -> str:
        """Return a readable single-line description for CLI output."""
        status = "done" if self.completed else "pending"
        return (
            f"{self.due_date.isoformat()} {self.scheduled_time} | {self.title} "
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

    def get_tasks_by_status(self, completed: bool) -> list[Task]:
        """Return tasks filtered by completion status."""
        return [task for task in self.tasks if task.completed is completed]

    def mark_task_complete(self, task_title: str) -> Optional[Task]:
        """Complete a task and add its next recurring instance when needed."""
        for task in self.tasks:
            if task.title == task_title and not task.completed:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task is not None:
                    self.add_task(next_task)
                return next_task
        return None


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

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return a pet by name when it exists."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks from every pet owned by this user."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_pending_tasks())
        return all_tasks


class Scheduler:
    """Builds and explains a daily care plan."""

    def create_daily_plan(self, owner: Owner) -> list[Task]:
        """Build a daily task list sorted by priority first, then time."""
        tasks = self.filter_tasks(owner)
        prioritized_tasks = self.prioritize_tasks(tasks)
        return self.filter_tasks_by_time(prioritized_tasks, owner.available_minutes)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by due date and HH:MM time string."""
        return sorted(tasks, key=lambda task: (task.due_date, task.scheduled_time, task.title.lower()))

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by importance and time."""
        return sorted(
            tasks,
            key=lambda task: (
                -task.priority_score(),
                task.due_date,
                task.scheduled_time,
                task.title.lower(),
            ),
        )

    def filter_tasks(
        self,
        owner: Owner,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = False,
    ) -> list[Task]:
        """Return tasks filtered by pet name and completion status."""
        pets = owner.pets if pet_name is None else [pet for pet in owner.pets if pet.name == pet_name]
        filtered_tasks: list[Task] = []

        for pet in pets:
            for task in pet.tasks:
                if completed is None or task.completed is completed:
                    filtered_tasks.append(task)

        return filtered_tasks

    def filter_tasks_by_time(self, tasks: list[Task], available_minutes: int) -> list[Task]:
        """Keep only the tasks that fit within the available time budget."""
        selected_tasks: list[Task] = []
        used_minutes = 0

        for task in tasks:
            if used_minutes + task.duration_minutes <= available_minutes:
                selected_tasks.append(task)
                used_minutes += task.duration_minutes

        return selected_tasks

    def detect_conflicts(self, owner: Owner) -> list[str]:
        """Return warning messages for tasks that share the same exact date and time."""
        schedule_map: dict[tuple[date, str], list[tuple[str, Task]]] = {}

        for pet in owner.pets:
            for task in pet.get_pending_tasks():
                key = (task.due_date, task.scheduled_time)
                schedule_map.setdefault(key, []).append((pet.name, task))

        warnings: list[str] = []
        for (due_date, scheduled_time), entries in schedule_map.items():
            if len(entries) > 1:
                details = ", ".join(f"{task.title} for {pet_name}" for pet_name, task in entries)
                warnings.append(
                    f"Conflict at {scheduled_time} on {due_date.isoformat()}: {details}."
                )

        return warnings

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
            f"by priority first, then sorted by date and time. Total planned time: {total_minutes} minutes."
        )
