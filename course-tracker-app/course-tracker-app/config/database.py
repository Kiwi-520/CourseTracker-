from pymongo import MongoClient
import os

def get_database():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DB_NAME", "course_tracker")
    
    client = MongoClient(mongo_uri)
    return client[db_name]