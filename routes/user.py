from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
import hashlib
import logging
from services.mongo import get_mongo_client
from bson.json_util import dumps, loads
from pymongo.errors import PyMongoError

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserData(BaseModel):
    data: Dict

def get_device_id(request: Request) -> str:
    user_agent = request.headers.get("User-Agent", "")
    ip_address = request.client.host
    fingerprint = f"{user_agent}{ip_address}"
    return hashlib.sha256(fingerprint.encode()).hexdigest()

@router.get("/")
async def get_data(request: Request):
    try:
        device_id = get_device_id(request)
        mongo_client = get_mongo_client()
        if not mongo_client:
            raise HTTPException(status_code=500, detail="Failed to connect to MongoDB")
        
        db = mongo_client['bigo']
        users_collection = db['users']
        analyses_collection = db['analyses']

        # Retrieve user data from MongoDB
        user = users_collection.find_one({"device_id": device_id})

        if user:
            # Retrieve all analyses for the user
            analyses = analyses_collection.find({"user_id":user['_id']})

            # Convert the analyses cursor to a list and handle BSON format
            analyses_list = loads(dumps(list(analyses)))
            # analyses_list = list(analyses.map(lambda x: x['']))

            return {
                "analyses": list(map(lambda analysis: { "time_complexity":analysis['time_complexity'],
                                                        "space_complexity":analysis['space_complexity'],
                                                        "explanation":analysis['explanation'],
                                                        "code_snippet":analysis['code_snippet'],
                                                        "created_at":analysis['created_at']
                                                        },
                                     analyses_list)),
            }
        else:
            return {"message": "No user found for this device"}
    except PyMongoError as e:
        logger.error(f"MongoDB error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")