import bcrypt
import streamlit as st
from database import get_user_by_username, create_user, init_db

def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def init_session_state():
    """Initialize session state variables."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'edit_entry_id' not in st.session_state:
        st.session_state.edit_entry_id = None

def login(username, password):
    """Attempt to log in a user."""
    user = get_user_by_username(username)
    if user and verify_password(password, user['password']):
        st.session_state.logged_in = True
        st.session_state.user = user['username']
        st.session_state.user_id = user['id']
        st.session_state.is_admin = bool(user['is_admin'])
        return True
    return False

def logout():
    """Log out the current user."""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.is_admin = False
    st.session_state.edit_entry_id = None

def require_auth():
    """Check if user is authenticated, show warning if not."""
    if not st.session_state.get('logged_in', False):
        st.warning("Please log in to access this page.")
        st.stop()

def require_admin():
    """Check if user is an admin, show warning if not."""
    require_auth()
    if not st.session_state.get('is_admin', False):
        st.error("You do not have permission to access this page.")
        st.stop()

def setup_default_admin():
    """Create default admin user if no users exist."""
    init_db()
    user = get_user_by_username('admin')
    if not user:
        hashed = hash_password('admin')
        create_user('admin', hashed, is_admin=1)
