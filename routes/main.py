import urllib.parse
import re
import json
import requests
from fastapi import APIRouter, HTTPException, Body, Request, Query
from fastapi.responses import JSONResponse
from core.analysis import analyze_code_snippet
from utility.redis_cache import get_cached_data, cache_data, invalidate_cache
import redis
import os
from core.user import store_user_analysis, get_device_id
from services.mongo import get_mongo_client
from datetime import datetime, UTC

# Redis configuration
REDIS_REMOTE_HOST = os.getenv("REDIS_REMOTE_HOST")
REDIS_REMOTE_DB_PORT = os.getenv("REDIS_REMOTE_DB_PORT")
REDIS_REMOTE_PASSWORD = os.getenv("REDIS_REMOTE_PASSWORD")
SCRAP_URL = os.getenv("SCRAP_URL")
router = APIRouter()

# Initialize Redis client
redis_client = redis.Redis(
  host=REDIS_REMOTE_HOST,
  port=REDIS_REMOTE_DB_PORT,
  password=REDIS_REMOTE_PASSWORD,
  ssl=True
)

# Rate limiting is now handled by middleware

def store_company_tags_access(request: Request, title_slug: str):
    """
    Store device ID in database for company-tags access
    
    Args:
        request: The incoming request
        title_slug: The LeetCode problem title slug
    """
    try:
        device_id = get_device_id(request)
        mongo_client = get_mongo_client()
        
        if mongo_client:
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
                        "company_tags_count": 1
                    }
                    user_collection.insert_one(user)
                else:
                    # Update user with company tags access
                    update_fields = {}
                    
                    # Increment company_tags_count if it exists, otherwise set it to 1
                    if "company_tags_count" in user:
                        update_fields["$inc"] = {"company_tags_count": 1}
                    else:
                        update_fields["$set"] = {"company_tags_count": 1}
                    
                    if update_fields:
                        user_collection.update_one(
                            {"_id": user['_id']},
                            update_fields,
                            upsert=True
                        )
                
                print(f"Successfully recorded company tags access for device {device_id}")
            except Exception as e:
                print(f"Error storing company tags access: {str(e)}")
            finally:
                mongo_client.close()
    except Exception as e:
        print(f"Error in device tracking: {str(e)}")

@router.get("/company-tags")
async def get_company_tags(
    request: Request, 
    url: str = Query(None, description="LeetCode problem URL to fetch company tags")
):
    print(f"Received request with URL parameter: {url}")
    # Check if URL parameter is provided
    if url is None:
        return JSONResponse(
            status_code=400,
            content={"detail": "Missing required query parameter 'url'"}
        )
    
    try:
        # Decode the URL parameter if it's encoded
        decoded_url = urllib.parse.unquote(url)
        print(f"Decoded URL: {decoded_url}")
        
        # Extract the problem title slug from the URL
        match = re.search(r'/problems/([^/]+)/', decoded_url)
        if not match:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid LeetCode problem URL"}
            )
            
        title_slug = match.group(1)
        print(f"Title slug: {title_slug}")
        
        # Store device ID in database for company-tags access
        store_company_tags_access(request, title_slug)
        
        # Create a cache key from the title slug
        cache_key = f"leetcode:company_tags:{title_slug}"
        
        # Try to get data from Redis cache
        cached_data, is_valid = get_cached_data(redis_client, cache_key)
        
        # If we have valid cached data (less than 14 days old), return it
        if cached_data and is_valid:
            print(f"Returning cached data for {title_slug}")
            return cached_data
        
        # If cache is invalid or doesn't exist, fetch fresh data
        print(f"Fetching fresh data for {title_slug}")
        
        # Use Playwright to fetch the page content (mimicking a real browser)
        # html_content, status_code = await fetch_leetcode_page_with_playwright(decoded_url)

        # First attempt to scrape the URL
        response = requests.get(SCRAP_URL + f"/api/scrape?url={url}")
        res = response.json()
        status_code = res.get("statusCode")
        company_tag_stats = res.get("companyTags")  # Get companyTags directly from the API response
        
        # If the first attempt fails with a non-200 status, try one more time
        if status_code != 200:
            print(f"First scraping attempt failed with status code: {status_code}. Retrying...")
            response = requests.get(SCRAP_URL + f"/api/scrape?url={url}")
            res = response.json()
            status_code = res.get("statusCode")
            company_tag_stats = res.get("companyTags")
        
        if status_code != 200 or not company_tag_stats:
            # If we have expired cached data, return it as a fallback
            if cached_data:
                print(f"Fetch failed, returning expired cached data for {title_slug}")
                return cached_data
                
            return JSONResponse(
                status_code=status_code or 500,
                content={
                    "detail": f"Failed to fetch data from LeetCode. Status code: {status_code}",
                }
            )
        
        # Parse the JSON string to a Python object
        try:
            parsed_data = json.loads(company_tag_stats)
            
            # Cache the parsed data in Redis
            cache_data(redis_client, cache_key, parsed_data)
            
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"Error parsing company tags JSON: {str(e)}")
            # If we have expired cached data, return it as a fallback
            if cached_data:
                print(f"JSON parse error, returning expired cached data for {title_slug}")
                return cached_data
                
            return JSONResponse(
                status_code=400,
                content={"error": "Could not parse company tags data"}
            )
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error: {str(e)}")
        print(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": str(e),
                "traceback": error_traceback
            }
        )

@router.post("/analyze")
async def analyze(request: Request, code_snippet: str = Body(..., embed=True)):
    result = analyze_code_snippet(code_snippet)
    
    if result["success"]:
        # Store user data asynchronously
        store_user_analysis(request, code_snippet, result["response"])
        return {"response": result["response"], "indices": result["indices"]}
    else:
        raise HTTPException(status_code=500, detail=result["error"])