import hashlib
import time
from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from core.analysis import analyze_code_snippet
import redis
import os

from core.user import store_user_analysis

REDIS_REMOTE_HOST = os.getenv("REDIS_REMOTE_HOST")
REDIS_REMOTE_DB_PORT = os.getenv("REDIS_REMOTE_DB_PORT")
REDIS_REMOTE_PASSWORD = os.getenv("REDIS_REMOTE_PASSWORD")
MAX_REQUESTS = int(os.getenv("API_MAX_REQUESTS"))
TIME_FRAME = int(os.getenv("API_TIME_FRAME"))


router = APIRouter()

redis_client = redis.Redis(
  host=REDIS_REMOTE_HOST,
  port=REDIS_REMOTE_DB_PORT,
  password=REDIS_REMOTE_PASSWORD,
  ssl=True
)

def get_device_id(request: Request) -> str:
    user_agent = request.headers.get("User-Agent", "")
    ip_address = request.client.host
    fingerprint = f"{user_agent}{ip_address}"
    return hashlib.sha256(fingerprint.encode()).hexdigest()

def rate_limit(device_id: str) -> tuple[bool, int]:
    current_time = int(time.time())
    key = f"api_rate_limit:{device_id}"

    with redis_client.pipeline() as pipe:
        pipe.zremrangebyscore(key, 0, current_time - TIME_FRAME)  # remove expired
        pipe.zrange(key, 0, -1, withscores=True)  # get requests after filtration
        results = pipe.execute()
    
    recent_requests = results[1]
    request_count = len(recent_requests)
    
    if request_count < MAX_REQUESTS:
        # Only add the new request if the limit is not exceeded
        redis_client.zadd(key, {current_time: current_time})
        redis_client.expire(key, TIME_FRAME)
        return True, 0
    else:
        oldest_timestamp = recent_requests[0][1] if recent_requests else current_time
        reset_time = oldest_timestamp + TIME_FRAME
        seconds_left = max(0, int(reset_time - current_time))
        return False, seconds_left

@router.post("/analyze")
async def analyze(request: Request, code_snippet: str = Body(..., embed=True)):
    device_id = get_device_id(request)
    try:
        is_allowed, seconds_left = rate_limit(device_id)
    except Exception as e:
        print(f"Rate limiting error: {str(e)}")
        is_allowed, seconds_left = False, 300
    
    if not is_allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded", "seconds_left": seconds_left}
        )
    
    result = analyze_code_snippet(code_snippet)
    
    if result["success"]:
        # Store user data asynchronously
        store_user_analysis(request, code_snippet, result["response"])
        return {"response": result["response"], "indices": result["indices"]}
    else:
        raise HTTPException(status_code=500, detail=result["error"])