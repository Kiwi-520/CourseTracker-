from pymongo import MongoClient
import pytest
from src.database.mongodb_client import get_db
from src.database.models import Course

@pytest.fixture(scope="module")
def db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["course_tracker_test"]
    yield db
    client.drop_database("course_tracker_test")

def test_get_db(db):
    assert db.name == "course_tracker_test"

def test_course_model(db):
    course_data = {
        "course_name": "Test Course",
        "subcourses": {},
        "description": "A course for testing.",
        "total_modules": 0
    }
    course = Course(**course_data)
    db.courses.insert_one(course.__dict__)

    retrieved_course = db.courses.find_one({"course_name": "Test Course"})
    assert retrieved_course["course_name"] == "Test Course"
    assert retrieved_course["description"] == "A course for testing."
    assert retrieved_course["total_modules"] == 0

def test_course_deletion(db):
    db.courses.delete_many({"course_name": "Test Course"})
    assert db.courses.find_one({"course_name": "Test Course"}) is None