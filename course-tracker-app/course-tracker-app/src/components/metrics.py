from pymongo import MongoClient

def calculate_course_stats(courses):
    total_courses = len(courses)
    total_modules = sum(len(course_data.get("subcourses", {})) for course_data in courses.values())
    completed_modules = sum(
        sum(1 for subdata in course_data.get("subcourses", {}).values() 
            if subdata.get("completed", False))
        for course_data in courses.values()
    )
    
    progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    
    return {
        "total_courses": total_courses,
        "total_modules": total_modules,
        "completed_modules": completed_modules,
        "progress_percentage": progress_percentage,
        "courses_in_progress": sum(1 for course_data in courses.values() 
                                 if any(subdata.get("completed", False) 
                                       for subdata in course_data.get("subcourses", {}).values())),
        "avg_progress": progress_percentage
    }

def display_metrics(stats):
    """Display metrics in the Streamlit app"""
    import streamlit as st
    
    st.metric("Total Courses", str(stats["total_courses"]))
    st.metric("Completed", f"{stats['completed_modules']}/{stats['total_modules']}")
    
    progress_value = stats["progress_percentage"] / 100 if stats["progress_percentage"] > 0 else 0
    st.progress(progress_value)
    st.text(f"{stats['progress_percentage']:.1f}% Complete")