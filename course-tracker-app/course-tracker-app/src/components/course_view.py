import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.helpers import calculate_course_progress, get_recent_activities
from database.mongodb_client import save_courses

def display_course_dashboard(course_name, course_data):
    """Display individual course dashboard"""
    
    # Calculate course progress
    progress = calculate_course_progress(course_data)
    subcourses = course_data.get("subcourses", {})
    
    # === COURSE HEADER ===
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, var(--primary-blue-ultra-light) 0%, #DBEAFE 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #93C5FD;
        margin-bottom: 24px;
    '>
    """, unsafe_allow_html=True)
    
    header_col1, header_col2, header_col3 = st.columns([3, 2, 1])
    
    with header_col1:
        st.markdown(f"""
        <h2 style='
            color: var(--text-primary);
            font-size: 24px;
            font-weight: 700;
            margin: 0 0 8px 0;
        '>{course_name}</h2>
        <p style='
            color: var(--text-secondary);
            font-size: 14px;
            margin: 0;
        '>{course_data.get('description', 'Professional course curriculum')}</p>
        """, unsafe_allow_html=True)
    
    with header_col2:
        progress_value = progress["percentage"]
        st.markdown(f"""
        <div style='margin-top: 8px;'>
            <div style='
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 4px;
            '>
                <span style='color: var(--text-primary); font-weight: 600; font-size: 14px;'>Course Progress</span>
                <span style='color: var(--success-green); font-weight: 700; font-size: 16px;'>{progress_value:.0f}%</span>
            </div>
            <div style='
                background: var(--border-color);
                height: 8px;
                border-radius: 4px;
                overflow: hidden;
            '>
                <div style='
                    background: linear-gradient(90deg, var(--success-green) 0%, var(--success-green-light) 100%);
                    width: {progress_value}%;
                    height: 100%;
                    transition: width 0.3s ease;
                '></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with header_col3:
        st.metric(
            "Modules",
            value=f"{progress['completed']}/{progress['total']}",
            delta=f"{progress['percentage']:.1f}% Complete"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # === MAIN CONTENT LAYOUT ===
    content_col1, content_col2, content_col3 = st.columns([5, 4, 3], gap="large")
    
    # === COLUMN 1: MODULE MANAGEMENT ===
    with content_col1:
        st.markdown("""
        <div class="custom-card" style='height: 600px; overflow-y: auto;'>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📚 Course Modules")
        
        # Create unique form key for this course
        form_key = f"add_module_{course_name.replace(' ', '_').replace('-', '_')}"
        
        # Add new module form
        with st.form(form_key):
            new_module = st.text_input("Add New Module", placeholder="Enter module name...")
            module_type = st.selectbox("Module Type", ["Lesson", "Exercise", "Project", "Assessment", "Video"])
            
            col_add, col_cancel = st.columns(2)
            with col_add:
                add_clicked = st.form_submit_button("➕ Add Module", use_container_width=True)
            with col_cancel:
                st.form_submit_button("❌ Clear", use_container_width=True)
            
            if add_clicked and new_module:
                if new_module not in subcourses:
                    subcourses[new_module] = {
                        "completed": False,
                        "created": datetime.now().isoformat(),
                        "updated": datetime.now().isoformat(),
                        "type": module_type
                    }
                    
                    # Update session state and save to database
                    st.session_state["courses"][course_name]["subcourses"] = subcourses
                    save_courses(st.session_state["courses"])
                    
                    st.success(f"✅ Added module: {new_module}")
                    st.rerun()
                else:
                    st.error("❌ Module already exists!")
        
        if subcourses:
            st.markdown("---")
            st.markdown(f"**Total Modules: {len(subcourses)}**")
            
            # Module filters with unique keys
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                show_completed = st.checkbox("Show Completed", value=True, key=f"show_completed_{course_name}")
            with filter_col2:
                show_pending = st.checkbox("Show Pending", value=True, key=f"show_pending_{course_name}")
            
            # Display modules
            displayed_count = 0
            for idx, (module_name, module_data) in enumerate(subcourses.items()):
                is_completed = module_data.get("completed", False)
                
                # Apply filters
                if (is_completed and not show_completed) or (not is_completed and not show_pending):
                    continue
                
                displayed_count += 1
                
                # Module row with unique keys
                col_check, col_content, col_actions = st.columns([0.5, 8, 1.5])
                
                # Create unique key for each checkbox
                checkbox_key = f"check_{course_name}_{idx}_{module_name}".replace(' ', '_').replace('-', '_')
                
                with col_check:
                    completed = st.checkbox(
                        "",
                        value=is_completed,
                        key=checkbox_key,
                        label_visibility="collapsed"
                    )
                
                with col_content:
                    status_color = "#10B981" if completed else "#9CA3AF"
                    status_text = "✅ Completed" if completed else "⏳ Pending"
                    module_type = module_data.get('type', 'Module')
                    completion_date = module_data.get("completion_date", "")
                    
                    st.markdown(f"""
                    <div style='
                        padding: 12px 0;
                        border-bottom: 1px solid #F3F4F6;
                    '>
                        <div style='
                            display: flex;
                            justify-content: space-between;
                            align-items: flex-start;
                            margin-bottom: 4px;
                        '>
                            <h4 style='
                                color: var(--text-primary);
                                font-size: 14px;
                                font-weight: 600;
                                margin: 0;
                                line-height: 1.4;
                            '>{module_name}</h4>
                            <span style='
                                background: {status_color}20;
                                color: {status_color};
                                padding: 2px 8px;
                                border-radius: 12px;
                                font-size: 10px;
                                font-weight: 500;
                                white-space: nowrap;
                            '>{module_type}</span>
                        </div>
                        <div style='
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        '>
                            <span style='
                                color: {status_color};
                                font-size: 12px;
                                font-weight: 500;
                            '>{status_text}</span>
                            {f"<span style='color: var(--text-secondary); font-size: 11px;'>{completion_date}</span>" if completed and completion_date else ""}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create unique key for delete button
                delete_key = f"delete_{course_name}_{idx}_{module_name}".replace(' ', '_').replace('-', '_')
                
                with col_actions:
                    if st.button("🗑️", key=delete_key, help="Delete module"):
                        del subcourses[module_name]
                        st.session_state["courses"][course_name]["subcourses"] = subcourses
                        save_courses(st.session_state["courses"])
                        st.rerun()
                
                # Update completion status if changed
                if completed != is_completed:
                    subcourses[module_name]["completed"] = completed
                    subcourses[module_name]["updated"] = datetime.now().isoformat()
                    if completed:
                        subcourses[module_name]["completion_date"] = datetime.now().strftime("%Y-%m-%d")
                        st.balloons()  # Celebration effect
                    elif "completion_date" in subcourses[module_name]:
                        del subcourses[module_name]["completion_date"]
                    
                    st.session_state["courses"][course_name]["subcourses"] = subcourses
                    save_courses(st.session_state["courses"])
                    st.rerun()
            
            if displayed_count == 0:
                st.info("No modules match the selected filters.")
                
        else:
            st.info("📝 No modules added yet. Create your first module above!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # === COLUMN 2: PROGRESS ANALYTICS ===
    with content_col2:
        st.markdown("""
        <div class="custom-card" style='height: 600px;'>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📈 Progress Analytics")
        
        if subcourses:
            # Progress over time (mock data)
            st.markdown("#### 📅 Learning Timeline")
            
            # Generate mock progress data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Simulate cumulative progress
            daily_progress = np.random.choice([0, 1, 2], size=len(date_range), p=[0.7, 0.25, 0.05])
            cumulative_progress = np.cumsum(daily_progress)
            max_progress = max(cumulative_progress) if max(cumulative_progress) > 0 else 1
            normalized_progress = (cumulative_progress / max_progress) * progress["percentage"]
            
            progress_df = pd.DataFrame({
                'Date': date_range,
                'Progress': normalized_progress
            })
            
            timeline_fig = px.line(
                progress_df,
                x='Date',
                y='Progress',
                title='30-Day Progress Timeline',
                color_discrete_sequence=['#2563EB']
            )
            
            timeline_fig.update_layout(
                height=200,
                margin={'t': 40, 'b': 20, 'l': 20, 'r': 20},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#1F2937', 'size': 11}
            )
            
            timeline_fig.update_traces(line_width=3)
            st.plotly_chart(timeline_fig, use_container_width=True)
            
            # Module types breakdown
            st.markdown("#### 🏷️ Module Types")
            
            module_types = [data.get("type", "Module") for data in subcourses.values()]
            type_counts = pd.Series(module_types).value_counts()
            
            types_fig = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                color_discrete_sequence=['#10B981', '#F59E0B', '#3B82F6', '#EF4444', '#8B5CF6']
            )
            
            types_fig.update_traces(hole=0.4)
            types_fig.update_layout(
                height=200,
                margin={'t': 20, 'b': 20, 'l': 20, 'r': 20},
                font={'color': '#1F2937', 'size': 10},
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(types_fig, use_container_width=True)
            
            # Completion rate gauge
            st.markdown("#### 🎯 Completion Rate")
            
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=progress["percentage"],
                title={'text': "Course Completion"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#2563EB"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 100], 'color': "lightblue"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            gauge_fig.update_layout(
                height=150,
                margin={'t': 20, 'b': 20, 'l': 20, 'r': 20},
                font={'size': 10},
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(gauge_fig, use_container_width=True)
            
        else:
            st.info("📊 Add modules to see detailed analytics")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # === COLUMN 3: QUICK ACTIONS & DETAILS ===
    with content_col3:
        st.markdown("""
        <div class="custom-card" style='height: 600px; overflow-y: auto;'>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚡ Quick Actions")
        
        # Create unique keys for bulk action buttons
        mark_complete_key = f"mark_complete_{course_name}".replace(' ', '_').replace('-', '_')
        reset_progress_key = f"reset_progress_{course_name}".replace(' ', '_').replace('-', '_')
        
        # Bulk action buttons
        if st.button("✅ Mark All Complete", use_container_width=True, type="primary", key=mark_complete_key):
            for module_name in subcourses:
                subcourses[module_name]["completed"] = True
                subcourses[module_name]["updated"] = datetime.now().isoformat()
                subcourses[module_name]["completion_date"] = datetime.now().strftime("%Y-%m-%d")
            
            st.session_state["courses"][course_name]["subcourses"] = subcourses
            save_courses(st.session_state["courses"])
            st.success("🎉 All modules completed!")
            st.balloons()
            st.rerun()
        
        if st.button("↺ Reset All Progress", use_container_width=True, key=reset_progress_key):
            for module_name in subcourses:
                subcourses[module_name]["completed"] = False
                subcourses[module_name]["updated"] = datetime.now().isoformat()
                if "completion_date" in subcourses[module_name]:
                    del subcourses[module_name]["completion_date"]
            
            st.session_state["courses"][course_name]["subcourses"] = subcourses
            save_courses(st.session_state["courses"])
            st.success("↺ Progress reset!")
            st.rerun()
        
        # Course statistics
        st.markdown("---")
        st.markdown("### 📊 Course Stats")
        
        stats_container = st.container()
        with stats_container:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total", progress["total"])
                st.metric("Completed", progress["completed"])
            
            with col2:
                st.metric("Pending", progress["total"] - progress["completed"])
                st.metric("Progress", f"{progress['percentage']:.1f}%")
        
        # Estimated completion
        if progress["total"] > 0 and progress["completed"] > 0:
            remaining = progress["total"] - progress["completed"]
            # Assume 1 module per day (mock calculation)
            estimated_days = remaining
            completion_date = datetime.now() + timedelta(days=estimated_days)
            
            st.markdown("---")
            st.markdown("### 🎯 Estimated Completion")
            st.info(f"📅 **{completion_date.strftime('%B %d, %Y')}**\n\n"
                   f"🕒 Approx. {estimated_days} days remaining\n\n"
                   f"📈 Based on current progress rate")
        
        # Course notes with unique key
        st.markdown("---")
        st.markdown("### 📝 Course Notes")
        
        notes_key = f"notes_{course_name}".replace(' ', '_').replace('-', '_')
        
        notes = st.text_area(
            "",
            value=course_data.get("notes", ""),
            placeholder="Add your course notes, insights, or reminders...",
            height=100,
            key=notes_key
        )
        
        # Auto-save notes when changed
        if notes != course_data.get("notes", ""):
            st.session_state["courses"][course_name]["notes"] = notes
            save_courses(st.session_state["courses"])
        
        # Recent course activity
        st.markdown("---")
        st.markdown("### 🕒 Recent Activity")
        
        # Get recent activities for this course
        course_activities = get_recent_activities({course_name: course_data}, limit=5)
        
        if course_activities:
            for activity in course_activities:
                st.markdown(f"""
                <div style='
                    padding: 8px 12px;
                    background: var(--primary-blue-ultra-light);
                    border-radius: 6px;
                    border-left: 3px solid var(--success-green);
                    margin-bottom: 8px;
                '>
                    <div style='
                        font-size: 12px;
                        color: var(--text-primary);
                        font-weight: 500;
                        margin-bottom: 2px;
                    '>{activity['title']}</div>
                    <div style='
                        font-size: 10px;
                        color: var(--text-secondary);
                    '>{activity.get('timestamp', 'Recently')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("📝 No recent activity")
        
        st.markdown("</div>", unsafe_allow_html=True)