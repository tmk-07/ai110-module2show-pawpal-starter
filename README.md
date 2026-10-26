# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Implementation Summary

PawPal+ models pet care scheduling with four cooperating classes in `pawpal_system.py`:

- **`Task`** holds a single care item (name, category, duration, priority, optional preferred time/recurrence) and tracks its own completion via `mark_done()`.
- **`Pet`** owns a list of `Task` objects and exposes `add_task()`/`remove_task()` to manage them.
- **`Owner`** owns a list of `Pet` objects and can `add_pet()` or roll up every task across all pets with `get_all_tasks()`.
- **`Schedule`** takes a `Pet` and a list of tasks and turns them into a concrete daily plan: `generate_plan()` sorts pending tasks by priority (high → low) and then by preferred time, lays them out sequentially starting at a fixed day-start time, and skips any task that would exceed the available minutes budget. Each placed task becomes a `ScheduleEntry` (start/end time plus a plain-language reason it was placed there). `total_scheduled_minutes()` and `explain_plan()` summarize the result.

`main.py` ties these together end-to-end: it creates an `Owner`, two `Pet`s, assigns three `Task`s with different preferred times, builds a `Schedule` per pet, and prints each pet's schedule for the current date. `app.py` wires the same classes into a Streamlit UI for interactive use.

The UML class diagram in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd) reflects the final implementation above, including methods added after the initial draft (`Task.create_next_occurrence()`, `Pet.complete_task()`, `Pet.filter_tasks()`, `Owner.filter_tasks()`/`get_tasks_by_pet()`/`detect_conflicts()`, and `Schedule.sort_by_time()`).

## Features

- **Owner & pet management** — create an owner, add any number of pets, and switch between them in the UI (`Owner.add_pet()`, `Pet` dataclass).
- **Task creation** — add tasks with a name, duration, priority, optional preferred time, and optional daily/weekly recurrence.
- **Sorting by time** — `Schedule.sort_by_time()` returns a pet's tasks in chronological order (untimed tasks last); the Streamlit task table always displays in this order.
- **Priority-aware daily scheduling** — `Schedule.generate_plan()` builds a concrete day plan: high-priority tasks are placed first, pending tasks are laid out starting at a fixed day-start time, and anything that would blow the available-minutes budget is skipped. `explain_plan()` prints a plain-language reason for each placement.
- **Filtering** — `Pet.filter_tasks()` / `Owner.filter_tasks()` return just the done or pending tasks for a pet or across an owner's whole household; `Owner.get_tasks_by_pet()` pulls one pet's tasks by name.
- **Daily recurrence** — `Pet.complete_task()` marks a task done and, if it recurs, automatically creates the next occurrence via `Task.create_next_occurrence()` (due one day later for `"daily"`, one week later for `"weekly"`).
- **Conflict warnings** — `Owner.detect_conflicts()` scans every pet's tasks for ones sharing the exact same preferred time and returns warning strings (instead of raising), which the UI renders as `st.warning` banners so a pet owner immediately sees a double-booking.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
Schedule for Luna on 2026-10-24:
- 18:00-18:20 Evening Grooming: Scheduled at its preferred time (Low priority).
Total scheduled: 20/480 minutes.
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

`tests/test_pawpal.py` covers both happy paths and edge cases for the core scheduling behaviors:

- **Completion**: marking a task done flips `is_done`; adding a task increases a pet's task count.
- **Sorting** (`Schedule.sort_by_time()`): tasks come back in chronological order; untimed tasks sort last; an empty list returns an empty list.
- **Recurrence** (`Pet.complete_task()`, `Task.create_next_occurrence()`): completing a `"daily"` task auto-creates the next occurrence one day later, a `"weekly"` task one week later, and completing a non-recurring task creates nothing.
- **Conflict detection** (`Owner.detect_conflicts()`): two tasks (same pet or different pets) at the same `preferred_time` are flagged, non-overlapping times are not, and a pet with no tasks produces no conflicts.
- **Filtering** (`Pet.filter_tasks()`): tasks can be filtered by completion status or returned unfiltered.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-8.3.4, pluggy-1.5.0
rootdir: /Users/timmy/ai110-module2show-pawpal-starter
plugins: anyio-4.7.0
collected 12 items

