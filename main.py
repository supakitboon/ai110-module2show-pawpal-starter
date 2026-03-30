from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner(name="Alex")

# Create pets
dog = Pet(name="Biscuit", species="Dog")
cat = Pet(name="Luna", species="Cat")

# Add tasks to Biscuit (dog)
dog.add_task(Task(title="Morning walk", duration=30, priority="high", frequency="daily"))
dog.add_task(Task(title="Feed breakfast", duration=10, priority="high", frequency="daily"))
dog.add_task(Task(title="Brush fur", duration=15, priority="low", frequency="weekly"))

# Add tasks to Luna (cat)
cat.add_task(Task(title="Clean litter box", duration=10, priority="medium", frequency="daily"))
cat.add_task(Task(title="Playtime", duration=20, priority="low", frequency="daily"))

# Register pets with owner
owner.add_pet(dog)
owner.add_pet(cat)

# Create scheduler with 60 minutes available
scheduler = Scheduler(owner=owner, available_minutes=60)

# Print schedule
print(scheduler.explain_schedule())
