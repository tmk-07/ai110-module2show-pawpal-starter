"""Demo script: build an owner, pets, and tasks, then exercise the scheduling logic."""

from datetime import date, time

from pawpal_system import Owner, Pet, Priority, Schedule, Task, TaskCategory

owner = Owner(name="Jamie")

dog = Pet(name="Rex", species="Dog", breed="Labrador", age=4)
cat = Pet(name="Luna", species="Cat", breed="Tabby", age=2)
owner.add_pet(dog)
owner.add_pet(cat)

# Added out of chronological order on purpose, to exercise Schedule.sort_by_time().
evening_grooming = Task(
    task_id="T3",
    name="Evening Grooming",
    category=TaskCategory.GROOMING,
    duration_minutes=20,
    priority=Priority.LOW,
    preferred_time=time(18, 0),
)
morning_walk = Task(
    task_id="T1",
    name="Morning Walk",
    category=TaskCategory.WALK,
    duration_minutes=30,
    priority=Priority.HIGH,
    preferred_time=time(7, 30),
    is_recurring=True,
    recurrence="daily",
    due_date=date.today(),
)
afternoon_feeding = Task(
    task_id="T2",
    name="Afternoon Feeding",
    category=TaskCategory.FEEDING,
    duration_minutes=15,
    priority=Priority.MEDIUM,
    preferred_time=time(13, 0),
)

dog.add_task(evening_grooming)
dog.add_task(morning_walk)
dog.add_task(afternoon_feeding)
cat.add_task(
    Task(
        task_id="T4",
        name="Litter Box Cleaning",
        category=TaskCategory.OTHER,
        duration_minutes=10,
        priority=Priority.MEDIUM,
        # Scheduled at the same time as Rex's afternoon feeding, to demonstrate conflict detection.
        preferred_time=time(13, 0),
    )
)

print("=== Sorting demo: Rex's tasks sorted by time ===")
for task in Schedule.sort_by_time(dog.tasks):
    print(f"- {task.preferred_time}: {task.name}")
print()

print("=== Recurring task demo ===")
print(f"Before completing: {morning_walk.name} is_done={morning_walk.is_done}")
next_walk = dog.complete_task(morning_walk.task_id)
print(f"After completing: {morning_walk.name} is_done={morning_walk.is_done}")
if next_walk:
    print(f"Next occurrence auto-created: {next_walk.task_id}, due {next_walk.due_date}")
print()

print("=== Filtering demo ===")
print("Rex's completed tasks:", [task.name for task in dog.filter_tasks(is_done=True)])
print("Rex's pending tasks:", [task.name for task in dog.filter_tasks(is_done=False)])
print("All of Luna's tasks:", [task.name for task in owner.get_tasks_by_pet("Luna")])
print()

print("=== Conflict detection demo ===")
conflicts = owner.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"WARNING: {warning}")
else:
    print("No conflicts found.")
print()

print("=== Daily schedule ===")
today = date.today()
for pet in owner.pets:
    schedule = Schedule(pet=pet, schedule_date=today, available_minutes=480)
    schedule.generate_plan(pet.tasks)
    print(schedule.explain_plan())
    print()
