import streamlit as st
import pandas as pd
from auth import init_session_state, require_admin, hash_password
from database import get_all_users, create_user, update_user_password, delete_user, get_user_by_id

# Initialize session state
init_session_state()

st.set_page_config(
    page_title="Admin - AI Tracker",
    page_icon="👑",
    layout="wide"
)

# Require admin access
require_admin()

def main():
    st.title("👑 Admin Panel")
    st.markdown("Manage users and their access.")
    st.markdown("---")

    # Get all users
    users = get_all_users()

    # Display users table
    st.markdown("### 👥 All Users")

    if users:
        df = pd.DataFrame(users)
        df['is_admin'] = df['is_admin'].apply(lambda x: "✅ Yes" if x else "❌ No")
        df = df.rename(columns={
            'id': 'ID',
            'username': 'Username',
            'is_admin': 'Admin',
            'created_at': 'Created At'
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No users found.")

    st.markdown("---")

    # Tabs for different admin actions
    tab1, tab2, tab3 = st.tabs(["➕ Create User", "🔑 Change Password", "🗑️ Delete User"])

    with tab1:
        st.markdown("### Create New User")
        with st.form("create_user_form"):
            new_username = st.text_input("Username", placeholder="Enter username")
            new_password = st.text_input("Password", type="password", placeholder="Enter password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            is_admin = st.checkbox("Grant Admin Privileges")

            submit = st.form_submit_button("Create User", type="primary")

            if submit:
                if not new_username or not new_password:
                    st.error("Username and password are required!")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(new_password) < 4:
                    st.error("Password must be at least 4 characters!")
                else:
                    hashed = hash_password(new_password)
                    user_id = create_user(new_username, hashed, is_admin=1 if is_admin else 0)

                    if user_id:
                        st.success(f"✅ User '{new_username}' created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create user. Username '{new_username}' may already exist.")

    with tab2:
        st.markdown("### Change User Password")

        if users:
            # Filter out current user for safety
            other_users = [u for u in users if u['id'] != st.session_state.user_id]

            if other_users:
                user_options = {f"{u['username']} (ID: {u['id']})": u['id'] for u in other_users}

                with st.form("change_password_form"):
                    selected_user_label = st.selectbox("Select User", options=list(user_options.keys()))
                    new_pwd = st.text_input("New Password", type="password", placeholder="Enter new password")
                    confirm_pwd = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")

                    submit = st.form_submit_button("Change Password", type="primary")

                    if submit:
                        if not new_pwd:
                            st.error("Password is required!")
                        elif new_pwd != confirm_pwd:
                            st.error("Passwords do not match!")
                        elif len(new_pwd) < 4:
                            st.error("Password must be at least 4 characters!")
                        else:
                            user_id = user_options[selected_user_label]
                            hashed = hash_password(new_pwd)
                            success = update_user_password(user_id, hashed)

                            if success:
                                st.success("✅ Password changed successfully!")
                            else:
                                st.error("Failed to change password.")
            else:
                st.info("No other users to manage.")
        else:
            st.info("No users found.")

    with tab3:
        st.markdown("### Delete User")
        st.warning("⚠️ This action cannot be undone!")

        if users:
            # Filter out current user and the main admin
            deletable_users = [u for u in users
                              if u['id'] != st.session_state.user_id
                              and not (u['username'] == 'admin' and u['is_admin'])]

            if deletable_users:
                user_options = {f"{u['username']} (ID: {u['id']})": u['id'] for u in deletable_users}

                selected_user_label = st.selectbox("Select User to Delete", options=list(user_options.keys()))
                selected_user_id = user_options[selected_user_label]
                selected_user = get_user_by_id(selected_user_id)

                if selected_user:
                    st.markdown(f"**Username:** {selected_user['username']}")
                    st.markdown(f"**Admin:** {'Yes' if selected_user['is_admin'] else 'No'}")
                    st.markdown(f"**Created:** {selected_user['created_at']}")

                # Confirmation
                if 'delete_user_confirm' not in st.session_state:
                    st.session_state.delete_user_confirm = False

                if not st.session_state.delete_user_confirm:
                    if st.button("🗑️ Delete User", type="secondary"):
                        st.session_state.delete_user_confirm = True
                        st.rerun()
                else:
                    st.error(f"Are you sure you want to delete user '{selected_user_label}'?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Yes, Delete", type="primary"):
                            success = delete_user(selected_user_id)
                            if success:
                                st.session_state.delete_user_confirm = False
                                st.success("User deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete user.")
                    with col2:
                        if st.button("❌ Cancel"):
                            st.session_state.delete_user_confirm = False
                            st.rerun()
            else:
                st.info("No users available for deletion. (Cannot delete yourself or the main admin)")
        else:
            st.info("No users found.")

if __name__ == "__main__":
    main()
