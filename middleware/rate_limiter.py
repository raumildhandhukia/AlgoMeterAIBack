import time
import hashlib
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import os
import redis

# Rate limiting configuration from environment variables
MAX_REQUESTS = int(os.getenv("API_MAX_REQUESTS", 10))
TIME_FRAME = int(os.getenv("API_TIME_FRAME", 60))

# Redis configuration
REDIS_REMOTE_HOST = os.getenv("REDIS_REMOTE_HOST")
REDIS_REMOTE_DB_PORT = os.getenv("REDIS_REMOTE_DB_PORT")
REDIS_REMOTE_PASSWORD = os.getenv("REDIS_REMOTE_PASSWORD")

# Initialize Redis client
redis_client = redis.Redis(
    host=REDIS_REMOTE_HOST,
    port=REDIS_REMOTE_DB_PORT,
    password=REDIS_REMOTE_PASSWORD,
    ssl=True
)

def get_device_id(request: Request) -> str:
    """Generate a unique identifier for the client based on IP and user agent"""
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    identifier = f"{ip}:{user_agent}"
    return hashlib.md5(identifier.encode()).hexdigest()

async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to apply rate limiting to all API requests.
    
    Args:
        request: The incoming request
        call_next: The next middleware or route handler
        
    Returns:
        The response from the next middleware or route handler, or a 429 response if rate limited
    """
    # Skip rate limiting for certain paths if needed
    if request.url.path in ["/docs", "/redoc", "/openapi.json"] or request.url.path == "/api/company-tags":
        return await call_next(request)
    
    # Get device ID
    device_id = get_device_id(request)
    
    # Check rate limit
    is_allowed, seconds_left = check_rate_limit(device_id)
    
    if not is_allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded", "seconds_left": seconds_left}
        )
    
    # If not rate limited, proceed with the request
    return await call_next(request)

def check_rate_limit(device_id: str) -> tuple[bool, int]:
    """
    Check if the client has exceeded the rate limit.
    
    Args:
        device_id: Unique identifier for the client
        
    Returns:
        Tuple of (is_allowed, seconds_left)
    """
    try:
        current_time = int(time.time())
        key = f"rate_limit:{device_id}"
        
        # Remove requests older than the time frame
        redis_client.zremrangebyscore(key, 0, current_time - TIME_FRAME)
        
        # Count recent requests
        recent_requests = redis_client.zrange(key, 0, -1, withscores=True)
        
        if len(recent_requests) < MAX_REQUESTS:
            # Add the current request timestamp
            redis_client.zadd(key, {current_time: current_time})
            redis_client.expire(key, TIME_FRAME)
            return True, 0
        else:
            # Calculate time until oldest request expires
            oldest_timestamp = recent_requests[0][1] if recent_requests else current_time
            reset_time = oldest_timestamp + TIME_FRAME
            seconds_left = max(0, int(reset_time - current_time))
            return False, seconds_left
    except Exception as e:
        print(f"Rate limiting error: {str(e)}")
        # In case of error, allow the request to proceed
        return True, 0
