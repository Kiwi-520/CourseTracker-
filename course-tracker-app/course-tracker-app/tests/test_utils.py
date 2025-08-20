import pytest
from src.utils.helpers import format_course_data, calculate_progress_percentage

def test_format_course_data():
    course_data = {
        "course_name": "Data Science",
        "subcourses": {
            "Python Basics": {"completed": True},
            "Machine Learning": {"completed": False}
        },
        "description": "Learn the fundamentals of Data Science."
    }
    
    expected_output = {
        "name": "Data Science",
        "modules": {
            "Python Basics": {"completed": True},
            "Machine Learning": {"completed": False}
        },
        "description": "Learn the fundamentals of Data Science."
    }
    
    formatted_data = format_course_data(course_data)
    assert formatted_data == expected_output

def test_calculate_progress_percentage():
    subcourses = {
        "Module 1": {"completed": True},
        "Module 2": {"completed": False},
        "Module 3": {"completed": True}
    }
    
    progress = calculate_progress_percentage(subcourses)
    expected_progress = (2 / 3) * 100  # 2 completed out of 3 total
    assert progress == expected_progress

    empty_subcourses = {}
    progress_empty = calculate_progress_percentage(empty_subcourses)
    assert progress_empty == 0  # No modules should result in 0% progress