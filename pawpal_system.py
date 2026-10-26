"""PawPal+ domain model skeleton, generated from diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum, auto


class TaskCategory(Enum):
    WALK = auto()
    FEEDING = auto()
    MEDICATION = auto()
    GROOMING = auto()
    ENRICHMENT = auto()
    OTHER = auto()


class Priority(Enum):
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
_DAY_START = time(7, 0)
_RECURRENCE_DELTAS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _add_minutes(start: time, minutes: int) -> time:
    return (datetime.combine(date.today(), start) + timedelta(minutes=minutes)).time()


@dataclass
class Task:
    task_id: str
    name: str
    category: TaskCategory
    duration_minutes: int
    priority: Priority
    is_recurring: bool = False
    recurrence: str | None = None
    preferred_time: time | None = None
    is_done: bool = False
    due_date: date | None = None

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.is_done = True

    def create_next_occurrence(self) -> Task | None:
        """Return a fresh, not-done copy of this task due on its next recurrence date, or None if it doesn't recur."""
        if not self.is_recurring or self.recurrence not in _RECURRENCE_DELTAS:
            return None

        next_due_date = (self.due_date or date.today()) + _RECURRENCE_DELTAS[self.recurrence]
        return Task(
            task_id=f"{self.task_id}-next-{next_due_date.isoformat()}",
            name=self.name,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            is_recurring=self.is_recurring,
            recurrence=self.recurrence,
            preferred_time=self.preferred_time,
            due_date=next_due_date,
        )


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id from this pet's task list."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def complete_task(self, task_id: str) -> Task | None:
        """Mark a task done and, if it recurs, automatically add its next occurrence."""
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task is None:
            return None

        task.mark_done()
        next_task = task.create_next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task

    def filter_tasks(self, is_done: bool | None = None) -> list[Task]:
        """Return this pet's tasks, optionally filtered by completion status."""
        if is_done is None:
            return list(self.tasks)
        return [task for task in self.tasks if task.is_done == is_done]


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_tasks_by_pet(self, pet_name: str) -> list[Task]:
        """Return the tasks belonging to the pet with the given name."""
        return [task for pet in self.pets for task in pet.tasks if pet.name == pet_name]

    def filter_tasks(self, is_done: bool | None = None) -> list[Task]:
        """Return tasks across all pets, optionally filtered by completion status."""
        tasks = self.get_all_tasks()
        if is_done is None:
            return tasks
        return [task for task in tasks if task.is_done == is_done]

    def detect_conflicts(self) -> list[str]:
        """Return a warning message for each pair of tasks scheduled at the same preferred time.

        This is a lightweight check (exact time match only, not overlapping durations) so it can
        flag likely scheduling problems without crashing the program.
        """
        warnings: list[str] = []
        by_time: dict[time, list[tuple[Pet, Task]]] = {}
        for pet in self.pets:
            for task in pet.tasks:
                if task.preferred_time is None or task.is_done:
                    continue
                by_time.setdefault(task.preferred_time, []).append((pet, task))

        for scheduled_time, scheduled in by_time.items():
            if len(scheduled) < 2:
                continue
            names = ", ".join(f"{pet.name}'s {task.name}" for pet, task in scheduled)
            warnings.append(
                f"Conflict at {scheduled_time.strftime('%H:%M')}: {names} are all scheduled at the same time."
            )
        return warnings


@dataclass
class ScheduleEntry:
    task: Task
    start_time: time
    end_time: time
    reason: str


@dataclass
class Schedule:
    pet: Pet
    schedule_date: date
    available_minutes: int
    entries: list[ScheduleEntry] = field(default_factory=list)

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by preferred_time, with untimed tasks placed last."""
        return sorted(
            tasks,
            key=lambda task: task.preferred_time.strftime("%H:%M") if task.preferred_time else "99:99",
        )

    def generate_plan(self, tasks: list[Task]) -> list[ScheduleEntry]:
        """Build and store a time-ordered schedule from the given tasks, by priority then preferred time."""
        pending = [task for task in tasks if not task.is_done]
        pending.sort(
            key=lambda task: (
                _PRIORITY_ORDER[task.priority],
                task.preferred_time or _DAY_START,
            )
        )

        entries: list[ScheduleEntry] = []
        remaining_minutes = self.available_minutes
        current_time = _DAY_START

        for task in pending:
            if task.duration_minutes > remaining_minutes:
                continue

            start_time = max(current_time, task.preferred_time or current_time)
            end_time = _add_minutes(start_time, task.duration_minutes)

            if task.preferred_time and task.preferred_time >= current_time:
                reason = f"Scheduled at its preferred time ({task.priority.name.title()} priority)."
            else:
                reason = f"Next available slot for a {task.priority.name.title()} priority task."

            entries.append(
                ScheduleEntry(
                    task=task,
                    start_time=start_time,
                    end_time=end_time,
                    reason=reason,
                )
            )

            remaining_minutes -= task.duration_minutes
            current_time = end_time

        self.entries = entries
        return entries

    def total_scheduled_minutes(self) -> int:
        """Return the total minutes scheduled across all entries."""
        return sum(entry.task.duration_minutes for entry in self.entries)

    def explain_plan(self) -> str:
        """Return a human-readable summary of the generated schedule."""
        if not self.entries:
            return f"No tasks scheduled for {self.pet.name} on {self.schedule_date}."

        lines = [f"Schedule for {self.pet.name} on {self.schedule_date}:"]
        for entry in self.entries:
            lines.append(
                f"- {entry.start_time.strftime('%H:%M')}-{entry.end_time.strftime('%H:%M')} "
                f"{entry.task.name}: {entry.reason}"
            )
        lines.append(
            f"Total scheduled: {self.total_scheduled_minutes()}/{self.available_minutes} minutes."
        )
        return "\n".join(lines)
