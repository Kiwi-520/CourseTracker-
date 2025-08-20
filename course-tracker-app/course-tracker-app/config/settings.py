from pydantic import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017/"
    db_name: str = "course_tracker"
    app_title: str = "Course Tracker"
    app_icon: str = "📚"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"

    class Config:
        env_file = ".env"

settings = Settings()