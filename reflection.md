# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial design included four classes: `Pet`, `Owner`, `Task`, and `Scheduler`.

- **`Pet`** holds the animal's name and species. Its only responsibility is to store and return basic pet information. It is a pure data object with no scheduling logic.
- **`Owner`** holds the owner's name and a list of their pets. It is responsible for grouping pet ownership. One owner can have one or more pets.
- **`Task`** represents a single care activity (e.g., walk, feed, groom). It stores the task title, duration in minutes, and a priority level (`"low"`, `"medium"`, or `"high"`). It is responsible for converting its priority label into a numeric value to support sorting.
- **`Scheduler`** is the only class with real behavior. It holds a reference to the owner and a list of tasks. It is responsible for accepting new tasks, ordering them by priority, fitting them within available time, and producing a human-readable explanation of the resulting plan.

`Pet` and `Task` were implemented as Python dataclasses to keep attribute definitions clean and concise. `Owner` was also a dataclass since it is primarily a data container. `Scheduler` was a regular class because it manages state and coordinates behavior across the other objects.

**b. Design changes**

After reviewing the skeleton, two problems were identified and fixed:

**1. Added `available_minutes` to `Scheduler`**
The original skeleton had no way to track how much time the owner has in a day. Without this, `generate_schedule()` could not enforce any time constraint. It would just return all tasks regardless of whether they fit. Adding `available_minutes` (defaulting to 480, i.e. 8 hours) gives the scheduler the budget it needs to skip or stop adding tasks when time runs out.

**2. Changed `priority: str` to `priority: Literal["low", "medium", "high"]`**
The original type hint allowed any string, meaning a typo like `"hig"` or an invalid value like `"urgent"` would pass silently and break sorting logic later. Using `Literal` from Python's `typing` module documents the valid values directly in the type signature and lets static analysis tools (like Pylance/mypy) catch mistakes early.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two hard constraints: **available time** (the owner's daily minute budget) and **task completion status** (only pending tasks are eligible). Within those constraints, it uses **priority** as the primary ordering signal and **duration** as a tiebreaker.

Priority mattered most because it directly reflects the owner's intent. A missed medication is more serious than a missed grooming session. Duration as a tiebreaker was chosen because, when two tasks are equally urgent, fitting the shorter one first leaves more time for everything else.

**b. Tradeoffs**

The scheduler uses a **greedy fit** approach: it walks through tasks sorted by priority and adds each one if its duration fits within the remaining time budget. If a task doesn't fit, it is skipped entirely. The scheduler does not try to rearrange earlier tasks or look ahead to find a better combination.

For example, if 15 minutes remain and there is a 20-minute low-priority task and a 10-minute low-priority task further down the list, the greedy approach skips the 20-minute task but may still pick up the 10-minute one. It does not backtrack to swap earlier choices for a more optimal total.

This is a reasonable tradeoff for a pet care app because the task list is small (typically under 10 items), simplicity matters more than perfect optimization, and the priority ordering is already the owner's stated preference. A full optimal packing algorithm (like 0/1 knapsack) would be more powerful but far harder to explain to a non-technical user.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used across every phase, but with different roles at each stage:

- **Design brainstorming (Phase 1):** Used Copilot Chat with prompts like *"What attributes and methods should a Task class need if it supports recurring schedules?"* to stress-test the UML before writing any code. This surfaced `frequency` and `due_date` as necessary fields that the original sketch was missing.
- **Implementation (Phase 2):** Used inline Copilot completions to generate boilerplate: dataclass field definitions, `__repr__` formatting, and `timedelta` arithmetic. The most effective prompts were specific and scoped: *"Write `mark_complete()` so it returns a new Task with the next due date based on frequency"* rather than asking for the whole class at once.
- **Testing (Phase 3):** Used `#codebase` chat to ask *"What edge cases should I test for a greedy scheduler with a time budget?"* This produced a complete list of boundary conditions (0-minute budget, exact fit, same-priority tiebreaker) that would have taken much longer to enumerate manually.
- **UI (Phase 4):** Used Copilot to draft the Streamlit layout structure, then edited each section to wire in the real `Scheduler` methods.

