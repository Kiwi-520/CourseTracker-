from datetime import datetime
import pandas as pd

def calculate_course_stats(courses):
    """Calculate comprehensive course statistics"""
    if not courses:
        return {
            "total_courses": 0,
            "total_modules": 0,
            "completed_modules": 0,
            "progress_percentage": 0
        }
    
    total_courses = len(courses)
    total_modules = 0
    completed_modules = 0
    
    for course_name, course_data in courses.items():
        subcourses = course_data.get("subcourses", {})
        total_modules += len(subcourses)
        completed_modules += sum(1 for sub_data in subcourses.values() 
                               if sub_data.get("completed", False))
    
    progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    
    return {
        "total_courses": total_courses,
        "total_modules": total_modules,
        "completed_modules": completed_modules,
        "progress_percentage": progress_percentage
    }

def calculate_course_progress(course_data):
    """Calculate progress for a single course"""
    if not course_data:
        return {
            "total": 0,
            "completed": 0,
            "percentage": 0,
            "remaining": 0
        }
    
    subcourses = course_data.get("subcourses", {})
    total = len(subcourses)
    completed = sum(1 for sub_data in subcourses.values() if sub_data.get("completed", False))
    percentage = (completed / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "completed": completed,
        "percentage": percentage,
        "remaining": total - completed
    }

def get_recent_activities(courses, limit=5):
    """Get recent activities from course updates"""
    activities = []
    
    for course_name, course_data in courses.items():
        subcourses = course_data.get("subcourses", {})
        for sub_name, sub_data in subcourses.items():
            if sub_data.get("completed", False):
                completion_date = sub_data.get("completion_date", "")
                updated_time = sub_data.get("updated", "")
                
                activities.append({
                    "title": f"Completed: {sub_name}",
                    "course": course_name,
                    "timestamp": completion_date or updated_time or datetime.now().isoformat(),
                    "type": "completion",
                    "module_type": sub_data.get("type", "Module")
                })
    
    # Sort by timestamp (most recent first)
    activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return activities[:limit]

def format_duration(minutes):
    """Format duration in minutes to human readable format"""
    if minutes < 60:
        return f"{minutes}m"
    elif minutes < 1440:  # Less than 24 hours
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    else:
        days = minutes // 1440
        hours = (minutes % 1440) // 60
        return f"{days}d {hours}h" if hours > 0 else f"{days}d"

def get_completion_streak(courses):
    """Calculate current completion streak in days"""
    # This is a mock implementation
    # In a real app, you'd track daily completion data
    return 12

def get_study_statistics(courses):
    """Get detailed study statistics"""
    stats = calculate_course_stats(courses)
    
    if not courses:
        return {**stats, "avg_progress": 0, "courses_not_started": 0, "courses_in_progress": 0, "courses_completed": 0, "completion_rate": 0}
    
    # Calculate additional metrics
    course_progress_list = []
    for course_name, course_data in courses.items():
        progress = calculate_course_progress(course_data)
        course_progress_list.append(progress["percentage"])
    
    avg_progress = sum(course_progress_list) / len(course_progress_list) if course_progress_list else 0
    
    # Count courses by status
    not_started = sum(1 for p in course_progress_list if p == 0)
    in_progress = sum(1 for p in course_progress_list if 0 < p < 100)
    completed = sum(1 for p in course_progress_list if p == 100)
    
    return {
        **stats,
        "avg_progress": avg_progress,
        "courses_not_started": not_started,
        "courses_in_progress": in_progress,
        "courses_completed": completed,
        "completion_rate": (completed / len(course_progress_list) * 100) if course_progress_list else 0
    }