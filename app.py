import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize session state — only runs once per session, not on every rerender
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None

st.title("🐾 PawPal+")

# ── Section 1: Owner & Pet setup ────────────────────────────────────────────
st.subheader("Step 1: Set Up Your Profile")

owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
available_minutes = st.number_input("Minutes available today", min_value=10, max_value=480, value=60)

if st.button("Save profile"):
    pet = Pet(name=pet_name, species=species)
    owner = Owner(name=owner_name)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.success(f"Profile saved! {owner.get_info()}")

if st.session_state.owner:
    st.caption(f"Active profile: {st.session_state.owner.get_info()}")

st.divider()

# ── Section 2: Add tasks ─────────────────────────────────────────────────────
st.subheader("Step 2: Add Tasks")

if st.session_state.pet is None:
    st.info("Save your profile above before adding tasks.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        task = Task(title=task_title, duration=int(duration), priority=priority)
        st.session_state.pet.add_task(task)
        st.success(f"Added: {task}")

    pending = st.session_state.pet.get_pending_tasks()
    if pending:
        st.write("Current tasks:")
        st.table([
            {"title": t.title, "duration (min)": t.duration, "priority": t.priority}
            for t in pending
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ── Section 3: Generate schedule ─────────────────────────────────────────────
st.subheader("Step 3: Generate Today's Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please save your profile first.")
    elif not st.session_state.pet.get_pending_tasks():
        st.warning("No tasks to schedule. Add some tasks first.")
    else:
        scheduler = Scheduler(owner=st.session_state.owner, available_minutes=int(available_minutes))
        st.text(scheduler.explain_schedule())
