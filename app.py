from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Priority, Schedule, Task, TaskCategory

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# Streamlit reruns this whole script on every interaction, so a plain local
# variable would reset on each click. st.session_state is the "vault" that
# survives reruns, so we only build a new Owner the first time through.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

owner = st.session_state.owner
owner.name = owner_name

st.divider()

st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    breed = st.text_input("Breed", value="unknown")

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age=0))

if not owner.pets:
    st.info("No pets yet. Add one above.")
    st.stop()

pet_names = [p.name for p in owner.pets]
selected_pet_name = st.selectbox("Select pet", pet_names, index=len(pet_names) - 1)
pet = next(p for p in owner.pets if p.name == selected_pet_name)

st.divider()

st.markdown("### Tasks")
st.caption(f"Add a few tasks for {pet.name}.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    has_preferred_time = st.checkbox("Set a preferred time", value=True)
with col5:
    preferred_time = st.time_input("Preferred time", value=time(9, 0), disabled=not has_preferred_time)
with col6:
    recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])

if st.button("Add task"):
    pet.add_task(
        Task(
            task_id=f"t{len(pet.tasks) + 1}",
            name=task_title,
            category=TaskCategory.OTHER,
            duration_minutes=int(duration),
            priority=Priority[priority.upper()],
            preferred_time=preferred_time if has_preferred_time else None,
            is_recurring=recurrence != "none",
            recurrence=None if recurrence == "none" else recurrence,
            due_date=date.today() if recurrence != "none" else None,
        )
    )

# Owner.detect_conflicts() is a lightweight, exact-time-match check across every
# pet, so a pet owner sees it as soon as they create a scheduling clash, not
# buried in the per-pet task table below.
conflicts = owner.detect_conflicts()
for warning in conflicts:
    st.warning(f"⚠️ {warning}")

if pet.tasks:
    st.write("Current tasks (sorted by time via `Schedule.sort_by_time()`):")
    sorted_tasks = Schedule.sort_by_time(pet.tasks)
    st.table(
        [
            {
                "title": task.name,
                "time": task.preferred_time.strftime("%H:%M") if task.preferred_time else "—",
                "duration_minutes": task.duration_minutes,
                "priority": task.priority.name.lower(),
                "recurrence": task.recurrence or "none",
                "status": "✅ done" if task.is_done else "⏳ pending",
            }
            for task in sorted_tasks
        ]
    )

    pending_tasks = pet.filter_tasks(is_done=False)
    if pending_tasks:
        task_to_complete = st.selectbox(
            "Mark a task complete", [task.name for task in pending_tasks], key="complete_task_select"
        )
        if st.button("Mark complete"):
            task = next(t for t in pending_tasks if t.name == task_to_complete)
            next_task = pet.complete_task(task.task_id)
            if next_task is not None:
                st.success(
                    f"✅ {task.name} marked complete. Next occurrence added, due {next_task.due_date}."
                )
            else:
                st.success(f"✅ {task.name} marked complete.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(f"This button calls Schedule.generate_plan() for {pet.name}.")

if st.button("Generate schedule"):
    schedule = Schedule(pet=pet, schedule_date=date.today(), available_minutes=480)
    schedule.generate_plan(pet.tasks)
    st.success(f"Schedule generated for {pet.name}.")
    st.text(schedule.explain_plan())