The most effective prompt pattern throughout was: **provide context + state the constraint + ask for one specific thing.** Broad prompts like *"build the scheduler"* produced over-engineered responses; narrow prompts like *"write `get_dropped_tasks()` using the result of `generate_schedule()`"* produced code that fit the existing design cleanly.

**b. Judgment and verification**

The clearest rejection came during the `get_dropped_tasks()` implementation. Copilot suggested tracking dropped tasks by adding a `dropped: bool` flag directly to the `Task` dataclass and setting it inside `generate_schedule()`. The suggestion was technically functional, but it violated the single-responsibility principle: `Task` is a data object and should not carry scheduling state. Accepting it would have meant every test for recurrence or priority would also need to account for this flag.

The approach was replaced with a stateless design: `get_dropped_tasks()` calls `generate_schedule()` internally and computes the difference using a set of scheduled titles. The `Task` class remained a pure data container with no knowledge of whether it was scheduled or not.

Verification was done by writing tests first for the expected behavior, then checking that the AI-suggested version failed those tests, and the revised version passed them. This made the rejection concrete rather than just a gut feeling about code style.

---

## 4. Testing and Verification

**a. What you tested**

Fifteen tests were written across three categories:

- **Sorting correctness**: verified that `sort_by_time()` returns tasks in ascending duration order, that `generate_schedule()` places high-priority tasks before low-priority ones, and that equal-priority tasks are broken by duration (shorter first). These were important because a sorting bug is silent. The schedule runs without errors but produces wrong output.
- **Recurrence logic**: confirmed that daily tasks produce a next-day due date, weekly tasks advance by 7 days, and `as-needed` tasks return `None`. Also verified that `Pet.complete_task()` appends the next occurrence to the pet's task list for recurring tasks but does not append anything for one-off tasks. These tests mattered because recurrence is stateful. A missed append means a care task disappears permanently.
- **Budget and conflict detection**: tested zero-minute budgets, exact-fit tasks, tasks that exceed remaining time, and an all-complete pet producing an empty schedule. These guard the boundary conditions where the greedy algorithm is most likely to behave unexpectedly.

**b. Confidence**

**Confidence Level: ★★★★☆ (4/5)**

The core scheduling behaviors are well-covered and all 15 tests pass. The one star held back reflects two known gaps: `get_dropped_tasks()` uses title-based deduplication, which would misidentify two different tasks that happen to share the same title as one; and there are no integration tests covering an owner with multiple pets whose tasks interact during scheduling. Those are the next two tests to write.

---

## 5. Reflection

**a. What went well**

The part of this project I'm most satisfied with is the recurrence system. `mark_complete()` returning a new `Task` instance rather than mutating the original kept the data model clean. Completed tasks are preserved in history, and the next occurrence is a fresh object with no leftover state. That decision made testing straightforward and the UI logic simple: pending tasks are always just `pet.get_pending_tasks()`, with no need to filter by date or check flags.

The AI strategy section of this reflection also reflects real decisions made during the build, not retrofitted answers. The `get_dropped_tasks()` redesign (see Section 3b) was a genuine moment where understanding the design mattered more than accepting working code.

**b. What you would improve**

Two things stand out:

First, `get_dropped_tasks()` should match tasks by object identity or a unique ID rather than title string. The current approach breaks silently if two tasks share a name. A simple `id()` comparison or an auto-generated UUID field on `Task` would fix this without changing the rest of the system.

Second, the Streamlit session state resets the entire owner and pet on every "Save profile" click, which wipes all existing tasks. A real app would separate profile creation from profile editing, or at least warn the user before overwriting their task list.

**c. Key takeaway**

The most important thing learned about collaborating with AI tools is that **the AI is fastest when you are clearest about the boundary**. Every time a prompt described what one method should do, what it should return, and what it should not touch, the suggestion was useful on the first try. Every time the prompt was open-ended ("build the scheduler"), the response was over-engineered and required significant trimming.

Being the lead architect means deciding where the boundaries are before asking the AI anything. The design decisions (what each class owns, what it delegates, what state it is allowed to hold) have to come from the developer. Once those decisions exist, AI becomes a very fast way to fill them in correctly. Without them, it produces code that works but doesn't belong to any coherent design.
