import urllib.parse
import re
import json
from fastapi import APIRouter, HTTPException, Body, Request, Query
from fastapi.responses import JSONResponse
from core.analysis import analyze_code_snippet
from utility.playwright import fetch_leetcode_page_with_playwright  
from utility.beautiful_soup import get_leetcode_company_tags
from utility.redis_cache import get_cached_data, cache_data, invalidate_cache
import redis
import os
from core.user import store_user_analysis

# Redis configuration
REDIS_REMOTE_HOST = os.getenv("REDIS_REMOTE_HOST")
REDIS_REMOTE_DB_PORT = os.getenv("REDIS_REMOTE_DB_PORT")
REDIS_REMOTE_PASSWORD = os.getenv("REDIS_REMOTE_PASSWORD")

router = APIRouter()

# Initialize Redis client
redis_client = redis.Redis(
  host=REDIS_REMOTE_HOST,
  port=REDIS_REMOTE_DB_PORT,
  password=REDIS_REMOTE_PASSWORD,
  ssl=True
)

# Rate limiting is now handled by middleware

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
        html_content, status_code = await fetch_leetcode_page_with_playwright(decoded_url)
        
        if status_code != 200 or not html_content:
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
        
        # Extract company tags from HTML content
        company_tag_stats = get_leetcode_company_tags(html_content)
        
        if company_tag_stats:
            # Parse the JSON string to a Python object
            parsed_data = json.loads(company_tag_stats)
            
            # Cache the parsed data in Redis
            cache_data(redis_client, cache_key, parsed_data)
            
            return parsed_data
        else:
            # If we have expired cached data, return it as a fallback
            if cached_data:
                print(f"No new data found, returning expired cached data for {title_slug}")
                return cached_data
                
            return JSONResponse(
                status_code=404,
                content={"error": "Could not find companyTagStatsV2 data for this problem"}
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