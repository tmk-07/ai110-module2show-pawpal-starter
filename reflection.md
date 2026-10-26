# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
1. add different types of tasks
2. be able to schedule tasks on a daily/weekly basis
3. display task schedules

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

task, pet, owner, and schedule were the classes. each respectively holds the info pertaining to it. for example, owner holds all data related to owner, and all the actions owners can take.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

--- yes - we made a minor change to Task, adding a variable for completion so we can modify the state of a given task. 

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: task priority (high/medium/low), each pet's available minutes for the day, and a task's preferred time. `Schedule.generate_plan()` sorts pending tasks by priority first, then by preferred time, so a high-priority task without a preferred time is still placed before a low-priority task with one. It then walks that ordered list, skipping any task whose duration would exceed the remaining minutes budget, so the day never over-commits. Priority mattered most to us because a pet owner's real failure mode is "I ran out of time and skipped something important" — ordering by priority first means if the day runs short, it's the low-priority tasks that get dropped, not the high-priority ones. Preferred time is used as a tiebreaker rather than a hard constraint, since in this version tasks aren't locked to their preferred time (see tradeoff below).

**b. Tradeoffs**

`Owner.detect_conflicts()` only flags tasks that share the exact same `preferred_time` value, rather than checking whether their `[start, start + duration]` windows overlap. For example, a 30-minute walk at 7:30 and a 15-minute feeding at 7:40 would actually overlap in real time, but the current check would miss it because the two `preferred_time` values differ. I chose this simpler check because it's cheap to compute (a single dictionary grouped by exact time, O(n) instead of an O(n²) pairwise interval comparison), it's easy to read and verify, and for the common case in this app — multiple tasks explicitly scheduled "at the same time" — it catches the conflicts a pet owner is most likely to create by accident. A full overlap check would catch more real conflicts but adds complexity that isn't justified yet for a small number of tasks per pet per day; it's a reasonable next iteration if the task list grows or durations become longer and more variable.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code throughout implementation, not just design brainstorming. It generated the initial class skeletons from my UML diagram, wrote the `generate_plan()` scheduling logic (sorting by priority then preferred time, tracking remaining minutes, building `ScheduleEntry` objects with a reason string), added the one-line docstrings across `pawpal_system.py`, and wrote `main.py` to exercise the whole system (owner, two pets, three tasks at different times, printed schedule). The most useful prompts were ones that referenced concrete classes and methods already in the file (e.g., "import classes from pawpal_system, create an owner and 2 pets...") rather than open-ended design questions — pointing at the real code let it produce output that matched the existing structure instead of inventing a new one.

**b. Judgment and verification**

AI suggestions were accepted when they matched the UML-derived class structure already in the repo (e.g., keeping `Schedule` scoped to a single pet rather than the whole owner, which kept `generate_plan()` simple). I verified correctness by actually running the generated code (`python3 main.py`) and checking that the printed schedule matched expectations — tasks appeared at their preferred times, sorted correctly, and the total-minutes math was right — rather than trusting the code just because it ran without errors. I also cross-checked new logic against the existing `tests/test_pawpal.py` cases (e.g., `mark_done` and `add_task` behavior) to make sure nothing the AI added broke assumptions the tests already depended on.

One suggestion I rejected: when adding conflict detection, the first instinct (mine and the AI's) was to implement full interval-overlap checking (comparing `[start, start+duration]` ranges pairwise across every task). I had the AI implement it, but the pairwise comparison was noticeably harder to read and reason about for a feature this small, and it was O(n²). I asked it to simplify to an exact-time-match check grouped by a dictionary keyed on `preferred_time` instead — less thorough, but easier to verify correct by inspection and fast enough for the realistic number of tasks a pet owner would enter in a day. That tradeoff is documented in section 2b above.

**c. AI strategy**

Two AI coding assistant features were most effective: (1) being able to reference the actual file (`pawpal_system.py`, `app.py`) in a prompt instead of describing the classes from memory — this consistently produced code that matched the existing structure rather than a generic reimplementation, and (2) running the code immediately after a change and feeding any error or unexpected output back into the same conversation, which turned debugging into a tight loop instead of a guessing game.

Using separate chat sessions for different phases (design/UML, core implementation, algorithmic features, testing, UI/polish) helped keep each conversation's context focused on one concern, so the AI's suggestions in, say, the testing phase weren't colored by unrelated UI discussion, and it was easier for me to review a session's full diff against a single, narrow goal instead of an entangled one.

The key takeaway on being the "lead architect": the AI is very good at producing code that compiles and looks reasonable, but it has no stake in the project's actual constraints (what a pet owner needs, which tradeoffs are acceptable, which abstractions are overkill). Those calls are mine to make — the AI can draft and explain options quickly, but I'm the one who has to decide if an output is actually the output I asked for and would still make sense to another engineer a year from now, and to push back when "more correct" (full interval overlap) came at the cost of "harder to read and no one needs it yet."

---

## 4. Testing and Verification

**a. What you tested**

The automated suite (`tests/test_pawpal.py`, 12 tests) covers completion state, sorting, recurrence, conflict detection, and filtering. These were the behaviors most likely to silently produce wrong output without crashing: a sort that's off by one still returns a list, a conflict check with a logic bug still returns a (wrong, possibly empty) list, and a recurrence calculation with the wrong `timedelta` still produces a date — none of these fail loudly on their own, so they needed explicit assertions. Edge cases specifically covered: an empty task list for sorting, an untimed task mixed with timed ones, a non-recurring task being completed (should spawn nothing), and a pet with zero tasks for conflict detection (should return no warnings, not raise).

**b. Confidence**

I'm fairly confident (see the 4/5 rating in `README.md`) in the sorting, recurrence, and filtering logic, since each has direct test coverage for both its happy path and the obvious edge cases. I'm less confident in two areas that aren't yet tested: `Schedule.generate_plan()`'s behavior right at the `available_minutes` boundary (e.g., a task whose duration exactly equals the remaining minutes, or multiple tasks that together exceed the budget by a small margin), and `Owner.detect_conflicts()`'s known blind spot for overlapping-but-not-identical times. If I had more time I'd add boundary tests for `generate_plan()` and extend conflict detection to true interval overlap with tests for partial overlaps, back-to-back (non-overlapping) tasks, and tasks that start at the same minute but have zero duration.

---

## 5. Reflection

**a. What went well**

The four-class design (`Task`, `Pet`, `Owner`, `Schedule`) held up well all the way through adding sorting, recurrence, filtering, and conflict detection — none of those features required restructuring the original classes, just adding focused methods to the ones that already owned the relevant data (e.g., recurrence logic lives on `Task`/`Pet` because that's who owns task state; conflict detection lives on `Owner` because it needs visibility across pets). I'm most satisfied with how cleanly that scaled.

**b. What you would improve**

I'd replace the exact-time-match conflict check with real interval overlap once the task model has more realistic durations, and I'd add a `due_date`-aware filter so recurring tasks that are now overdue can be surfaced distinctly from tasks that are merely pending. I'd also tighten `generate_plan()`'s boundary behavior (see section 4b) and add tests for it.

**c. Key takeaway**

Designing the domain model (who owns what data, who's responsible for which decision) mattered more than any individual algorithm — once `Task`, `Pet`, `Owner`, and `Schedule` had clear, non-overlapping responsibilities, every new feature had an obvious home and didn't require renegotiating the architecture. Working with AI reinforced that this architectural judgment is the part that has to stay mine: the AI could generate a correct-looking method for almost any request, but only I could tell whether that method belonged on `Task` versus `Pet` versus `Owner`, and whether a "more correct" version was worth the added complexity for this project.
