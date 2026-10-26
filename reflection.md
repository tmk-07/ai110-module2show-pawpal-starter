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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

`Owner.detect_conflicts()` only flags tasks that share the exact same `preferred_time` value, rather than checking whether their `[start, start + duration]` windows overlap. For example, a 30-minute walk at 7:30 and a 15-minute feeding at 7:40 would actually overlap in real time, but the current check would miss it because the two `preferred_time` values differ. I chose this simpler check because it's cheap to compute (a single dictionary grouped by exact time, O(n) instead of an O(n²) pairwise interval comparison), it's easy to read and verify, and for the common case in this app — multiple tasks explicitly scheduled "at the same time" — it catches the conflicts a pet owner is most likely to create by accident. A full overlap check would catch more real conflicts but adds complexity that isn't justified yet for a small number of tasks per pet per day; it's a reasonable next iteration if the task list grows or durations become longer and more variable.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code throughout implementation, not just design brainstorming. It generated the initial class skeletons from my UML diagram, wrote the `generate_plan()` scheduling logic (sorting by priority then preferred time, tracking remaining minutes, building `ScheduleEntry` objects with a reason string), added the one-line docstrings across `pawpal_system.py`, and wrote `main.py` to exercise the whole system (owner, two pets, three tasks at different times, printed schedule). The most useful prompts were ones that referenced concrete classes and methods already in the file (e.g., "import classes from pawpal_system, create an owner and 2 pets...") rather than open-ended design questions — pointing at the real code let it produce output that matched the existing structure instead of inventing a new one.

**b. Judgment and verification**

AI suggestions were accepted when they matched the UML-derived class structure already in the repo (e.g., keeping `Schedule` scoped to a single pet rather than the whole owner, which kept `generate_plan()` simple). I verified correctness by actually running the generated code (`python3 main.py`) and checking that the printed schedule matched expectations — tasks appeared at their preferred times, sorted correctly, and the total-minutes math was right — rather than trusting the code just because it ran without errors. I also cross-checked new logic against the existing `tests/test_pawpal.py` cases (e.g., `mark_done` and `add_task` behavior) to make sure nothing the AI added broke assumptions the tests already depended on.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
