import streamlit as st
import pandas as pd
import plotly.express as px
from utils.progress_manager import ProgressManager

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(page_title="Progress Tracker",  layout="wide")

# ----------------------------
# Ensure user is logged in
# ----------------------------
if "user_manager" not in st.session_state or st.session_state["user_manager"] is None:
    st.error("⚠️ Please log in to access the Progress Tracker.")
    st.stop()

manager = st.session_state["user_manager"]

# ----------------------------
# Load progress safely
# ----------------------------
progress_data = manager.load_progress()  # no arguments
if not isinstance(progress_data, dict):
    progress_data = {}

# ----------------------------
# Session state for success messages
# ----------------------------
if "show_success" not in st.session_state:
    st.session_state.show_success = False
if "success_message" not in st.session_state:
    st.session_state.success_message = ""

# ----------------------------
# Title and input section
# ----------------------------
st.title("Coding Prep Progress Tracker")
st.markdown("Track your DSA learning journey!")

st.subheader("Add / Update Topic Progress")
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input("Topic Name", placeholder="e.g., Binary Search", key="topic_input")
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="difficulty_input")
    completion = st.slider("Completion (%)", 0, 100, 0, key="completion_input")
    notes = st.text_area("Notes (Optional)", placeholder="Add tips or reminders...", key="notes_input")

with col2:
    st.image(
        "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/chart-increasing_1f4c8.png",
        width=150
    )
    st.markdown("### Tips")
    st.markdown(
        "- Be specific with topic names\n"
        "- Update regularly\n"
        "- Use notes to log key insights"
    )

# ----------------------------
# Add/Update Progress button
# ----------------------------
if st.button("Add / Update Progress", key="add_update_btn"):
    if not topic.strip():
        st.error("Topic name cannot be empty!")
    else:
        normalized_topic = topic.strip()
        entry = {"difficulty": difficulty, "completion": completion, "notes": notes.strip()}
        progress_data[normalized_topic] = entry
        manager.save_progress(progress_data)  # only one argument
        st.session_state.show_success = True
        st.session_state.success_message = f"Progress for **{normalized_topic}** saved!"
        st.rerun()

# ----------------------------
# Display success message
# ----------------------------
if st.session_state.show_success:
    st.success(st.session_state.success_message)
    st.session_state.show_success = False

# ----------------------------
# Display Progress Overview
# ----------------------------
st.divider()
st.subheader("Your Progress Overview")

if progress_data:
    #df = pd.DataFrame.from_dict(progress_data, orient='index').reset_index().rename(columns={'index': 'Topic'})
    # Keep only valid dict entries
    valid_progress = {k: v if isinstance(v, dict) else {"completion": 0, "difficulty": "Unknown", "notes": ""} 
                  for k, v in progress_data.items()}

    df = pd.DataFrame.from_dict(valid_progress, orient='index').reset_index().rename(columns={'index': 'Topic'})

    # Ensure completion column exists
    if 'completion' not in df.columns:
        df['completion'] = 0
    df['completion'] = pd.to_numeric(df['completion'], errors='coerce').fillna(0)
    df = df[df['completion'].between(0, 100)]
    
    df = df.sort_values(by='completion', ascending=True).reset_index(drop=True)

    avg_progress = df['completion'].mean() if not df.empty else 0
    weakest_topic = df.iloc[0]['Topic'] if not df.empty else "N/A"

    col_metric1, col_metric2, col_metric3 = st.columns(3)
    col_metric1.metric("Total Topics", len(df))
    col_metric2.metric("Avg Completion", f"{avg_progress:.1f}%")
    col_metric3.metric("Weakest Topic", weakest_topic)

    # ----------------------------
    # Bar chart
    # ----------------------------
    st.markdown("### Completion by Topic")
    fig = px.bar(df, x='Topic', y='completion', color='difficulty',
                 color_discrete_map={"Easy": "#2E8B57", "Medium": "#FFA500", "Hard": "#DC143C"},
                 text='completion', height=400)
    fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # Detailed Table
    # ----------------------------
    st.markdown("### Detailed Progress")
    df_display = df[['Topic', 'difficulty', 'completion', 'notes']].copy()
    df_display['completion'] = df_display['completion'].apply(lambda x: f"{x:.0f}%")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ----------------------------
    # Reset Progress
    # ----------------------------
    st.divider()
    st.subheader("Reset Progress")
    reset_col1, reset_col2 = st.columns(2)

    with reset_col1:
        topic_to_reset = st.selectbox("Select a topic to reset", [""] + list(progress_data.keys()), key="reset_topic_select")
        if st.button("Reset Selected Topic", disabled=(topic_to_reset == ""), key="reset_topic_btn"):
            if topic_to_reset in progress_data:
                progress_data.pop(topic_to_reset)
                manager.save_progress(progress_data)
                st.success(f"Progress for **{topic_to_reset}** has been reset!")
                st.rerun()

    with reset_col2:
        if st.button("Reset ALL Progress", key="reset_all_btn"):
            st.session_state.confirm_reset_all = True

        if st.session_state.get("confirm_reset_all", False):
            if st.button("Yes, reset everything", key="confirm_reset_all_btn"):
                manager.save_progress({})
                st.success("All progress has been reset!")
                st.session_state.confirm_reset_all = False
                st.rerun()
            if st.button("No, keep my progress", key="cancel_reset_all_btn"):
                st.session_state.confirm_reset_all = False
                st.rerun()
else:
    st.info("No progress data yet! Add your first topic above.")
