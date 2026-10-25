"""Demo script: build an owner, pets, and tasks, then print today's schedule."""

from datetime import date, time

from pawpal_system import Owner, Pet, Priority, Schedule, Task, TaskCategory

owner = Owner(name="Jamie")

dog = Pet(name="Rex", species="Dog", breed="Labrador", age=4)
cat = Pet(name="Luna", species="Cat", breed="Tabby", age=2)
owner.add_pet(dog)
owner.add_pet(cat)

morning_walk = Task(
    task_id="T1",
    name="Morning Walk",
    category=TaskCategory.WALK,
    duration_minutes=30,
    priority=Priority.HIGH,
    preferred_time=time(7, 30),
)
afternoon_feeding = Task(
    task_id="T2",
    name="Afternoon Feeding",
    category=TaskCategory.FEEDING,
    duration_minutes=15,
    priority=Priority.MEDIUM,
    preferred_time=time(13, 0),
)
evening_grooming = Task(
    task_id="T3",
    name="Evening Grooming",
    category=TaskCategory.GROOMING,
    duration_minutes=20,
    priority=Priority.LOW,
    preferred_time=time(18, 0),
)

dog.add_task(morning_walk)
dog.add_task(afternoon_feeding)
cat.add_task(evening_grooming)

today = date.today()

for pet in owner.pets:
    schedule = Schedule(pet=pet, schedule_date=today, available_minutes=480)
    schedule.generate_plan(pet.tasks)
    print(schedule.explain_plan())
    print()
