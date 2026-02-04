import streamlit as st
from auth import init_session_state, require_auth, render_page_header
from database import get_all_entries, get_entry_by_id, update_entry, delete_entry

# Initialize session state
init_session_state()

st.set_page_config(
    page_title="Edit Entry - AI Tracker",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Require authentication
require_auth()

# Page header with logout
render_page_header()

def main():
    st.title("✏️ Edit Entry")
    st.markdown("Modify or delete existing entries.")
    st.markdown("---")

    # Get all entries for selection
    entries = get_all_entries()

    if not entries:
        st.info("No entries to edit. Go to 'Add Entry' to create your first entry!")
        return

    # Create a mapping for the selectbox
    entry_options = {f"{e['website_address']} (ID: {e['id']})": e['id'] for e in entries}

    # Check if we came from dashboard with a specific entry
    default_index = 0
    if st.session_state.edit_entry_id:
        for i, (label, eid) in enumerate(entry_options.items()):
            if eid == st.session_state.edit_entry_id:
                default_index = i
                break

    # Entry selection
    selected_label = st.selectbox(
        "Select an entry to edit",
        options=list(entry_options.keys()),
        index=default_index
    )

    selected_id = entry_options[selected_label]
    entry = get_entry_by_id(selected_id)

    if not entry:
        st.error("Entry not found!")
        return

    st.markdown("---")
    st.markdown(f"### Editing: {entry['website_address']}")
    st.caption(f"Created: {entry['created_at']} | Last Updated: {entry['updated_at']}")

    # Edit form
    with st.form("edit_entry_form"):
        # Website Address (required)
        website_address = st.text_input(
            "Website Address *",
            value=entry['website_address'],
            help="Enter the website URL (required)"
        )

        # Video Link (optional)
        video_link = st.text_input(
            "Video Link",
            value=entry['video_link'] or "",
            help="Enter a YouTube or video URL (optional)"
        )

        # Description (optional)
        description = st.text_area(
            "Description",
            value=entry['description'] or "",
            help="Enter a description of the website/AI agent (optional)",
            height=150
        )

        # Remarks (optional)
        remarks = st.text_area(
            "Remarks",
            value=entry['remarks'] or "",
            help="Enter any additional remarks (optional)",
            height=100
        )

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            update_btn = st.form_submit_button("💾 Update Entry", type="primary")
        with col2:
            pass  # Leave space for delete button outside form

        if update_btn:
            if not website_address:
                st.error("Website Address is required!")
            else:
                success = update_entry(
                    entry_id=selected_id,
                    website_address=website_address.strip(),
                    video_link=video_link.strip() if video_link else None,
                    description=description.strip() if description else None,
                    remarks=remarks.strip() if remarks else None
                )

                if success:
                    st.success("✅ Entry updated successfully!")
                    # Clear the edit_entry_id
                    st.session_state.edit_entry_id = None
                    st.rerun()
                else:
                    st.error("Failed to update entry. Please try again.")

    # Delete section (outside form)
    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")

    # Use session state to track delete confirmation
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = False

    if not st.session_state.confirm_delete:
        if st.button("🗑️ Delete Entry", type="secondary"):
            st.session_state.confirm_delete = True
            st.rerun()
    else:
        st.warning(f"Are you sure you want to delete **{entry['website_address']}**? This cannot be undone!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", type="primary"):
                success = delete_entry(selected_id)
                if success:
                    st.session_state.confirm_delete = False
                    st.session_state.edit_entry_id = None
                    st.success("Entry deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete entry.")
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_delete = False
                st.rerun()

if __name__ == "__main__":
    main()
