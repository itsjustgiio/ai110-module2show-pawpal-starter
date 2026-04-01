from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(owner: Owner, scheduler: Scheduler) -> None:
    """Print a readable daily schedule for the terminal."""
    schedule = scheduler.create_daily_plan(owner)

    print(f"Today's Schedule for {owner.name}")
    print("-" * 40)

    if not schedule:
        print("No tasks scheduled today.")
        return

    for index, task in enumerate(schedule, start=1):
        print(f"{index}. {task}")

    print("-" * 40)
    print(scheduler.explain_plan(schedule, owner))


def print_filtered_tasks(owner: Owner, scheduler: Scheduler, pet_name: str) -> None:
    """Print filtered tasks for one pet."""
    tasks = scheduler.sort_by_time(scheduler.filter_tasks(owner, pet_name=pet_name, completed=False))
    print(f"\nPending tasks for {pet_name}")
    print("-" * 40)
    for task in tasks:
        print(task)


def print_conflicts(owner: Owner, scheduler: Scheduler) -> None:
    """Print scheduling conflict warnings when they exist."""
    conflicts = scheduler.detect_conflicts(owner)
    print("\nConflict Check")
    print("-" * 40)
    if conflicts:
        for warning in conflicts:
            print(f"WARNING: {warning}")
    else:
        print("No exact-time conflicts detected.")


def print_recurring_result(pet: Pet, task_title: str) -> None:
    """Complete a recurring task and print the newly created occurrence."""
    next_task = pet.mark_task_complete(task_title)
    print("\nRecurring Task Demo")
    print("-" * 40)
    if next_task is None:
        print(f"No recurring task was generated for '{task_title}'.")
    else:
        print(f"Completed '{task_title}' and created next occurrence:")
        print(next_task)


def build_demo_data() -> tuple[Owner, Scheduler]:
    """Create demo pets and tasks for CLI verification."""
    owner = Owner(name="Jordan", available_minutes=75, preferences=["morning", "routine"])

    mochi = Pet(name="Mochi", species="dog", age=4, care_notes="Loves long walks.")
    luna = Pet(name="Luna", species="cat", age=2, care_notes="Needs evening playtime.")

    mochi.add_task(
        Task(
            title="Morning walk",
            duration_minutes=25,
            priority="high",
            category="exercise",
            scheduled_time="08:00",
            frequency="daily",
            preferred_time="morning",
        )
    )
    mochi.add_task(
        Task(
            title="Breakfast",
            duration_minutes=10,
            priority="high",
            category="feeding",
            scheduled_time="07:30",
            frequency="daily",
        )
    )
    mochi.add_task(
        Task(
            title="Medication",
            duration_minutes=5,
            priority="high",
            category="medication",
            scheduled_time="06:45",
            frequency="daily",
        )
    )
    luna.add_task(
        Task(
            title="Evening play session",
            duration_minutes=20,
            priority="medium",
            category="enrichment",
            scheduled_time="08:00",
            frequency="daily",
            preferred_time="evening",
        )
    )
    luna.add_task(
        Task(
            title="Brush fur",
            duration_minutes=15,
            priority="low",
            category="grooming",
            scheduled_time="19:00",
            frequency="weekly",
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(luna)

    return owner, Scheduler()


if __name__ == "__main__":
    demo_owner, demo_scheduler = build_demo_data()
    print_schedule(demo_owner, demo_scheduler)
    print_filtered_tasks(demo_owner, demo_scheduler, pet_name="Mochi")
    print_conflicts(demo_owner, demo_scheduler)

    mochi = demo_owner.get_pet("Mochi")
    if mochi is not None:
        print_recurring_result(mochi, "Morning walk")
