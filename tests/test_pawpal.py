from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


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


def test_sort_by_time_returns_tasks_in_chronological_order() -> None:
    scheduler = Scheduler()
    tasks = [
        Task(
            title="Evening walk",
            duration_minutes=20,
            priority="medium",
            category="exercise",
            scheduled_time="18:00",
            due_date=date(2026, 4, 1),
        ),
        Task(
            title="Breakfast",
            duration_minutes=10,
            priority="high",
            category="feeding",
            scheduled_time="07:30",
            due_date=date(2026, 4, 1),
        ),
        Task(
            title="Vet reminder",
            duration_minutes=15,
            priority="high",
            category="health",
            scheduled_time="09:00",
            due_date=date(2026, 4, 2),
        ),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.title for task in sorted_tasks] == [
        "Breakfast",
        "Evening walk",
        "Vet reminder",
    ]


def test_detect_conflicts_flags_duplicate_task_times() -> None:
    owner = Owner(name="Jordan", available_minutes=90)
    scheduler = Scheduler()
    mochi = Pet(name="Mochi", species="dog", age=4)
    luna = Pet(name="Luna", species="cat", age=2)

    mochi.add_task(
        Task(
            title="Morning walk",
            duration_minutes=25,
            priority="high",
            category="exercise",
            scheduled_time="08:00",
            due_date=date(2026, 4, 1),
        )
    )
    luna.add_task(
        Task(
            title="Breakfast",
            duration_minutes=10,
            priority="high",
            category="feeding",
            scheduled_time="08:00",
            due_date=date(2026, 4, 1),
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(luna)

    conflicts = scheduler.detect_conflicts(owner)

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]
    assert "Morning walk for Mochi" in conflicts[0]
    assert "Breakfast for Luna" in conflicts[0]


def test_create_daily_plan_returns_empty_list_for_pet_with_no_tasks() -> None:
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(Pet(name="Mochi", species="dog", age=4))
    scheduler = Scheduler()

    schedule = scheduler.create_daily_plan(owner)

    assert schedule == []
