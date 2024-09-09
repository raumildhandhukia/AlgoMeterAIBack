from fastapi import Request
from services.mongo import get_mongo_client
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
import hashlib
from datetime import datetime, UTC

def store_user_analysis(request: Request, code_snippet: str, analysis: dict):
    device_id = get_device_id(request)
    mongo_client = get_mongo_client()
    if not mongo_client:
        print("Failed to connect to database")
        return
    
    try:
        db = mongo_client['bigo']
        user_collection = db['users']
        analysis_collection = db['analyses']
        
        # Check if user exists
        user = user_collection.find_one({"device_id": device_id})
        
        if not user:
            # Create new user if not exists
            user = {
                "device_id": device_id,
                "created_at": datetime.now(UTC),
                "analyses": []
            }
            user_result = user_collection.insert_one(user)
            user_id = user_result.inserted_id
        else:
            user_id = user['_id']
        
        # Create new analysis document
        new_analysis = {
            "user_id": user_id,
            "code_snippet": code_snippet,
            "time_complexity": analysis['time_complexity'],
            "space_complexity": analysis['space_complexity'],
            "explanation": analysis['explanation'],
            "created_at": datetime.now(UTC)
        }
        analysis_result = analysis_collection.insert_one(new_analysis)
        
        # Update user document with reference to the new analysis
        user_collection.update_one(
            {"_id": user_id},
            {"$push": {"analyses": analysis_result.inserted_id}}
        )
        
        print(f"Successfully stored analysis for device {device_id}")
    except Exception as e:
        print(f"Database operation failed: {str(e)}")
    finally:
        mongo_client.close()

def get_device_id(request: Request) -> str:
    user_agent = request.headers.get("User-Agent", "")
    ip_address = request.client.host
    fingerprint = f"{user_agent}{ip_address}"
    return hashlib.sha256(fingerprint.encode()).hexdigest()