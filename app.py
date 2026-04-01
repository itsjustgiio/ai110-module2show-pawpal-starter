import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This version is connected to the Python logic layer, so pets and tasks are stored
as real objects during the current Streamlit session.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.subheader("Owner Setup")
owner.name = st.text_input("Owner name", value=owner.name)
owner.update_available_time(
    int(
        st.number_input(
            "Available minutes today",
            min_value=1,
            max_value=480,
            value=owner.available_minutes,
        )
    )
)

st.divider()

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age", min_value=0, max_value=30, value=1)
care_notes = st.text_area("Care notes", value="")

if st.button("Add pet"):
    if pet_name.strip():
        owner.add_pet(
            Pet(
                name=pet_name.strip(),
                species=species,
                age=int(pet_age),
                care_notes=care_notes.strip(),
            )
        )
        st.success(f"Added {pet_name.strip()} to {owner.name}'s pets.")
    else:
        st.error("Please enter a pet name before adding a pet.")

if owner.pets:
    st.table(
        [
            {
                "name": pet.name,
                "species": pet.species,
                "age": pet.age,
                "care_notes": pet.care_notes,
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Tasks")
st.caption("Add tasks, then filter and review them before building a schedule.")

task_title = st.text_input("Task title", value="Morning walk")
task_col1, task_col2, task_col3 = st.columns(3)
with task_col1:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with task_col2:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with task_col3:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"], index=0)

task_col4, task_col5 = st.columns(2)
with task_col4:
    category = st.text_input("Category", value="exercise")
with task_col5:
    scheduled_time = st.text_input("Scheduled time", value="08:00")

selected_pet_name = st.selectbox(
    "Assign task to pet",
    options=[pet.name for pet in owner.pets],
    index=None,
    placeholder="Choose a pet",
)

if st.button("Add task"):
    if not owner.pets:
        st.error("Add a pet before creating tasks.")
    elif not selected_pet_name:
        st.error("Choose which pet should receive this task.")
    else:
        selected_pet = owner.get_pet(selected_pet_name)
        if selected_pet is not None:
            selected_pet.add_task(
                Task(
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=priority,
                    category=category,
                    scheduled_time=scheduled_time,
                    frequency=frequency,
                )
            )
            st.success(f"Added task '{task_title}' for {selected_pet.name}.")

all_tasks = [task for pet in owner.pets for task in pet.tasks]
if all_tasks:
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter = st.selectbox(
            "Filter by pet",
            options=["All pets", *[pet.name for pet in owner.pets]],
        )
    with filter_col2:
        status_filter = st.selectbox(
            "Filter by status",
            options=["Pending only", "Completed only", "All tasks"],
        )

    selected_pet = None if pet_filter == "All pets" else pet_filter
    selected_status = {"Pending only": False, "Completed only": True, "All tasks": None}[status_filter]
    filtered_tasks = scheduler.sort_by_time(
        scheduler.filter_tasks(owner, pet_name=selected_pet, completed=selected_status)
    )

    st.table(
        [
            {
                "type": task.category_icon(),
                "due_date": task.due_date.isoformat(),
                "time": task.scheduled_time,
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority_badge(),
                "category": task.category,
                "frequency": task.frequency,
                "status": task.status_badge(),
            }
            for task in filtered_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
conflicts = scheduler.detect_conflicts(owner)
if conflicts:
    for warning in conflicts:
        st.warning(warning)
elif all_tasks:
    st.success("No exact-time conflicts detected in the current task list.")

if st.button("Generate schedule"):
    schedule = scheduler.create_daily_plan(owner)
    if schedule:
        high_priority_count = sum(1 for task in schedule if task.priority.lower() == "high")
        st.success(f"Built a plan with {len(schedule)} task(s), including {high_priority_count} high-priority item(s).")
        st.table(
            [
                {
                    "type": task.category_icon(),
                    "due_date": task.due_date.isoformat(),
                    "time": task.scheduled_time,
                    "title": task.title,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority_badge(),
                    "category": task.category,
                    "status": task.status_badge(),
                }
                for task in schedule
            ]
        )
        st.info(scheduler.explain_plan(schedule, owner))
    else:
        st.warning("No tasks fit the current plan. Add tasks or increase available minutes.")
