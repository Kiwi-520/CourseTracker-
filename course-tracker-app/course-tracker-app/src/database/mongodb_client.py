from pymongo import MongoClient
import streamlit as st
from datetime import datetime
import os

def get_db():
    """Connect to MongoDB and return the database"""
    try:
        # Try to get MongoDB URI from environment variable first
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri)
        
        # Test the connection
        client.admin.command('ping')
        
        db = client["course_tracker"]
        return db
    except Exception as e:
        st.error(f"❌ Failed to connect to MongoDB: {e}")
        st.info("💡 Make sure MongoDB is running on your system, or we'll use local storage")
        return None

@st.cache_data
def load_courses():
    """Load courses from MongoDB or local storage"""
    db = get_db()
    if db is not None:
        try:
            courses_collection = db["courses"]
            doc = courses_collection.find_one({"_id": "main"})
            
            if doc and "courses" in doc:
                return doc["courses"]
            else:
                # Return empty dict if no data found
                return {}
        except Exception as e:
            st.error(f"❌ Error loading courses from MongoDB: {e}")
            # Fall back to session state if MongoDB fails
            return st.session_state.get("courses_backup", {})
    else:
        # Use session state as fallback when MongoDB is not available
        return st.session_state.get("courses_backup", {})

def save_courses(courses):
    """Save courses to MongoDB and local backup"""
    # Always save to session state as backup
    st.session_state["courses_backup"] = courses
    
    db = get_db()
    if db is not None:
        try:
            courses_collection = db["courses"]
            
            # Update the document with timestamp
            result = courses_collection.update_one(
                {"_id": "main"},
                {
                    "$set": {
                        "courses": courses,
                        "last_updated": datetime.now().isoformat()
                    }
                },
                upsert=True
            )
            
            # Clear the cache to ensure fresh data on next load
            load_courses.clear()
            
            return result.acknowledged
        except Exception as e:
            st.error(f"❌ Error saving courses to MongoDB: {e}")
            st.info("💡 Data saved locally but not synced to database")
            return False
    else:
        # When MongoDB is not available, just confirm local save
        st.info("💾 Data saved locally (MongoDB not connected)")
        return True

def backup_data():
    """Create a backup of all course data"""
    db = get_db()
    if db is not None:
        try:
            courses_collection = db["courses"]
            backup_collection = db["courses_backup"]
            
            # Get current data
            current_data = courses_collection.find_one({"_id": "main"})
            
            if current_data:
                # Add backup timestamp
                backup_doc = {
                    **current_data,
                    "_id": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "backup_created": datetime.now().isoformat()
                }
                
                result = backup_collection.insert_one(backup_doc)
                return result.acknowledged
            else:
                st.warning("⚠️ No data found to backup")
                return False
                
        except Exception as e:
            st.error(f"❌ Error creating backup: {e}")
            return False
    return False

def restore_data(backup_id):
    """Restore data from a specific backup"""
    db = get_db()
    if db is not None:
        try:
            courses_collection = db["courses"]
            backup_collection = db["courses_backup"]
            
            # Get backup data
            backup_data = backup_collection.find_one({"_id": backup_id})
            
            if backup_data:
                # Restore the data (remove backup-specific fields)
                restore_doc = {
                    "_id": "main",
                    "courses": backup_data.get("courses", {}),
                    "last_updated": datetime.now().isoformat(),
                    "restored_from": backup_id,
                    "restored_at": datetime.now().isoformat()
                }
                
                result = courses_collection.replace_one(
                    {"_id": "main"},
                    restore_doc,
                    upsert=True
                )
                
                # Clear cache
                load_courses.clear()
                
                return result.acknowledged
            else:
                st.error(f"❌ Backup {backup_id} not found")
                return False
                
        except Exception as e:
            st.error(f"❌ Error restoring data: {e}")
            return False
    return False

def get_backup_list():
    """Get list of available backups"""
    db = get_db()
    if db is not None:
        try:
            backup_collection = db["courses_backup"]
            backups = backup_collection.find({}, {"_id": 1, "backup_created": 1}).sort("backup_created", -1)
            
            backup_list = []
            for backup in backups:
                backup_list.append({
                    "id": backup["_id"],
                    "created": backup.get("backup_created", "Unknown"),
                    "formatted_date": datetime.fromisoformat(backup.get("backup_created", "")).strftime("%Y-%m-%d %H:%M:%S") if backup.get("backup_created") else "Unknown"
                })
            
            return backup_list
        except Exception as e:
            st.error(f"❌ Error getting backup list: {e}")
            return []
    return []

