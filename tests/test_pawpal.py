from pawpal_system import Pet, Task, TaskCategory, Priority


def _make_task(task_id="t1"):
    return Task(
        task_id=task_id,
        name="Walk",
        category=TaskCategory.WALK,
        duration_minutes=30,
        priority=Priority.MEDIUM,
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
