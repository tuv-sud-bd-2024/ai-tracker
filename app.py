import streamlit as st
from auth import init_session_state, login, logout, setup_default_admin

# Page configuration
st.set_page_config(
    page_title="AI Tracker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and default admin
setup_default_admin()

# Initialize session state
init_session_state()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def main():
    if st.session_state.logged_in:
        # Show logged in state
        st.sidebar.success(f"Logged in as: **{st.session_state.user}**")
        if st.session_state.is_admin:
            st.sidebar.info("👑 Admin User")

        if st.sidebar.button("Logout", type="primary"):
            logout()
            st.rerun()

        # Main content for logged in users
        st.markdown('<h1 class="main-header">🤖 AI Tracker</h1>', unsafe_allow_html=True)
        st.markdown("---")

        st.success("Welcome to AI Tracker! Use the sidebar to navigate.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📊 Dashboard")
            st.write("View and search all tracked AI agents and websites.")

        with col2:
            st.markdown("### ➕ Add Entry")
            st.write("Add a new AI agent or website to track.")

        with col3:
            st.markdown("### ✏️ Edit Entry")
            st.write("Modify or delete existing entries.")

        if st.session_state.is_admin:
            st.markdown("---")
            st.markdown("### 👑 Admin Panel")
            st.write("As an admin, you can manage users in the Admin page.")

    else:
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
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")

        st.markdown("---")
        st.info("Default admin credentials: **admin** / **admin**")

if __name__ == "__main__":
    main()