def delete_backup(backup_id):
    """Delete a specific backup"""
    db = get_db()
    if db is not None:
        try:
            backup_collection = db["courses_backup"]
            result = backup_collection.delete_one({"_id": backup_id})
            return result.deleted_count > 0
        except Exception as e:
            st.error(f"❌ Error deleting backup: {e}")
            return False
    return False

def get_database_stats():
    """Get database statistics"""
    db = get_db()
    if db is not None:
        try:
            courses_collection = db["courses"]
            backup_collection = db["courses_backup"]
            
            # Get document count and size
            courses_count = courses_collection.count_documents({})
            backup_count = backup_collection.count_documents({})
            
            # Get database stats
            db_stats = db.command("dbStats")
            
            return {
                "courses_documents": courses_count,
                "backup_documents": backup_count,
                "database_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0),
                "indexes": db_stats.get("indexes", 0),
                "collections": db_stats.get("collections", 0)
            }
        except Exception as e:
            st.error(f"❌ Error getting database stats: {e}")
            return {}
    return {}

def export_to_json():
    """Export all course data to JSON format"""
    db = get_db()
    if db is not None:
        try:
            courses_collection = db["courses"]
            doc = courses_collection.find_one({"_id": "main"})
            
            if doc:
                import json
                # Remove MongoDB-specific _id field
                export_data = {
                    "courses": doc.get("courses", {}),
                    "exported_at": datetime.now().isoformat(),
                    "export_version": "1.0"
                }
                return json.dumps(export_data, indent=2, default=str)
            else:
                return None
        except Exception as e:
            st.error(f"❌ Error exporting data: {e}")
            return None
    else:
        # Export from session state if MongoDB not available
        try:
            import json
            export_data = {
                "courses": st.session_state.get("courses_backup", {}),
                "exported_at": datetime.now().isoformat(),
                "export_version": "1.0"
            }
            return json.dumps(export_data, indent=2, default=str)
        except Exception as e:
            st.error(f"❌ Error exporting data: {e}")
            return None

def import_from_json(json_data):
    """Import course data from JSON"""
    db = get_db()
    try:
        import json
        data = json.loads(json_data)
        
        if "courses" in data:
            courses = data["courses"]
            
            # Save to session state first
            st.session_state["courses_backup"] = courses
            
            if db is not None:
                courses_collection = db["courses"]
                
                # Create backup before importing
                backup_result = backup_data()
                if backup_result:
                    st.success("✅ Backup created before import")
                
                # Import the data
                import_doc = {
                    "_id": "main",
                    "courses": courses,
                    "last_updated": datetime.now().isoformat(),
                    "imported_at": datetime.now().isoformat()
                }
                
                result = courses_collection.replace_one(
                    {"_id": "main"},
                    import_doc,
                    upsert=True
                )
                
                # Clear cache
                load_courses.clear()
                
                return result.acknowledged
            else:
                st.info("💾 Data imported locally (MongoDB not connected)")
                return True
        else:
            st.error("❌ Invalid JSON format - missing 'courses' field")
            return False
            
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON format: {e}")
        return False
    except Exception as e:
        st.error(f"❌ Error importing data: {e}")
        return False

def check_connection():
    """Check if MongoDB connection is working"""
    db = get_db()
    return db is not None

def initialize_database():
    """Initialize the database with default structure if needed"""
    db = get_db()
    if db is not None:
        try:
            courses_collection = db["courses"]
            
            # Check if main document exists
            doc = courses_collection.find_one({"_id": "main"})
            
            if not doc:
                # Create initial document
                initial_doc = {
                    "_id": "main",
                    "courses": {},
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
                
                courses_collection.insert_one(initial_doc)
                st.success("✅ Database initialized successfully")
                return True
            else:
                return True
                
        except Exception as e:
            st.error(f"❌ Error initializing database: {e}")
            return False
    return False