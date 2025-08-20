import streamlit as st
import sys
import os

# Add the current directory to Python path so we can import from components, utils, etc.
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from components.dashboard import display_overall_dashboard
from components.course_view import display_course_dashboard
from components.sidebar import display_sidebar
from database.mongodb_client import load_courses

# --- App Configuration ---
st.set_page_config(
    page_title="DataCamp Course Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global CSS ---
st.markdown("""
<style>
    :root {
        --primary-blue: #2563EB;
        --primary-blue-light: #3B82F6;
        --primary-blue-dark: #1D4ED8;
        --primary-blue-ultra-light: #EFF6FF;
        --success-green: #10B981;
        --success-green-light: #34D399;
        --text-primary: #1F2937;
        --text-secondary: #6B7280;
        --border-color: #E5E7EB;
        --background: #F9FAFB;
        --card-background: #FFFFFF;
        --status-progress: #F59E0B;
        --status-not-started: #9CA3AF;
    }
    
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    .main .block-container {
        padding: 1rem 2rem 2rem 2rem;
        max-width: none;
        background: var(--background);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: var(--background);
        padding: 4px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 6px;
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--card-background) !important;
        color: var(--primary-blue) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: var(--card-background);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .custom-card {
        background: var(--card-background);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem 1rem 1rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "courses" not in st.session_state:
    st.session_state["courses"] = load_courses()

def main():
    """Main application function"""
    # Display sidebar
    display_sidebar()
    
    # Get courses for tabs
    all_courses = st.session_state["courses"]
    course_names = list(all_courses.keys())
    
    # Create tab names - limit to prevent overflow
    tab_names = ["🏠 Overall Dashboard"]
    
    # Add individual course tabs (limit to 6 to prevent tab overflow)
    for i, name in enumerate(course_names[:6]):
        short_name = name[:15] + "..." if len(name) > 15 else name
        tab_names.append(f"📚 {short_name}")
    
    # If there are more than 6 courses, add an "All Courses" tab
    if len(course_names) > 6:
        tab_names.append("📋 All Courses")
    
    # Create tabs
    tabs = st.tabs(tab_names)
    
    # Overall Dashboard Tab
    with tabs[0]:
        display_overall_dashboard(all_courses)
    
    # Individual Course Dashboard Tabs
    for i, course_name in enumerate(course_names[:6], 1):
        if i < len(tabs):
            with tabs[i]:
                display_course_dashboard(course_name, all_courses[course_name])
    
    # Handle "All Courses" tab if there are more than 6 courses
    if len(course_names) > 6 and len(tabs) > 7:
        with tabs[-1]:
            st.markdown("## 📋 All Courses Overview")
            st.info("Select a course from the dropdown to view detailed dashboard")
            
            # Course selector for overflow courses
            remaining_courses = course_names[6:]
            selected_course = st.selectbox(
                "Select a course:",
                remaining_courses,
                key="overflow_course_selector"
            )
            
            if selected_course:
                st.markdown("---")
                display_course_dashboard(selected_course, all_courses[selected_course])

if __name__ == "__main__":
    main()