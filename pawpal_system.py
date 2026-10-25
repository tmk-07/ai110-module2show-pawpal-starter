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

    def mark_done(self) -> None:
        self.is_done = True


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [task for task in self.tasks if task.task_id != task_id]


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        return [task for pet in self.pets for task in pet.tasks]


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

    def generate_plan(self, tasks: list[Task]) -> list[ScheduleEntry]:
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
        return sum(entry.task.duration_minutes for entry in self.entries)

    def explain_plan(self) -> str:
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
