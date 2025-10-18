import streamlit as st
import json
import random
import os
from utils.progress_manager import ProgressManager

# ----------------------------
# Verify login
# ----------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please log in to access this page.")
    st.stop()

# ----------------------------
# Initialize
# ----------------------------
user_id = st.session_state.user_id
manager = st.session_state.user_manager

QUESTIONS_FILE = "data/questions.json"

# ----------------------------
# Load or create JSON file
# ----------------------------
if not os.path.exists(QUESTIONS_FILE):
    default_questions = {
        "Arrays": {
            "questions": [
                "What is an array?",
                "Explain dynamic arrays.",
                "How do you reverse an array in place?",
                "What is the time complexity of insertion in arrays?",
                "Difference between array and linked list?"
            ],
            "attempted_counts": {}
        },
        "Strings": {
            "questions": [
                "What is string immutability in Java?",
                "Explain substring method.",
                "How do you reverse a string?",
                "Difference between StringBuilder and StringBuffer?",
                "How do you check if two strings are anagrams?"
            ],
            "attempted_counts": {}
        }
    }
    os.makedirs(os.path.dirname(QUESTIONS_FILE), exist_ok=True)
    with open(QUESTIONS_FILE, "w") as f:
        json.dump(default_questions, f, indent=4)

with open(QUESTIONS_FILE, "r") as f:
    all_questions = json.load(f)

# ----------------------------
# Main Page UI
# ----------------------------
st.title(" Try Yourself")

topics = list(all_questions.keys())
topic = st.selectbox("Select a Topic", topics)

if topic:
    st.subheader(f"Topic: {topic}")
    questions = all_questions[topic]["questions"]
    random.shuffle(questions)

    st.markdown("### Questions:")
    for i, q in enumerate(questions, 1):
        st.markdown(f"**{i}.** {q}")

    num_questions = st.number_input("How many were you able to answer correctly?", 0, len(questions), 0)
    
    if st.button("Submit", key=f"submit_{topic}"):
        # Update attempt count for the user
        if "attempted_counts" not in all_questions[topic]:
            all_questions[topic]["attempted_counts"] = {}

        all_questions[topic]["attempted_counts"][user_id] = num_questions

        # Save back to JSON
        with open(QUESTIONS_FILE, "w") as f:
            json.dump(all_questions, f, indent=4)

        # Save progress to user's file
        accuracy = (num_questions / len(questions)) * 100
        user_data = manager.load_user_data()
        user_data[topic] = {"completed": True, "accuracy": accuracy}
        manager.save_user_data(user_data)

        st.success(f"✅ You answered {num_questions} out of {len(questions)} ({accuracy:.1f}%) correctly!")

