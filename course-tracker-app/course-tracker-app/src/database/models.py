from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Subcourse(BaseModel):
    name: str
    completed: bool = False
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

class Course(BaseModel):
    course_name: str
    description: Optional[str] = None
    subcourses: Dict[str, Subcourse] = Field(default_factory=dict)
    total_modules: int = 0

    def add_subcourse(self, subcourse_name: str):
        if subcourse_name not in self.subcourses:
            self.subcourses[subcourse_name] = Subcourse(name=subcourse_name)
            self.total_modules += 1

    def remove_subcourse(self, subcourse_name: str):
        if subcourse_name in self.subcourses:
            del self.subcourses[subcourse_name]
            self.total_modules -= 1

    def update_subcourse(self, subcourse_name: str, completed: bool):
        if subcourse_name in self.subcourses:
            self.subcourses[subcourse_name].completed = completed
            self.subcourses[subcourse_name].updated = datetime.now()

class CourseTracker(BaseModel):
    courses: Dict[str, Course] = Field(default_factory=dict)

    def add_course(self, course_name: str, description: Optional[str] = None):
        if course_name not in self.courses:
            self.courses[course_name] = Course(course_name=course_name, description=description)

    def remove_course(self, course_name: str):
        if course_name in self.courses:
            del self.courses[course_name]