import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
from auth import init_session_state, require_auth, render_page_header
from database import get_all_entries

# Initialize session state
init_session_state()

st.set_page_config(
    page_title="Dashboard - AI Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Require authentication
require_auth()

# Page header with logout
render_page_header()

# Custom CSS
st.markdown("""
<style>
    .website-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .website-header a {
        color: #1E88E5;
        text-decoration: none;
    }
    .website-header a:hover {
        color: #1565C0;
        text-decoration: underline;
    }
    .entry-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats."""
    if not url:
        return None
    patterns = [
        r'(?:youtube\.com|youtu\.be|youtube-nocookie\.com)\/(?:watch\?v=|embed\/|v\/|shorts\/)?([a-zA-Z0-9_-]{11})',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def render_video(video_link):
    """Render video embed or link."""
    if not video_link:
        st.write("No video")
        return

    youtube_id = extract_youtube_id(video_link)
    if youtube_id:
        embed_url = f"https://www.youtube.com/embed/{youtube_id}"
        video_html = f'''<iframe src="{embed_url}" width="100%" height="100%"
            style="border:0;"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media;
            gyroscope; picture-in-picture" allowfullscreen></iframe>'''
        components.html(video_html, height=220)
    else:
        # For non-YouTube direct video files
        if video_link.lower().endswith(('.mp4', '.webm', '.ogg')):
            st.video(video_link)
        else:
            st.markdown(f"[Watch Video]({video_link})")

def main():
    st.title("📊 Dashboard")
    st.markdown("View and search all tracked AI agents and websites.")
    st.markdown("---")

    # Get all entries
    entries = get_all_entries()

    if not entries:
        st.info("No entries yet. Go to 'Add Entry' to create your first entry!")
        return

    # Convert to DataFrame for filtering
    df = pd.DataFrame(entries)

    # Filter section
    st.markdown("### 🔍 Search & Filter")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        filter_website = st.text_input("Filter by Website", key="filter_website",
                                        placeholder="Type to filter...")
    with col2:
        filter_description = st.text_input("Filter by Description", key="filter_desc",
                                            placeholder="Type to filter...")
    with col3:
        filter_remarks = st.text_input("Filter by Remarks", key="filter_remarks",
                                        placeholder="Type to filter...")
    with col4:
        filter_date = st.text_input("Filter by Date", key="filter_date",
                                     placeholder="e.g., 2026-01-")

    # Sort options
    col_sort1, col_sort2 = st.columns(2)
    with col_sort1:
        sort_by = st.selectbox("Sort by", ["Date", "Website", "Description", "Remarks"],
                               key="sort_by")
    with col_sort2:
        sort_order = st.selectbox("Order", ["Descending", "Ascending"], key="sort_order")

    # Apply filters
    filtered_df = df.copy()

    if filter_website:
        filtered_df = filtered_df[
            filtered_df['website_address'].str.lower().str.contains(filter_website.lower(), na=False)
        ]

    if filter_description:
        filtered_df = filtered_df[
            filtered_df['description'].str.lower().str.contains(filter_description.lower(), na=False)
        ]

    if filter_remarks:
        filtered_df = filtered_df[
            filtered_df['remarks'].str.lower().str.contains(filter_remarks.lower(), na=False)
        ]

    if filter_date:
        filtered_df = filtered_df[
            filtered_df['created_at'].str.contains(filter_date, na=False)
        ]

    # Apply sorting
    sort_column_map = {
        "Date": "created_at",
        "Website": "website_address",
        "Description": "description",
        "Remarks": "remarks"
    }
    sort_col = sort_column_map[sort_by]
    ascending = sort_order == "Ascending"
    filtered_df = filtered_df.sort_values(by=sort_col, ascending=ascending, na_position='last')

    st.markdown("---")
    st.markdown(f"### Showing {len(filtered_df)} of {len(df)} entries")

    # Display entries
    for _, row in filtered_df.iterrows():
        with st.container():
            # Website header
            website_url = row['website_address']
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url

            st.markdown(f'''
                <div class="entry-card">
                    <p class="website-header">
                        <a href="{website_url}" target="_blank">{row['website_address']}</a>
                    </p>
                </div>
            ''', unsafe_allow_html=True)

            # Content columns
            col_video, col_desc, col_remarks, col_date, col_action = st.columns([2, 2, 2, 1, 1])

            with col_video:
                st.markdown("**Video**")
                render_video(row['video_link'])

            with col_desc:
                st.markdown("**Description**")
                st.write(row['description'] if row['description'] else "No description")

            with col_remarks:
                st.markdown("**Remarks**")
                st.write(row['remarks'] if row['remarks'] else "No remarks")

            with col_date:
                st.markdown("**Date**")
                date_str = row['created_at'][:10] if row['created_at'] else "N/A"
                st.write(date_str)

            with col_action:
                st.markdown("**Action**")
                if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                    st.session_state.edit_entry_id = row['id']
                    st.switch_page("pages/3_Edit_Entry.py")

            st.markdown("---")

if __name__ == "__main__":
    main()
