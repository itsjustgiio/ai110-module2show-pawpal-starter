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
    luna.add_task(
        Task(
            title="Evening play session",
            duration_minutes=20,
            priority="medium",
            category="enrichment",
            scheduled_time="18:30",
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
