from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner(name="Alex")
dog = Pet(name="Biscuit", species="Dog")
cat = Pet(name="Luna", species="Cat")

dog.add_task(Task(title="Morning walk",   duration=30, priority="high",   frequency="daily"))
dog.add_task(Task(title="Brush fur",      duration=15, priority="low",    frequency="weekly"))
cat.add_task(Task(title="Clean litter",   duration=10, priority="medium", frequency="daily"))
cat.add_task(Task(title="Vet check",      duration=60, priority="high",   frequency="as-needed"))

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner=owner, available_minutes=60)

# ── Before completion ─────────────────────────────────────────────────────────
print("=== All tasks BEFORE completion ===")
for t in owner.get_all_tasks():
    print(f"  {t}")

# Complete "Morning walk" (daily) and "Brush fur" (weekly)
morning_walk = dog.tasks[0]
brush_fur = dog.tasks[1]
vet_check = cat.tasks[1]

next_walk = dog.complete_task(morning_walk)
next_brush = dog.complete_task(brush_fur)
next_vet = cat.complete_task(vet_check)  # as-needed — should NOT recur

print("\n=== Recurrence results ===")
print(f"  Morning walk next due: {next_walk.due_date if next_walk else 'no recurrence'}")
print(f"  Brush fur next due:    {next_brush.due_date if next_brush else 'no recurrence'}")
print(f"  Vet check next due:    {next_vet.due_date if next_vet else 'no recurrence (as-needed)'}")

# ── After completion ──────────────────────────────────────────────────────────
print("\n=== All tasks AFTER completion (completed + new recurrences) ===")
for t in owner.get_all_tasks():
    print(f"  {t}")

print("\n=== Pending tasks only ===")
for t in owner.get_all_pending_tasks():
    print(f"  {t}")

# ── Schedule ──────────────────────────────────────────────────────────────────
print("\n=== Today's Schedule ===")
print(scheduler.explain_schedule())
