import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ── Session state bootstrap ──────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "available_minutes" not in st.session_state:
    st.session_state.available_minutes = 60

# ── Helpers ──────────────────────────────────────────────────────────────────
PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}
FREQUENCY_ICON = {"daily": "📅", "weekly": "🗓️", "as-needed": "📌"}

def tasks_to_rows(tasks):
    return [
        {
            "Task": t.title,
            "Duration (min)": t.duration,
            "Priority": f"{PRIORITY_ICON[t.priority]} {t.priority}",
            "Repeats": f"{FREQUENCY_ICON[t.frequency]} {t.frequency}",
            "Due": str(t.due_date),
        }
        for t in tasks
    ]


# ── Title ────────────────────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption("Plan your pet's day — smartly sorted, nothing forgotten.")

# ── Section 1: Owner & Pet setup ─────────────────────────────────────────────
st.subheader("Step 1: Set Up Your Profile")

owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
available_minutes = st.number_input(
    "Minutes available today", min_value=10, max_value=480, value=st.session_state.available_minutes
)

if st.button("Save profile"):
    pet = Pet(name=pet_name, species=species)
    owner = Owner(name=owner_name)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.available_minutes = int(available_minutes)
    st.success(f"Profile saved! {owner.get_info()} — {int(available_minutes)} min available today.")

if st.session_state.owner:
    st.caption(
        f"Active: {st.session_state.owner.get_info()} · "
        f"{st.session_state.available_minutes} min available"
    )

st.divider()

# ── Section 2: Add tasks ──────────────────────────────────────────────────────
st.subheader("Step 2: Add Tasks")

if st.session_state.pet is None:
    st.info("Save your profile above before adding tasks.")
else:
    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Repeats", ["daily", "weekly", "as-needed"])

    if st.button("Add task"):
        if not task_title.strip():
            st.error("Task title cannot be empty.")
        else:
            task = Task(
                title=task_title.strip(),
                duration=int(duration),
                priority=priority,
                frequency=frequency,
            )
            st.session_state.pet.add_task(task)
            st.success(f"Added **{task.title}** ({duration} min, {priority} priority, {frequency})")

    # ── Current task list sorted by duration ─────────────────────────────────
    pending = st.session_state.pet.get_pending_tasks()
    if pending:
        scheduler_preview = Scheduler(
            owner=st.session_state.owner,
            available_minutes=st.session_state.available_minutes,
        )
        sorted_pending = scheduler_preview.sort_by_time(pending)

        st.markdown("**Current tasks** *(sorted shortest → longest)*")
        st.table(tasks_to_rows(sorted_pending))

        total_pending_mins = sum(t.duration for t in pending)
        budget = st.session_state.available_minutes
        fill_ratio = min(total_pending_mins / budget, 1.0)

        st.caption(f"Total task time: **{total_pending_mins} min** · Budget: **{budget} min**")
        st.progress(fill_ratio)

        if total_pending_mins > budget:
            st.warning(
                f"Your tasks add up to **{total_pending_mins} min**, but you only have "
                f"**{budget} min** available. Some tasks will be dropped — generate the "
                "schedule below to see which ones."
            )
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ── Section 3: Generate schedule ─────────────────────────────────────────────
st.subheader("Step 3: Generate Today's Schedule")

if st.button("Generate schedule", type="primary"):
    if st.session_state.owner is None:
        st.warning("Please save your profile first.")
    elif not st.session_state.pet.get_pending_tasks():
        st.warning("No pending tasks to schedule. Add some tasks first.")
    else:
        scheduler = Scheduler(
            owner=st.session_state.owner,
            available_minutes=st.session_state.available_minutes,
        )
        scheduled = scheduler.generate_schedule()
        dropped = scheduler.get_dropped_tasks()
        budget = st.session_state.available_minutes
        time_used = sum(t.duration for t in scheduled)
        time_left = budget - time_used

        # ── Summary metrics ───────────────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        m1.metric("Tasks scheduled", len(scheduled))
        m2.metric("Time used", f"{time_used} min")
        m3.metric("Time remaining", f"{time_left} min")

        st.progress(time_used / budget if budget > 0 else 0)

        # ── Scheduled tasks ───────────────────────────────────────────────────
        if scheduled:
            st.success(f"Schedule ready! {len(scheduled)} task(s) fit within your {budget}-minute budget.")
            st.table(tasks_to_rows(scheduled))
        else:
            st.error("No tasks could be scheduled. Your available time may be too short for any task.")

        # ── Dropped task warnings ─────────────────────────────────────────────
        if dropped:
            st.warning(
                f"**{len(dropped)} task(s) were dropped** — they couldn't fit in your remaining time. "
                "Consider completing a shorter task first to free up time, or increase your available minutes."
            )
            with st.expander(f"See dropped tasks ({len(dropped)})"):
                for t in dropped:
                    st.markdown(
                        f"- {PRIORITY_ICON[t.priority]} **{t.title}** — "
                        f"{t.duration} min · {t.priority} priority · {t.frequency}"
                    )
        else:
            if scheduled:
                st.success("All pending tasks fit in your schedule today!")

st.divider()

# ── Section 4: Complete a task ────────────────────────────────────────────────
st.subheader("Step 4: Mark a Task Complete")

if st.session_state.pet is None or not st.session_state.pet.get_pending_tasks():
    st.info("No pending tasks to complete.")
else:
    pending_titles = [t.title for t in st.session_state.pet.get_pending_tasks()]
    selected_title = st.selectbox("Select a task to mark complete", pending_titles)

    if st.button("Mark complete"):
        pet = st.session_state.pet
        task_to_complete = next(
            (t for t in pet.get_pending_tasks() if t.title == selected_title), None
        )
        if task_to_complete:
            next_task = pet.complete_task(task_to_complete)
            if next_task:
                st.success(
                    f"Done! **{task_to_complete.title}** marked complete. "
                    f"Next occurrence queued for **{next_task.due_date}** ({next_task.frequency})."
                )
            else:
                st.success(
                    f"Done! **{task_to_complete.title}** marked complete. "
                    "This is a one-off task — no recurrence scheduled."
                )
