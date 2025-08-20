import pytest
from src.components.sidebar import Sidebar
from src.components.dashboard import Dashboard
from src.components.course_view import CourseView
from src.components.metrics import calculate_course_stats

def test_sidebar_initialization():
    sidebar = Sidebar()
    assert sidebar is not None
    assert sidebar.title == "Course Tracker"

def test_dashboard_initialization():
    dashboard = Dashboard()
    assert dashboard is not None
    assert dashboard.title == "Learning Overview"

def test_course_view_initialization():
    course_view = CourseView()
    assert course_view is not None
    assert course_view.title == "Course View"

def test_calculate_course_stats():
    courses = {
        "Course A": {
            "subcourses": {
                "Module 1": {"completed": True},
                "Module 2": {"completed": False}
            }
        },
        "Course B": {
            "subcourses": {
                "Module 1": {"completed": True},
                "Module 2": {"completed": True}
            }
        }
    }
    stats = calculate_course_stats(courses)
    assert stats["total_courses"] == 2
    assert stats["total_modules"] == 4
    assert stats["completed_modules"] == 4
    assert stats["progress_percentage"] == 100.0
    assert stats["courses_in_progress"] == 0
    assert stats["avg_progress"] == 100.0