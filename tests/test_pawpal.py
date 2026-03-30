from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ─── Existing tests ─────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feed", duration=10, priority="medium"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Walk", duration=20, priority="high"))
    assert len(pet.tasks) == 2


# ─── Sorting Correctness ────────────────────────────────────────────────────────

def test_sort_by_time_returns_shortest_first():
    """sort_by_time() should return tasks ordered by duration ascending."""
    tasks = [
        Task(title="Groom", duration=45, priority="low"),
        Task(title="Feed", duration=10, priority="medium"),
        Task(title="Walk", duration=30, priority="high"),
    ]
    owner = Owner(name="Alex", pets=[Pet(name="Biscuit", species="Dog", tasks=tasks)])
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.sort_by_time(tasks)
    durations = [t.duration for t in sorted_tasks]
    assert durations == sorted(durations), "Tasks should be in ascending duration order"


def test_generate_schedule_orders_by_priority_descending():
    """generate_schedule() should place high-priority tasks before low-priority ones."""
    pet = Pet(name="Luna", species="Cat")
    pet.add_task(Task(title="Trim nails", duration=15, priority="low"))
    pet.add_task(Task(title="Give medicine", duration=10, priority="high"))
    pet.add_task(Task(title="Brush fur", duration=20, priority="medium"))

    owner = Owner(name="Alex", pets=[pet])
    scheduler = Scheduler(owner, available_minutes=120)

    schedule = scheduler.generate_schedule()
    priorities = [t.priority_value() for t in schedule]
    assert priorities == sorted(priorities, reverse=True), (
        "Schedule should list highest-priority tasks first"
    )


def test_generate_schedule_breaks_priority_ties_by_shortest_duration():
    """When two tasks share the same priority, the shorter one should appear first."""
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task(title="Long walk", duration=60, priority="high"))
    pet.add_task(Task(title="Quick feed", duration=10, priority="high"))

    owner = Owner(name="Alex", pets=[pet])
    scheduler = Scheduler(owner, available_minutes=120)

    schedule = scheduler.generate_schedule()
    assert schedule[0].title == "Quick feed", (
        "Shorter task should come first when priority is equal"
    )
    assert schedule[1].title == "Long walk"


# ─── Recurrence Logic ──────────────────────────────────────────────────────────

def test_daily_task_recurs_next_day():
    """Completing a daily task should return a new task due the following day."""
    today = date.today()
    task = Task(title="Morning walk", duration=30, priority="high",
                frequency="daily", due_date=today)
    next_task = task.mark_complete()

    assert next_task is not None, "Daily task should produce a next occurrence"
    assert next_task.due_date == today + timedelta(days=1), (
        "Next daily task should be due tomorrow"
    )
    assert next_task.completed is False, "Next occurrence should start as pending"
    assert next_task.title == task.title


def test_weekly_task_recurs_seven_days_later():
    """Completing a weekly task should return a new task due 7 days later."""
    today = date.today()
    task = Task(title="Bath time", duration=40, priority="medium",
                frequency="weekly", due_date=today)
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_as_needed_task_does_not_recur():
    """Completing an as-needed task should return None — no automatic recurrence."""
    task = Task(title="Vet visit", duration=90, priority="high", frequency="as-needed")
    next_task = task.mark_complete()

    assert next_task is None, "as-needed tasks should not auto-generate a next occurrence"


def test_complete_task_on_pet_appends_next_occurrence():
    """Pet.complete_task() should append the next daily task to the pet's task list."""
    pet = Pet(name="Biscuit", species="Dog")
    walk = Task(title="Walk", duration=30, priority="high", frequency="daily")
    pet.add_task(walk)

    pet.complete_task(walk)

    assert len(pet.tasks) == 2, "Next occurrence should be appended to pet.tasks"
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False


def test_complete_as_needed_task_does_not_append():
    """Pet.complete_task() on as-needed task should NOT add a new task."""
    pet = Pet(name="Luna", species="Cat")
    vet = Task(title="Vet check", duration=60, priority="high", frequency="as-needed")
    pet.add_task(vet)

    pet.complete_task(vet)

    assert len(pet.tasks) == 1, "No new task should be appended for as-needed frequency"


# ─── Conflict / Time Budget Detection ──────────────────────────────────────────

def test_tasks_with_same_duration_both_scheduled_when_budget_allows():
    """Two tasks with identical durations should both be scheduled if budget permits."""
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task(title="Walk", duration=30, priority="high"))
    pet.add_task(Task(title="Feed", duration=30, priority="high"))

    owner = Owner(name="Alex", pets=[pet])
    scheduler = Scheduler(owner, available_minutes=60)

    schedule = scheduler.generate_schedule()
    assert len(schedule) == 2, "Both same-duration tasks should fit when budget is sufficient"


def test_scheduler_drops_task_that_exceeds_remaining_time():
    """A task that pushes total duration over the budget should appear in dropped tasks."""
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task(title="High prio big task", duration=50, priority="high"))
    pet.add_task(Task(title="Low prio small task", duration=20, priority="low"))

    # Budget 60: high-prio (50 min) fits, leaves 10 min — low-prio (20 min) does not fit
    owner = Owner(name="Alex", pets=[pet])
    scheduler = Scheduler(owner, available_minutes=60)

    scheduled_titles = [t.title for t in scheduler.generate_schedule()]
    dropped_titles = [t.title for t in scheduler.get_dropped_tasks()]

    assert "High prio big task" in scheduled_titles
    assert "Low prio small task" in dropped_titles, (
        "Task exceeding remaining budget should appear in dropped tasks"
    )


def test_zero_minute_budget_drops_all_tasks():
    """With 0 available minutes, every pending task should be dropped."""
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task(title="Walk", duration=30, priority="high"))
    pet.add_task(Task(title="Feed", duration=10, priority="medium"))

    owner = Owner(name="Alex", pets=[pet])
    scheduler = Scheduler(owner, available_minutes=0)

    assert scheduler.generate_schedule() == [], "No tasks should be scheduled with 0 minutes"
    assert len(scheduler.get_dropped_tasks()) == 2, "All tasks should be dropped"


def test_task_exactly_filling_budget_is_scheduled():
    """A single task whose duration exactly equals available_minutes should be scheduled."""
    pet = Pet(name="Luna", species="Cat")
    pet.add_task(Task(title="Long groom", duration=120, priority="medium"))

    owner = Owner(name="Alex", pets=[pet])
    scheduler = Scheduler(owner, available_minutes=120)

    schedule = scheduler.generate_schedule()
    assert len(schedule) == 1
    assert schedule[0].title == "Long groom"
    assert scheduler.get_dropped_tasks() == []


def test_no_pending_tasks_produces_empty_schedule():
    """A pet with all tasks already completed should result in an empty schedule."""
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(title="Walk", duration=30, priority="high")
    task.mark_complete()
    pet.add_task(task)

    owner = Owner(name="Alex", pets=[pet])
    scheduler = Scheduler(owner, available_minutes=480)

    assert scheduler.generate_schedule() == []
    assert scheduler.get_dropped_tasks() == []
