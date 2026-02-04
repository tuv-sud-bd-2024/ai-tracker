import streamlit as st
from datetime import datetime
from auth import init_session_state, require_auth
from database import create_entry

# Initialize session state
init_session_state()

st.set_page_config(
    page_title="Add Entry - AI Tracker",
    page_icon="➕",
    layout="wide"
)

# Require authentication
require_auth()

# Custom CSS
st.markdown("""
<style>
    .form-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .required-field::after {
        content: " *";
        color: red;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("➕ Add New Entry")
    st.markdown("Add a new AI agent or website to track.")
    st.markdown("---")

    # Display current date/time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.info(f"📅 Entry will be created with date: **{current_date}**")

    with st.form("add_entry_form"):
        # Website Address (required)
        website_address = st.text_input(
            "Website Address *",
            placeholder="e.g., https://example.com or example.com",
            help="Enter the website URL (required)"
        )

        # Video Link (optional)
        video_link = st.text_input(
            "Video Link",
            placeholder="e.g., https://youtube.com/watch?v=...",
            help="Enter a YouTube or video URL (optional)"
        )

        # Description (optional)
        description = st.text_area(
            "Description",
            placeholder="Describe what this AI agent or website does...",
            help="Enter a description of the website/AI agent (optional)",
            height=150
        )

        # Remarks (optional)
        remarks = st.text_area(
            "Remarks",
            placeholder="Any additional notes or remarks...",
            help="Enter any additional remarks (optional)",
            height=100
        )

        st.markdown("---")
        st.markdown("*Fields marked with * are required*")

        col1, col2 = st.columns([1, 4])
        with col1:
            submit = st.form_submit_button("💾 Save Entry", type="primary")

        if submit:
            if not website_address:
                st.error("Website Address is required!")
            else:
                # Create the entry
                entry_id = create_entry(
                    website_address=website_address.strip(),
                    video_link=video_link.strip() if video_link else None,
                    description=description.strip() if description else None,
                    remarks=remarks.strip() if remarks else None,
                    created_by=st.session_state.user_id
                )

                if entry_id:
                    st.success("✅ Entry created successfully!")
                    st.balloons()

                    # Show what was saved
                    st.markdown("### Entry Summary")
                    st.write(f"**Website:** {website_address}")
                    if video_link:
                        st.write(f"**Video:** {video_link}")
                    if description:
                        st.write(f"**Description:** {description}")
                    if remarks:
                        st.write(f"**Remarks:** {remarks}")

                    st.info("Go to Dashboard to view all entries.")
                else:
                    st.error("Failed to create entry. Please try again.")

if __name__ == "__main__":
    main()
