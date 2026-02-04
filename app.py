import streamlit as st
from auth import init_session_state, login, logout, setup_default_admin

# Page configuration
st.set_page_config(
    page_title="AI Tracker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize database and default admin
setup_default_admin()

# Initialize session state
init_session_state()

# If already logged in, redirect to appropriate page
if st.session_state.logged_in:
    if st.session_state.is_admin:
        st.switch_page("pages/4_Admin.py")
    else:
        st.switch_page("pages/1_Dashboard.py")

# Custom CSS for login page
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Login page
st.markdown('<h1 class="main-header">🤖 AI Tracker</h1>', unsafe_allow_html=True)
st.markdown("### Login")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login", type="primary")

    if submit:
        if username and password:
            if login(username, password):
                st.success("Login successful!")
                if st.session_state.is_admin:
                    st.switch_page("pages/4_Admin.py")
                else:
                    st.switch_page("pages/1_Dashboard.py")
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please enter both username and password")
