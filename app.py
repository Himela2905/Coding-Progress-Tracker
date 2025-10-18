import streamlit as st
import random
from datetime import datetime
from utils.progress_manager import ProgressManager
from utils.leetcode_api import fetch_leetcode_stats
from utils.firebase_config import auth, db  # make sure firebase_config.py exists

#===============================
#  SESSION INITIALIZATION
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_manager" not in st.session_state:
    st.session_state.user_manager = None


# ===============================
# ✅ LOGIN FUNCTION
# ===============================
def login_user(email):
    """Handles user login and session setup."""
    st.session_state.logged_in = True
    st.session_state.user_id = email
    st.session_state.user_manager = ProgressManager(email)
    st.success(f"Welcome back, {email} ")
    st.rerun()


# ===============================
# ✅ LOGOUT FUNCTION
# ===============================
def logout_user():
    """Clears session and logs out the user."""
    for key in ["logged_in", "user_id", "user_manager"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_manager = None
    st.rerun()
# ----------------------------
# App Config
# ----------------------------
APP_TITLE = "Coding Prep Progress Tracker Dashboard"
MOTIVATIONAL_QUOTES = [
    "The only way to learn a new programming language is by writing programs in it. – Dennis Ritchie",
    "Talk is cheap. Show me the code. – Linus Torvalds",
    "First, solve the problem. Then, write the code. – John Johnson",
    "Code is like humor. When you have to explain it, it’s bad. – Cory House",
    "The best error message is the one that never shows up. – Thomas Fuchs",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand. – Martin Fowler"
]

# ----------------------------
# Session State
# ----------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_manager' not in st.session_state:
    st.session_state.user_manager = None

# ----------------------------
# Firebase Auth Functions
# ----------------------------
def signup_user(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        ProgressManager(email).save_user_data()  # initialize empty progress
        return True, user
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return True, user
    except Exception as e:
        return False, str(e)

# ----------------------------
# Login / Signup Page
# ----------------------------
def login_page():
    st.markdown(f"<h1 style='text-align: center; color: #4F8BF9;'>{APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Track your DSA learning journey </h3>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs([" Login", " Sign Up"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            submit = st.form_submit_button("Login")
            if submit:
                success, res = login_user(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.current_user = email
                    st.session_state.user_manager = ProgressManager(email)
                    st.success(f"Welcome back, **{email}**! ")
                    st.rerun()
                else:
                    st.error(f"Login failed: {res}")

    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_user")
            password = st.text_input("Password", type="password", key="signup_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass")
            signup = st.form_submit_button("Sign Up")
            if signup:
                if not email or not password:
                    st.error("Please fill in all fields.")
                elif password != confirm_pass:
                    st.error("Passwords do not match!")
                else:
                    success, res = signup_user(email, password)
                    if success:
                        st.success("Account created successfully! Please login.")
                        st.balloons()
                    else:
                        if "EMAIL_EXISTS" in res:
                            st.warning("This email is already registered. Please log in instead.")
                        else:
                            st.error(f"Sign up failed: {res}")

# ----------------------------
# Dashboard Pages
# ----------------------------
def render_home_page():
    st.title(" Welcome to Your Coding Journey!")
    st.markdown(f"### Hi, **{st.session_state.current_user}**! Let's crush those DSA problems together. ")

    # Motivational quote
    quote = random.choice(MOTIVATIONAL_QUOTES)
    st.info(f"**Motivation for today:**\n\n> {quote}")

    # Progress metrics
    #user_progress = st.session_state.user_manager.get_progress()
    user_progress = st.session_state.user_manager.load_user_data()
    if not isinstance(user_progress, dict):
        user_progress = {}

    total_topics = len(user_progress)
    completed_topics = sum(1 for t in user_progress.values() if t.get("completed"))
    accuracy_rate = 0
    if user_progress:
        accuracies = [t.get("accuracy", 0) for t in user_progress.values() if t.get("accuracy") is not None]
        if accuracies:
            accuracy_rate = sum(accuracies) / len(accuracies)

    col1, col2, col3 = st.columns(3)
    col1.metric(" Total Topics", total_topics)
    col2.metric(" Completed", completed_topics)
    col3.metric(" Avg Accuracy", f"{accuracy_rate:.1f}%" if accuracy_rate > 0 else "N/A")

    st.markdown("---")
    st.subheader(" Your LeetCode Stats")
    lc_username = st.session_state.user_manager.get_leetcode_username()
    if lc_username:
        try:
            lc_data = fetch_leetcode_stats(lc_username)
            if lc_data:
                col1, col2, col3 ,col4= st.columns(4)
                col1.metric("Total Solved", lc_data.get("totalSolved", "N/A"))
                col2.metric("Easy", lc_data.get("Easy", "N/A"))
                
                col3.metric("Medium", lc_data.get("Medium", "N/A"))
                col4.metric("Hard", lc_data.get("Hard", "N/A"))
        except Exception:
            st.warning("Unable to fetch LeetCode stats right now. Try again later.")
    else:
        st.info("Connect your LeetCode account in the sidebar to see stats!")

def render_progress_tracker():
    st.header(" Progress Tracker")
    user_progress = st.session_state.user_manager.get_progress()
    st.json(user_progress)

def render_analytics():
    st.header(" Analytics")
    st.info("Analytics charts coming soon!")

def render_leetcode_stats():
    st.header(" LeetCode Stats")
    lc_username = st.session_state.user_manager.get_leetcode_username()
    if lc_username:
        lc_data = fetch_leetcode_stats(lc_username)
        st.json(lc_data)
    else:
        st.info("Connect your LeetCode username in the sidebar.")

def render_quiz():
    st.header(" Evaluation Quiz")
    st.info("Quiz functionality coming soon!")

def render_about():
    st.header(" About")
    st.markdown("This app tracks your DSA progress, quizzes, and LeetCode stats.")


# ----------------------------
# Main Dashboard
# ----------------------------
def main_dashboard():
    """Render the main dashboard after login."""
    # Sidebar navigation
    st.sidebar.title(f"Hello, {st.session_state.current_user}! ")
    st.sidebar.markdown("---")

    # Navigation options
    pages = {
        "Home": render_home_page,
        "Progress Tracker": lambda: __import__("pages.1_Progress_Tracker"),
        "Analytics": lambda: __import__("pages.2_Analytics"),
        "LeetCode Stats": lambda: __import__("pages.3_LeetCode_Stats"),
        "Evaluation Quiz": lambda: __import__("pages.4_Evaluation_Quiz"),
        "About": lambda: __import__("pages.5_About")
    }

    selection = st.sidebar.radio("Navigation", list(pages.keys()), index=0)

    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.user_data = {}
        st.session_state.user_manager = None
        st.rerun()

    # Initialize ProgressManager for current user
    if "user_manager" not in st.session_state or st.session_state.user_manager is None:
        st.session_state.user_manager = ProgressManager(st.session_state.current_user)

    # Load user progress safely
    user_manager = st.session_state.user_manager
    user_progress = user_manager.load_user_data()
    if not isinstance(user_progress, dict):
        user_progress = {}

    # Load and display selected page
    page_func = pages[selection]
    try:
        page_func()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.markdown("### Falling back to Home view...")
        render_home_page()


# ----------------------------
# Home Page Content
# ----------------------------
def render_home_page():
    st.title(" Welcome to Your Coding Journey!")
    st.markdown(f"### Hi, **{st.session_state.current_user}**! Let's crush those DSA problems together. ")

    # Display motivational quote
    quote = random.choice(MOTIVATIONAL_QUOTES)
    st.info(f"**Motivation for today:**\n\n> {quote}")

    # Access ProgressManager safely
    user_manager = st.session_state.user_manager
    user_progress = user_manager.load_user_data()
    if not isinstance(user_progress, dict):
        user_progress = {}

    # Calculate metrics
    total_topics = len(user_progress)
    completed_topics = sum(1 for t in user_progress.values() if isinstance(t, dict) and t.get("completed", False))
    accuracy_rate = 0
    accuracies = [t.get("accuracy", 0) for t in user_progress.values() if isinstance(t, dict) and t.get("accuracy") is not None]
    if accuracies:
        accuracy_rate = sum(accuracies) / len(accuracies)

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    col1.metric(" Total Topics", total_topics)
    col2.metric(" Completed", completed_topics)
    col3.metric(" Avg Accuracy", f"{accuracy_rate:.1f}%" if accuracy_rate > 0 else "N/A")

    st.markdown("---")
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(" Add New Topic", use_container_width=True, key="add_new_topic_btn"):
            st.switch_page("pages/1_Progress_Tracker.py")
    with col2:
        if st.button(" Take a Quiz", use_container_width=True, key="take_a_quiz_btn"):
            st.switch_page("pages/4_Evaluation_Quiz.py")

    # LeetCode stats preview
    st.markdown("---")
    st.subheader(" Your LeetCode Stats")
    try:
        lc_username = user_manager.get_leetcode_username()
        if lc_username:
            lc_data = fetch_leetcode_stats(lc_username)
            if lc_data:
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Solved", lc_data.get("total_solved", "N/A"))
                col2.metric("Easy", lc_data.get("easy_solved", "N/A"))
                col3.metric("Medium", lc_data.get("medium_solved", "N/A"))
            else:
                st.info("No LeetCode data found for your username.")
        else:
            st.info("Connect your LeetCode account in the **LeetCode Stats** section to see your progress!")
    except Exception as e:
        st.warning(f"Unable to fetch LeetCode stats right now. {str(e)}")

# ----------------------------
# Main App
# ----------------------------
def main():
    st.set_page_config(
        page_title=APP_TITLE,
        #page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if not st.session_state.logged_in:
        login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
