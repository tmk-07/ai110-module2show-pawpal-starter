"""PawPal+ domain model skeleton, generated from diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
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

    def mark_done(self) -> None:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError


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
        raise NotImplementedError

    def total_scheduled_minutes(self) -> int:
        raise NotImplementedError

    def explain_plan(self) -> str:
        raise NotImplementedError
