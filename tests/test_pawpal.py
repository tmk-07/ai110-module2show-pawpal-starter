from datetime import date, time

from pawpal_system import Owner, Pet, Schedule, Task, TaskCategory, Priority


def _make_task(task_id="t1", preferred_time=None, is_recurring=False, recurrence=None, due_date=None):
    return Task(
        task_id=task_id,
        name="Walk",
        category=TaskCategory.WALK,
        duration_minutes=30,
        priority=Priority.MEDIUM,
        preferred_time=preferred_time,
        is_recurring=is_recurring,
        recurrence=recurrence,
        due_date=due_date,
    )


def test_mark_done_changes_task_status():
    task = _make_task()
    assert task.is_done is False

    task.mark_done()

    assert task.is_done is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Rex", species="Dog", breed="Lab", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(_make_task())

    assert len(pet.tasks) == 1


# --- Sorting correctness ---------------------------------------------------


def test_sort_by_time_returns_chronological_order():
    morning = _make_task(task_id="t1", preferred_time=time(7, 30))
    afternoon = _make_task(task_id="t2", preferred_time=time(13, 0))
    evening = _make_task(task_id="t3", preferred_time=time(18, 0))

    sorted_tasks = Schedule.sort_by_time([evening, morning, afternoon])

    assert [task.task_id for task in sorted_tasks] == ["t1", "t2", "t3"]


def test_sort_by_time_places_untimed_tasks_last():
    timed = _make_task(task_id="t1", preferred_time=time(9, 0))
    untimed = _make_task(task_id="t2", preferred_time=None)

    sorted_tasks = Schedule.sort_by_time([untimed, timed])

    assert [task.task_id for task in sorted_tasks] == ["t1", "t2"]


def test_sort_by_time_on_empty_list_returns_empty_list():
    assert Schedule.sort_by_time([]) == []


# --- Recurrence logic --------------------------------------------------------


def test_completing_daily_task_creates_next_day_occurrence():
    pet = Pet(name="Rex", species="Dog", breed="Lab", age=3)
    task = _make_task(
        task_id="t1",
        is_recurring=True,
        recurrence="daily",
        due_date=date(2026, 1, 1),
    )
    pet.add_task(task)

    next_task = pet.complete_task("t1")

    assert task.is_done is True
    assert next_task is not None
    assert next_task.is_done is False
    assert next_task.due_date == date(2026, 1, 2)
    assert next_task in pet.tasks


def test_completing_weekly_task_creates_occurrence_one_week_later():
    pet = Pet(name="Rex", species="Dog", breed="Lab", age=3)
    task = _make_task(
        task_id="t1",
        is_recurring=True,
        recurrence="weekly",
        due_date=date(2026, 1, 1),
    )
    pet.add_task(task)

    next_task = pet.complete_task("t1")

    assert next_task.due_date == date(2026, 1, 8)


def test_completing_non_recurring_task_does_not_create_new_task():
    pet = Pet(name="Rex", species="Dog", breed="Lab", age=3)
    pet.add_task(_make_task(task_id="t1"))

    next_task = pet.complete_task("t1")

    assert next_task is None
    assert len(pet.tasks) == 1


# --- Conflict detection ------------------------------------------------------


def test_detect_conflicts_flags_two_tasks_at_the_same_time():
    owner = Owner(name="Jamie")
    rex = Pet(name="Rex", species="Dog", breed="Lab", age=3)
    luna = Pet(name="Luna", species="Cat", breed="Tabby", age=2)
    owner.add_pet(rex)
    owner.add_pet(luna)

    rex.add_task(_make_task(task_id="t1", preferred_time=time(13, 0)))
    luna.add_task(_make_task(task_id="t2", preferred_time=time(13, 0)))

    conflicts = owner.detect_conflicts()

    assert len(conflicts) == 1
    assert "13:00" in conflicts[0]


def test_detect_conflicts_returns_empty_list_when_no_overlap():
    owner = Owner(name="Jamie")
    pet = Pet(name="Rex", species="Dog", breed="Lab", age=3)
    owner.add_pet(pet)
    pet.add_task(_make_task(task_id="t1", preferred_time=time(7, 0)))
    pet.add_task(_make_task(task_id="t2", preferred_time=time(8, 0)))

    assert owner.detect_conflicts() == []


def test_detect_conflicts_on_pet_with_no_tasks_returns_empty_list():
    owner = Owner(name="Jamie")
    owner.add_pet(Pet(name="Rex", species="Dog", breed="Lab", age=3))

    assert owner.detect_conflicts() == []


# --- Filtering ----------------------------------------------------------------


def test_filter_tasks_by_completion_status():
    pet = Pet(name="Rex", species="Dog", breed="Lab", age=3)
    done_task = _make_task(task_id="t1")
    done_task.mark_done()
    pending_task = _make_task(task_id="t2")
    pet.add_task(done_task)
    pet.add_task(pending_task)

    assert pet.filter_tasks(is_done=True) == [done_task]
    assert pet.filter_tasks(is_done=False) == [pending_task]
    assert pet.filter_tasks() == [done_task, pending_task]
