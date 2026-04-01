from datetime import date

from pawpal_system import Pet, Task


def test_mark_complete_sets_task_status_to_true() -> None:
    task = Task(
        title="Give medication",
        duration_minutes=5,
        priority="high",
        category="medication",
        scheduled_time="09:00",
    )

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog", age=4)
    task = Task(
        title="Lunch",
        duration_minutes=10,
        priority="medium",
        category="feeding",
        scheduled_time="12:00",
    )

    pet.add_task(task)

    assert len(pet.tasks) == 1


def test_mark_task_complete_creates_next_daily_occurrence() -> None:
    pet = Pet(name="Luna", species="cat", age=2)
    task = Task(
        title="Evening play",
        duration_minutes=15,
        priority="medium",
        category="enrichment",
        scheduled_time="18:00",
        frequency="daily",
        due_date=date(2026, 4, 1),
    )
    pet.add_task(task)

    next_task = pet.mark_task_complete("Evening play")

    assert next_task is not None
    assert next_task.due_date == date(2026, 4, 2)
    assert len(pet.tasks) == 2
