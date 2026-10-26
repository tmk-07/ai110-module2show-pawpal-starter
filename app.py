from datetime import date

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

if st.button("Add task"):
    pet.add_task(
        Task(
            task_id=f"t{len(pet.tasks) + 1}",
            name=task_title,
            category=TaskCategory.OTHER,
            duration_minutes=int(duration),
            priority=Priority[priority.upper()],
        )
    )

if pet.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {"title": task.name, "duration_minutes": task.duration_minutes, "priority": task.priority.name.lower()}
            for task in pet.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(f"This button calls Schedule.generate_plan() for {pet.name}.")

if st.button("Generate schedule"):
    schedule = Schedule(pet=pet, schedule_date=date.today(), available_minutes=480)
    schedule.generate_plan(pet.tasks)
    st.text(schedule.explain_plan())
