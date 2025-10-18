import streamlit as st

st.set_page_config(page_title="About", page_icon="", layout="wide")

st.title(" About This App")
st.markdown("---")

st.subheader(" Coding Prep Progress Tracker")
st.write("""
This interactive **Progress Tracker** is designed to help students and professionals monitor their coding preparation — 
especially for **Data Structures, Algorithms, and Placement Practice**.  
You can add topics, update completion percentages, analyze progress visually, and reset data anytime.
""")

st.markdown("###  Key Features")
st.markdown("""
- **Add / Update Topics:** Track your learning progress by topic.  
- **Visual Analytics:** View bar & pie charts of your progress.  
- **Auto Save:** All progress is saved per user.  
- **Reset Options:** Easily reset specific or all data.  
- **Secure Login:** Each user’s progress is private and session-based.
""")

st.markdown("###  Purpose")
st.info("""
The main goal is to provide a **real-world productivity tool** that combines learning with motivation.
It can be used as part of your **portfolio**, **placement preparation**, or **personal growth dashboard**.
""")

st.markdown("###  Built With")
st.write("""
- **Streamlit** – for the frontend and app framework  
- **Plotly / Plotly Express** – for interactive charts  
- **Pandas** – for data handling  
- **Python** – for logic and backend  
""")

st.markdown("###  Credits & Developer")
st.success("""
Developed by **Himela Biswas**  
B.Tech Information Technology | Passionate about AI, ML, and Data-Driven Development  
""")

st.markdown("---")
st.markdown("💡 *Tip:* Keep updating your tracker daily to visualize your growth over time!")