tests/test_pawpal.py::test_mark_done_changes_task_status PASSED          [  8%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 16%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 25%]
tests/test_pawpal.py::test_sort_by_time_places_untimed_tasks_last PASSED [ 33%]
tests/test_pawpal.py::test_sort_by_time_on_empty_list_returns_empty_list PASSED [ 41%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_occurrence PASSED [ 50%]
tests/test_pawpal.py::test_completing_weekly_task_creates_occurrence_one_week_later PASSED [ 58%]
tests/test_pawpal.py::test_completing_non_recurring_task_does_not_create_new_task PASSED [ 66%]
tests/test_pawpal.py::test_detect_conflicts_flags_two_tasks_at_the_same_time PASSED [ 75%]
tests/test_pawpal.py::test_detect_conflicts_returns_empty_list_when_no_overlap PASSED [ 83%]
tests/test_pawpal.py::test_detect_conflicts_on_pet_with_no_tasks_returns_empty_list PASSED [ 91%]
tests/test_pawpal.py::test_filter_tasks_by_completion_status PASSED      [100%]

============================== 12 passed in 0.01s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5) — all core sorting, recurrence, filtering, and conflict-detection behaviors are covered and passing. One star withheld because conflict detection only checks exact time matches rather than overlapping durations (see `reflection.md`, section 2b), and `generate_plan()`'s interaction with the day-end/available-minutes boundary isn't yet covered by a dedicated test.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Schedule.sort_by_time()` | Sorts a list of `Task` objects by `preferred_time` (formatted as `"HH:MM"` for the sort key); untimed tasks sort last. Separate from `Schedule.generate_plan()`, which sorts by priority first and then by time while building the actual plan. |
| Filtering | `Pet.filter_tasks()`, `Owner.filter_tasks()`, `Owner.get_tasks_by_pet()` | Filter tasks by completion status (`is_done=True`/`False`/`None`) at the pet level or across every pet an owner has, or pull all tasks for one named pet. |
| Conflict handling | `Owner.detect_conflicts()` | Groups pending tasks across all of an owner's pets by exact `preferred_time` and returns a list of warning strings for any time with more than one task — same pet or different pets. Lightweight exact-match check, not full interval overlap (see `reflection.md`, section 2b). |
| Recurring tasks | `Task.create_next_occurrence()`, `Pet.complete_task()` | `Pet.complete_task(task_id)` marks a task done and, if it's recurring (`recurrence="daily"` or `"weekly"`), automatically creates and adds the next occurrence with its `due_date` advanced by `timedelta(days=1)` or `timedelta(weeks=1)`. |

## 📸 Demo Walkthrough

### Streamlit app (`app.py`)

The UI lets a user:

- Enter an **owner name**, which is kept in `st.session_state` so it survives Streamlit's rerun-on-every-click behavior.
- **Add a pet** (name, species, breed) and switch between pets with a selector once more than one exists.
- **Add a task** for the selected pet, with a title, duration, priority, an optional preferred time, and an optional recurrence (`none`/`daily`/`weekly`).
- See that pet's tasks in a table that is always **sorted by time** (via `Schedule.sort_by_time()`), with status (`✅ done` / `⏳ pending`) and recurrence shown per row.
- **Mark a pending task complete**; if it's recurring, the app confirms the next occurrence was added and shows its new due date.
- **Generate the day's schedule** for the selected pet, which calls `Schedule.generate_plan()` and prints the resulting plan with `explain_plan()`.
- See **conflict warnings** as soon as two tasks (for the same pet, or across different pets) share a preferred time — rendered as `st.warning` banners above the task table, so the owner notices a double-booking before they even generate a schedule, rather than discovering it buried in a schedule printout.

Example workflow: add pet "Mochi" → add a 7:30 AM "Morning walk" task → add a second pet "Milo" → add a 7:30 AM task for Milo too → a conflict warning appears immediately ("Conflict at 07:30: Mochi's Morning walk, Milo's ... are all scheduled at the same time") → generate the schedule for either pet to see it placed and explained.

### CLI demo (`main.py`)

`main.py` builds an owner with two pets, adds tasks out of chronological order (including one recurring daily task and two tasks that intentionally collide at 13:00), then exercises every algorithmic feature end-to-end. Sample output from `python3 main.py`:

```
=== Sorting demo: Rex's tasks sorted by time ===
- 07:30:00: Morning Walk
- 13:00:00: Afternoon Feeding
- 18:00:00: Evening Grooming

=== Recurring task demo ===
Before completing: Morning Walk is_done=False
After completing: Morning Walk is_done=True
Next occurrence auto-created: T1-next-2026-10-27, due 2026-10-27

=== Filtering demo ===
Rex's completed tasks: ['Morning Walk']
Rex's pending tasks: ['Evening Grooming', 'Afternoon Feeding', 'Morning Walk']
All of Luna's tasks: ['Litter Box Cleaning']

=== Conflict detection demo ===
WARNING: Conflict at 13:00: Rex's Afternoon Feeding, Luna's Litter Box Cleaning are all scheduled at the same time.

=== Daily schedule ===
Schedule for Rex on 2026-10-26:
- 07:30-08:00 Morning Walk: Scheduled at its preferred time (High priority).
- 13:00-13:15 Afternoon Feeding: Scheduled at its preferred time (Medium priority).
- 18:00-18:20 Evening Grooming: Scheduled at its preferred time (Low priority).
Total scheduled: 65/480 minutes.

Schedule for Luna on 2026-10-26:
- 13:00-13:10 Litter Box Cleaning: Scheduled at its preferred time (Medium priority).
Total scheduled: 10/480 minutes.
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
