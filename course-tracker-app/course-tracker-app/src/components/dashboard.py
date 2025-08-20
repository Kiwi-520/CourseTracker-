import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from utils.helpers import calculate_course_stats, calculate_course_progress

def display_overall_dashboard(courses):
    """Display the main overview dashboard"""
    st.markdown("## 🏠 Learning Overview Dashboard")
    
    if not courses:
        st.warning("🎯 No courses added yet. Add your first course from the sidebar!")
        return
    
    # Get overall statistics
    stats = calculate_course_stats(courses)
    
    # === TOP METRICS SECTION ===
    st.markdown("### 📊 Key Learning Metrics")
    
    # Create 4-column metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate additional metrics
    weekly_completed = 5  # Mock data - could be calculated from timestamps
    avg_completion = stats["progress_percentage"]
    streak_days = 15  # Mock data
    
    metric_cards = [
        {"title": "Total Courses", "value": str(stats["total_courses"]), "delta": "Active", "color": "#2563EB"},
        {"title": "Modules Done", "value": str(stats["completed_modules"]), "delta": f"+{weekly_completed} this week", "color": "#10B981"},
        {"title": "Overall Progress", "value": f"{avg_completion:.0f}%", "delta": "↗️ +12% this month", "color": "#F59E0B"},
        {"title": "Learning Streak", "value": f"{streak_days} days", "delta": "🔥 Keep it up!", "color": "#EF4444"}
    ]
    
    cols = [col1, col2, col3, col4]
    
    for col, card in zip(cols, metric_cards):
        with col:
            st.markdown(f"""
            <div class="metric-card" style='
                background: linear-gradient(135deg, {card["color"]}10 0%, {card["color"]}05 100%);
                border: 2px solid {card["color"]}20;
            '>
                <h3 style='
                    color: {card["color"]};
                    font-size: 28px;
                    font-weight: 700;
                    margin: 0 0 4px 0;
                '>{card["value"]}</h3>
                <p style='
                    color: var(--text-primary);
                    font-size: 14px;
                    font-weight: 600;
                    margin: 0 0 4px 0;
                '>{card["title"]}</p>
                <span style='
                    color: var(--text-secondary);
                    font-size: 11px;
                '>{card["delta"]}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === MAIN CHARTS SECTION ===
    chart_col1, chart_col2 = st.columns([3, 2], gap="large")
    
    with chart_col1:
        st.markdown("### 📈 Course Progress Overview")
        
        # Prepare data for horizontal bar chart
        course_progress_data = []
        for course_name, course_data in courses.items():
            progress = calculate_course_progress(course_data)
            course_progress_data.append({
                'course_name': course_name[:30] + "..." if len(course_name) > 30 else course_name,
                'completion_percentage': progress["percentage"],
                'completed_count': progress["completed"],
                'total_count': progress["total"]
            })
        
        if course_progress_data:
            df_progress = pd.DataFrame(course_progress_data)
            
            # Create horizontal bar chart
            fig = px.bar(
                df_progress,
                x='completion_percentage',
                y='course_name',
                orientation='h',
                color='completion_percentage',
                color_continuous_scale=[
                    [0.0, "#FEF3C7"],  # Light yellow for low progress
                    [0.3, "#FBBF24"],  # Orange for medium-low
                    [0.6, "#3B82F6"],  # Blue for medium-high  
                    [1.0, "#10B981"]   # Green for high progress
                ],
                title="Course Completion Status",
                labels={'completion_percentage': 'Completion %', 'course_name': 'Course'},
                hover_data={'completed_count': True, 'total_count': True}
            )
            
            fig.update_layout(
                height=400,
                margin={'t': 40, 'b': 20, 'l': 20, 'r': 20},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#1F2937', 'size': 12},
                showlegend=False,
                title_font_size=16
            )
            
            fig.update_traces(
                texttemplate='%{x:.0f}%',
                textposition='inside',
                textfont_size=10
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No course progress data available")
    
    with chart_col2:
        st.markdown("### 🎯 Learning Analytics")
        
        # Overall progress gauge
        progress_fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=stats["progress_percentage"],
            delta={'reference': 70, 'position': "top"},
            title={'text': "Overall Completion", 'font': {'size': 16}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1},
                'bar': {'color': "#2563EB", 'thickness': 0.2},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E5E7EB",
                'steps': [
                    {'range': [0, 30], 'color': '#FEF3C7'},
                    {'range': [30, 60], 'color': '#DBEAFE'},
                    {'range': [60, 100], 'color': '#D1FAE5'}
                ],
                'threshold': {
                    'line': {'color': "#10B981", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        progress_fig.update_layout(
            height=250,
            margin={'t': 20, 'b': 20, 'l': 20, 'r': 20},
            font={'color': '#1F2937', 'size': 12},
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(progress_fig, use_container_width=True)
        
        # Category breakdown pie chart
        st.markdown("#### 📊 Course Categories")
        
        # Categorize courses based on names
        categories = []
        for course_name in courses.keys():
            if "Data Scientist" in course_name:
                categories.append("Data Science")
            elif "SQL" in course_name or "Analyst" in course_name:
                categories.append("Analytics")
            elif "ML" in course_name or "Machine Learning" in course_name:
                categories.append("ML/AI")
            elif "Power BI" in course_name or "BI" in course_name:
                categories.append("Business Intelligence")
            elif "Python" in course_name:
                categories.append("Programming")
            else:
                categories.append("General")
        
        if categories:
            category_counts = pd.Series(categories).value_counts()
            
            category_fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                color_discrete_sequence=[
                    '#2563EB', '#10B981', '#F59E0B', 
                    '#EF4444', '#8B5CF6', '#06B6D4'
                ]
            )
            
            category_fig.update_layout(
                height=200,
                margin={'t': 20, 'b': 20, 'l': 20, 'r': 20},
                font={'color': '#1F2937', 'size': 10},
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(category_fig, use_container_width=True)
    
    # === DETAILED PROGRESS TABLE ===
    st.markdown("---")
    st.markdown("### 📋 Detailed Course Summary")
    
    summary_data = []
    for course_name, course_data in courses.items():
        progress = calculate_course_progress(course_data)
        last_updated = course_data.get("_meta", {}).get("updated", "N/A")
        
        # Format last updated date
        if last_updated != "N/A" and isinstance(last_updated, str):
            try:
                dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                formatted_date = dt.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = last_updated
        else:
            formatted_date = "N/A"
        
        summary_data.append({
            "📚 Course Name": course_name,
            "📊 Total Modules": progress["total"],
            "✅ Completed": progress["completed"],
            "📈 Progress": f"{progress['percentage']:.1f}%",
            "🕒 Last Updated": formatted_date,
            "📝 Description": course_data.get('description', 'No description')[:50] + "..." if len(course_data.get('description', '')) > 50 else course_data.get('description', 'No description')
        })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        
        # Style the dataframe
        st.dataframe(
            summary_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        # Add export functionality
        st.markdown("#### 📤 Export Options")
        
        export_col1, export_col2, export_col3 = st.columns([1, 1, 2])
        
        with export_col1:
            if st.button("📁 Download CSV", use_container_width=True):
                csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download",
                    data=csv,
                    file_name=f"course_progress_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with export_col2:
            if st.button("📋 Copy Summary", use_container_width=True):
                summary_text = f"""
                📚 Course Progress Report - {datetime.now().strftime('%Y-%m-%d')}
                
                📊 Overall Statistics:
                • Total Courses: {stats['total_courses']}
                • Total Modules: {stats['total_modules']}
                • Completed Modules: {stats['completed_modules']}
                • Overall Progress: {stats['progress_percentage']:.1f}%
                
                📋 Course Details:
                """ + "\n".join([f"• {row['📚 Course Name']}: {row['✅ Completed']}/{row['📊 Total Modules']} ({row['📈 Progress']})" for _, row in summary_df.iterrows()])
                
                st.text_area("Copy this report:", value=summary_text, height=200)
        
        with export_col3:
            st.info("💡 **Tip:** Click on individual course tabs to see detailed progress and manage modules!")
    else:
        st.info("📚 No course data to display")

    # === RECENT ACTIVITY FEED ===
    st.markdown("---")
    st.markdown("### 🕒 Recent Learning Activity")
    
    # Mock recent activity data - in real implementation, this would come from timestamps
    recent_activities = [
        {"action": "Completed", "item": "Introduction to Python", "course": "Data Science Fundamentals", "time": "2 hours ago"},
        {"action": "Started", "item": "Data Manipulation with pandas", "course": "Data Science Fundamentals", "time": "1 day ago"},
        {"action": "Completed", "item": "SQL Joins", "course": "SQL for Analysts", "time": "2 days ago"},
        {"action": "Added", "item": "New course: Machine Learning Basics", "course": "System", "time": "3 days ago"},
    ]
    
    activity_col1, activity_col2 = st.columns([3, 1])
    
    with activity_col1:
        for activity in recent_activities:
            action_color = "#10B981" if activity["action"] == "Completed" else "#3B82F6" if activity["action"] == "Started" else "#F59E0B"
            action_icon = "✅" if activity["action"] == "Completed" else "▶️" if activity["action"] == "Started" else "➕"
            
            st.markdown(f"""
            <div style='
                background: var(--card-background);
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 4px solid {action_color};
                margin-bottom: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            '>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong style='color: {action_color};'>{action_icon} {activity["action"]}</strong>
                        <span style='color: var(--text-primary); margin-left: 8px;'>{activity["item"]}</span>
                    </div>
                    <small style='color: var(--text-secondary);'>{activity["time"]}</small>
                </div>
                <div style='color: var(--text-secondary); font-size: 12px; margin-top: 4px;'>
                    📚 {activity["course"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with activity_col2:
        st.markdown("""
        <div class="custom-card">
            <h4 style='color: var(--text-primary); margin-bottom: 16px;'>🎯 Quick Stats</h4>
            <div style='text-align: center;'>
                <div style='margin-bottom: 12px;'>
                    <div style='font-size: 24px; font-weight: bold; color: #10B981;'>4</div>
                    <div style='font-size: 12px; color: var(--text-secondary);'>Activities Today</div>
                </div>
                <div style='margin-bottom: 12px;'>
                    <div style='font-size: 24px; font-weight: bold; color: #3B82F6;'>2.5h</div>
                    <div style='font-size: 12px; color: var(--text-secondary);'>Time Spent</div>
                </div>
                <div>
                    <div style='font-size: 24px; font-weight: bold; color: #F59E0B;'>85%</div>
                    <div style='font-size: 12px; color: var(--text-secondary);'>Weekly Goal</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)