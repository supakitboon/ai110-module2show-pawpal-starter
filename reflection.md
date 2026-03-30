# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial design included four classes: `Pet`, `Owner`, `Task`, and `Scheduler`.

- **`Pet`** holds the animal's name and species. Its only responsibility is to store and return basic pet information. It is a pure data object with no scheduling logic.
- **`Owner`** holds the owner's name and a list of their pets. It is responsible for grouping pet ownership — one owner can have one or more pets.
- **`Task`** represents a single care activity (e.g., walk, feed, groom). It stores the task title, duration in minutes, and a priority level (`"low"`, `"medium"`, or `"high"`). It is responsible for converting its priority label into a numeric value to support sorting.
- **`Scheduler`** is the only class with real behavior. It holds a reference to the owner and a list of tasks. It is responsible for accepting new tasks, ordering them by priority, fitting them within available time, and producing a human-readable explanation of the resulting plan.

`Pet` and `Task` were implemented as Python dataclasses to keep attribute definitions clean and concise. `Owner` was also a dataclass since it is primarily a data container. `Scheduler` was a regular class because it manages state and coordinates behavior across the other objects.

**b. Design changes**

After reviewing the skeleton, two problems were identified and fixed:

**1. Added `available_minutes` to `Scheduler`**
The original skeleton had no way to track how much time the owner has in a day. Without this, `generate_schedule()` could not enforce any time constraint — it would just return all tasks regardless of whether they fit. Adding `available_minutes` (defaulting to 480, i.e. 8 hours) gives the scheduler the budget it needs to skip or stop adding tasks when time runs out.

**2. Changed `priority: str` to `priority: Literal["low", "medium", "high"]`**
The original type hint allowed any string, meaning a typo like `"hig"` or an invalid value like `"urgent"` would pass silently and break sorting logic later. Using `Literal` from Python's `typing` module documents the valid values directly in the type signature and lets static analysis tools (like Pylance/mypy) catch mistakes early.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The scheduler uses a **greedy fit** approach: it walks through tasks sorted by priority and adds each one if its duration fits within the remaining time budget. If a task doesn't fit, it is skipped entirely — the scheduler does not try to rearrange earlier tasks or look ahead to find a better combination.

For example, if 15 minutes remain and there is a 20-minute low-priority task and a 10-minute low-priority task further down the list, the greedy approach skips the 20-minute task but may still pick up the 10-minute one. It does not backtrack to swap earlier choices for a more optimal total.

This is a reasonable tradeoff for a pet care app because the task list is small (typically under 10 items), simplicity matters more than perfect optimization, and the priority ordering is already the owner's stated preference. A full optimal packing algorithm (like 0/1 knapsack) would be more powerful but far harder to explain to a non-technical user.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
