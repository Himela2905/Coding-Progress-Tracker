import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.progress_manager import ProgressManager

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# ----------------------------
# Session check
# ----------------------------
if "user_manager" not in st.session_state or st.session_state["user_manager"] is None:
    st.error("Please log in to access Analytics.")
    st.stop()

manager = st.session_state["user_manager"]

# ----------------------------
# Load progress safely
# ----------------------------
progress_data = manager.load_progress()  # no arguments needed
if not isinstance(progress_data, dict):
    progress_data = {}

st.title("Analytics Dashboard")

if not progress_data:
    st.info("No progress data found! Add topics in the Progress Tracker.")
    st.stop()

# ----------------------------
# Prepare DataFrame
# ----------------------------
#df = pd.DataFrame.from_dict(progress_data, orient='index').reset_index().rename(columns={'index': 'Topic'})
# Keep only valid dict entries
valid_progress = {k: v if isinstance(v, dict) else {"completion": 0, "difficulty": "Unknown", "notes": ""} 
                  for k, v in progress_data.items()}

df = pd.DataFrame.from_dict(valid_progress, orient='index').reset_index().rename(columns={'index': 'Topic'})

# Ensure completion is numeric
if 'completion' not in df.columns:
    df['completion'] = 0
df['completion'] = pd.to_numeric(df['completion'], errors='coerce').fillna(0)
df = df[df['completion'].between(0, 100)]

# Metrics
total_topics = len(df)
completed_topics = len(df[df['completion'] == 100])
avg_completion = df['completion'].mean() if not df.empty else 0
weakest_topic = df.loc[df['completion'].idxmin()]['Topic'] if not df.empty else "N/A"
strongest_topic = df.loc[df['completion'].idxmax()]['Topic'] if not df.empty else "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Topics", total_topics)
col2.metric("Completed", completed_topics)
col3.metric("Avg Completion", f"{avg_completion:.1f}%")
col4.metric("Strongest Topic", strongest_topic)

# ----------------------------
# Bar chart
# ----------------------------
df['color'] = df['completion'].apply(lambda x: "#EF553B" if x <= 40 else "#FFA500" if x <= 70 else "#00CC96")
fig_bar = go.Figure(go.Bar(
    x=df['Topic'],
    y=df['completion'],
    marker_color=df['color'],
    text=df['completion'].apply(lambda x: f"{x:.0f}%"),
    textposition='outside'
))
fig_bar.update_layout(
    yaxis=dict(range=[0, 105]),
    height=450,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------
# Pie chart
# ----------------------------
completed_count = completed_topics
incomplete_count = total_topics - completed_count
fig_pie = go.Figure(go.Pie(
    labels=["Completed", "In Progress"],
    values=[completed_count, incomplete_count],
    hole=0.4,
    marker_colors=["#00CC96", "#636EFA"]
))
fig_pie.update_traces(textinfo='percent+label')
st.plotly_chart(fig_pie, use_container_width=True)

# ----------------------------
# Reset buttons
# ----------------------------
reset_col1, reset_col2 = st.columns(2)

# Reset single topic
with reset_col1:
    topic_to_reset = st.selectbox(
        "Select a topic to reset",
        [""] + list(progress_data.keys()),
        key="analytics_reset_select"
    )
    if st.button("Reset Selected Topic", disabled=(topic_to_reset == ""), key="analytics_reset_topic_btn"):
        if topic_to_reset in progress_data:
            progress_data.pop(topic_to_reset)
            manager.save_progress(progress_data)
            st.success(f"Progress for {topic_to_reset} reset!")
            st.rerun()

# Reset all topics
with reset_col2:
    if st.button("Reset ALL Analytics Data", key="analytics_reset_all_btn"):
        st.session_state.confirm_reset_all_analytics = True

    if st.session_state.get("confirm_reset_all_analytics", False):
        if st.button("Yes, reset everything", key="analytics_confirm_reset_all_btn"):
            manager.save_progress({})
            st.success("All analytics data reset!")
            st.session_state.confirm_reset_all_analytics = False
            st.rerun()
        if st.button("No, keep data", key="analytics_cancel_reset_all_btn"):
            st.session_state.confirm_reset_all_analytics = False
            st.rerun()
