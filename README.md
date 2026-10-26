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
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Schedule.sort_by_time()` | Sorts a list of `Task` objects by `preferred_time` (formatted as `"HH:MM"` for the sort key); untimed tasks sort last. Separate from `Schedule.generate_plan()`, which sorts by priority first and then by time while building the actual plan. |
| Filtering | `Pet.filter_tasks()`, `Owner.filter_tasks()`, `Owner.get_tasks_by_pet()` | Filter tasks by completion status (`is_done=True`/`False`/`None`) at the pet level or across every pet an owner has, or pull all tasks for one named pet. |
| Conflict handling | `Owner.detect_conflicts()` | Groups pending tasks across all of an owner's pets by exact `preferred_time` and returns a list of warning strings for any time with more than one task — same pet or different pets. Lightweight exact-match check, not full interval overlap (see `reflection.md`, section 2b). |
| Recurring tasks | `Task.create_next_occurrence()`, `Pet.complete_task()` | `Pet.complete_task(task_id)` marks a task done and, if it's recurring (`recurrence="daily"` or `"weekly"`), automatically creates and adds the next occurrence with its `due_date` advanced by `timedelta(days=1)` or `timedelta(weeks=1)`. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
