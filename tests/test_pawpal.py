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
