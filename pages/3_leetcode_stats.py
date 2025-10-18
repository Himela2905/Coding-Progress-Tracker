import streamlit as st
import requests
import json
from utils.progress_manager import ProgressManager

st.set_page_config(page_title="LeetCode Stats", layout="wide")

if "user_id" not in st.session_state:
    st.error("⚠️ Please log in to see your LeetCode stats.")
    st.stop()

user_id = st.session_state["user_id"]
manager = st.session_state.get("user_manager")

lc_username = manager.get_leetcode_username() or ""

st.title("LeetCode Stats Dashboard")

# Input for LeetCode username
lc_username_input = st.text_input("Enter your LeetCode username", value=lc_username, key="lc_username_input")

if st.button("Save Username", key="save_lc_username"):
    if lc_username_input.strip():
        manager.set_leetcode_username(lc_username_input.strip())
        st.success(f"LeetCode username saved: {lc_username_input.strip()}")
        st.rerun()

# Fetch stats via LeetCode GraphQL
if lc_username_input.strip():
    url = "https://leetcode.com/graphql"
    query = {
        "query": """
        query userProfile($username: String!) {
          matchedUser(username: $username) {
            username
            submitStats: submitStatsGlobal {
              acSubmissionNum {
                difficulty
                count
                submissions
              }
            }
          }
        }
        """,
        "variables": {"username": lc_username_input.strip()}
    }

    try:
        res = requests.post(url, json=query)
        data = res.json()
        stats = data.get("data", {}).get("matchedUser", {}).get("submitStats", {}).get("acSubmissionNum", [])
        if not stats:
            st.warning("No stats found. Make sure your username is correct.")
        else:
            st.subheader(f"LeetCode Stats for {lc_username_input.strip()}")
            for item in stats:
                st.metric(label=f"{item['difficulty']} Problems Solved", value=item['count'])
    except Exception as e:
        st.error(f"Error fetching LeetCode stats: {e}")
