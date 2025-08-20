import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from utils.helpers import calculate_course_stats
from database.mongodb_client import save_courses

def display_sidebar():
    """Display the sidebar with controls and course management"""
    
    current_date = datetime.now().strftime("%A, %d %b %Y")
    
    with st.sidebar:
        # Header Section
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
            padding: 20px;
            margin: -24px -24px 24px -24px;
            border-radius: 0 0 12px 12px;
            text-align: center;
        '>
            <h1 style='
                color: white;
                font-size: 24px;
                font-weight: 700;
                margin: 0;
                line-height: 1.2;
            '>📚 DataCamp Tracker</h1>
            <p style='
                color: rgba(255,255,255,0.8);
                font-size: 14px;
                margin: 8px 0 0 0;
            '>{current_date}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Stats Panel
        all_courses = st.session_state["courses"]
        stats = calculate_course_stats(all_courses)
        
        st.markdown("""
        <div style='
            background: var(--background);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin-bottom: 20px;
        '>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Courses", value=str(stats["total_courses"]), delta="Active")
        with col2:
            st.metric("Completed", value=f"{stats['completed_modules']}/{stats['total_modules']}")
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Progress", value=f"{stats['progress_percentage']:.0f}%")
        with col4:
            streak_days = 12  # Mock data
            st.metric("Streak", value=f"{streak_days}d", delta="2")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Progress Gauge
        progress_value = stats["progress_percentage"]
        progress_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Progress", 'font': {'size': 14, 'color': '#1F2937'}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#E5E7EB'},
                'bar': {'color': '#2563EB', 'thickness': 0.15},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E5E7EB",
                'steps': [
                    {'range': [0, 50], 'color': '#FEF3C7'},
                    {'range': [50, 80], 'color': '#DBEAFE'},
                    {'range': [80, 100], 'color': '#D1FAE5'}
                ],
                'threshold': {
                    'line': {'color': "#10B981", 'width': 3},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        progress_fig.update_layout(
            height=180,
            margin={'t': 40, 'b': 20, 'l': 20, 'r': 20},
            font={'color': '#1F2937', 'family': 'Arial, sans-serif'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(progress_fig, use_container_width=True)
        
        # Filters Section
        st.markdown("### 🎛️ View Options")
        
        status_filter = st.selectbox(
            "Filter by status:",
            ["All Courses", "In Progress", "Completed", "Not Started"],
            key="status_filter"
        )
        
        sort_option = st.selectbox(
            "Sort by:",
            ["Progress %", "Course Name", "Last Updated", "Total Modules"],
            key="sort_option"
        )
        
        # Export Options
        st.markdown("---")
        st.markdown("### 📊 Quick Export")
        
        export_col1, export_col2 = st.columns(2)
        with export_col1:
            if st.button("📁 CSV", use_container_width=True):
                # Generate CSV export
                export_data = []
                for course_name, course_data in all_courses.items():
                    subcourses = course_data.get("subcourses", {})
                    total_modules = len(subcourses)
                    completed_modules = sum(1 for sub_data in subcourses.values() if sub_data.get("completed", False))
                    progress_pct = (completed_modules / total_modules * 100) if total_modules > 0 else 0
                    
                    export_data.append({
                        "Course Name": course_name,
                        "Description": course_data.get("description", ""),
                        "Total Modules": total_modules,
                        "Completed Modules": completed_modules,
                        "Progress %": f"{progress_pct:.1f}%",
                        "Last Updated": course_data.get("_meta", {}).get("updated", "N/A")
                    })
                
                if export_data:
                    df_export = pd.DataFrame(export_data)
                    csv = df_export.to_csv(index=False)
                    
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"datacamp_courses_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("No data to export")
        
        with export_col2:
            if st.button("📋 Report", use_container_width=True):
                # Generate progress report
                report_lines = [
                    f"📚 DataCamp Progress Report - {current_date}",
                    "=" * 40,
                    "",
                    f"📊 Overall Statistics:",
                    f"• Total Courses: {stats['total_courses']}",
                    f"• Total Modules: {stats['total_modules']}",
                    f"• Completed Modules: {stats['completed_modules']}",
                    f"• Overall Progress: {stats['progress_percentage']:.1f}%",
                    "",
                    "📋 Course Details:"
                ]
                
                for course_name, course_data in all_courses.items():
                    subcourses = course_data.get("subcourses", {})
                    total = len(subcourses)
                    completed = sum(1 for sub_data in subcourses.values() if sub_data.get("completed", False))
                    progress_pct = (completed / total * 100) if total > 0 else 0
                    report_lines.append(f"• {course_name}: {completed}/{total} ({progress_pct:.0f}%)")
                
                report_text = "\n".join(report_lines)
                st.text_area("Progress Report:", value=report_text, height=200, help="Copy this report")
        
        # Course Management Section
        st.markdown("---")
        st.markdown("### ➕ Add New Course")
        
        # Add Course Form
        with st.form("add_course_form"):
            new_course_name = st.text_input("Course Name", placeholder="e.g., Data Scientist with Python")
            new_course_desc = st.text_area("Description", height=80, placeholder="Brief description of the course...")
            course_category = st.selectbox(
                "Category",
                ["Data Science", "Analytics", "Machine Learning", "Programming", "Business Intelligence", "Other"]
            )
            
            if st.form_submit_button("🚀 Add Course", use_container_width=True):
                if new_course_name and new_course_name not in all_courses:
                    # Add new course to session state
                    all_courses[new_course_name] = {
                        "subcourses": {},
                        "description": new_course_desc,
                        "category": course_category,
                        "notes": "",
                        "_meta": {
                            "created": datetime.now().isoformat(),
                            "updated": datetime.now().isoformat()
                        }
                    }
                    
                    # Update session state and save to database
                    st.session_state["courses"] = all_courses
                    save_courses(all_courses)
                    
                    st.success(f"✅ Added course: {new_course_name}")
                    st.rerun()
                    
                elif new_course_name in all_courses:
                    st.error("❌ Course already exists!")
                else:
                    st.error("❌ Please enter a course name!")
        
        # Delete Course Section
        st.markdown("---")
        st.markdown("### 🗑️ Manage Courses")
        
        if all_courses:
            course_to_delete = st.selectbox(
                "Select course to delete:",
                [""] + list(all_courses.keys()),
                key="delete_course_select"
            )
            
            if course_to_delete:
                st.warning(f"⚠️ This will permanently delete '{course_to_delete}' and all its modules!")
                
                if st.button("🗑️ Delete Course", use_container_width=True, type="secondary"):
                    del all_courses[course_to_delete]
                    st.session_state["courses"] = all_courses
                    save_courses(all_courses)
                    st.success(f"🗑️ Deleted: {course_to_delete}")
                    st.rerun()
        else:
            st.info("No courses to manage")
        
        # Study Goals Section
        st.markdown("---")
        st.markdown("### 🎯 Daily Goals")
        
        goal_col1, goal_col2 = st.columns(2)
        with goal_col1:
            daily_goal = st.number_input("Modules/Day", min_value=1, max_value=10, value=2, step=1)
        with goal_col2:
            weekly_goal = st.number_input("Hours/Week", min_value=1, max_value=40, value=10, step=1)
        
        # Progress towards goals (mock data)
        st.markdown("**Today's Progress:**")
        st.progress(0.6, text="3/5 modules completed")
        
        st.markdown("**Weekly Progress:**")
        st.progress(0.7, text="7/10 hours completed")
        
        # Quick tips
        st.markdown("---")
        st.markdown("### 💡 Quick Tips")
        
        tips = [
            "🎯 Set daily learning goals and stick to them",
            "📅 Use spaced repetition for better retention", 
            "🏆 Celebrate small wins to stay motivated",
            "📊 Track your progress regularly",
            "🤝 Join study groups for accountability"
        ]
        
        tip_index = datetime.now().day % len(tips)
        st.info(f"**Tip of the day:** {tips[tip_index]}")