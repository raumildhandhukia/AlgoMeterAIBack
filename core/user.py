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
        
        # Check if user exists
        user = user_collection.find_one({"device_id": device_id})
        
        if not user:
            # Create new user if not exists
            user = {
                "device_id": device_id,
                "created_at": datetime.now(UTC),
                "analysis_count": 1
            }
            user_collection.insert_one(user)
        else:
            # Increment analysis count for existing user
            user_collection.update_one(
                {"_id": user['_id']},
                {"$inc": {"analysis_count": 1}},
                upsert=True
            )
        
        print(f"Successfully incremented analysis count for device {device_id}")
    except Exception as e:
        print(f"Database operation failed: {str(e)}")
    finally:
        mongo_client.close()

def get_device_id(request: Request) -> str:
    user_agent = request.headers.get("User-Agent", "")
    ip_address = request.client.host
    fingerprint = f"{user_agent}{ip_address}"
    return hashlib.sha256(fingerprint.encode()).hexdigest()