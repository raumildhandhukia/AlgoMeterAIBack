import json
import time
from datetime import datetime, timedelta
import os


# Cache expiration time (14 days in seconds)
CACHE_EXPIRY_SECONDS = 14 * 24 * 60 * 60
CACHE_EXPIRY_SECONDS_ENV = int(os.getenv("CACHE_EXPIRY_SECONDS", CACHE_EXPIRY_SECONDS))

def get_cached_data(redis_client, key):
    """
    Get data from Redis cache if it exists and is not expired.
    
    Args:
        redis_client: Redis client instance
        key: Cache key (usually the decoded URL)
        
    Returns:
        Tuple of (data, is_valid):
        - data: The cached data or None if not found
        - is_valid: Boolean indicating if the data is valid (not expired)
    """
    try:
        # Try to get the cached data
        cached_data = redis_client.get(key)
        
        if not cached_data:
            return None, False
        
        # Parse the cached data
        data_dict = json.loads(cached_data)
        
        # Check if the timestamp exists and data is not expired
        if 'timestamp' in data_dict:
            timestamp = data_dict['timestamp']
            current_time = int(time.time())
            
            # Check if data is less than 14 days old
            if current_time - timestamp < CACHE_EXPIRY_SECONDS_ENV:
                return data_dict['data'], True
                
        # Data exists but is expired
        return data_dict['data'], False
        
    except Exception as e:
        print(f"Error retrieving data from Redis: {str(e)}")
        return None, False

def cache_data(redis_client, key, data):
    """
    Cache data in Redis with current timestamp.
    
    Args:
        redis_client: Redis client instance
        key: Cache key (usually the decoded URL)
        data: Data to cache
        
    Returns:
        Boolean indicating if caching was successful
    """
    try:
        # Create a dictionary with data and timestamp
        cache_dict = {
            'data': data,
            'timestamp': int(time.time())
        }
        
        # Store in Redis
        redis_client.set(key, json.dumps(cache_dict))
        return True
    except Exception as e:
        print(f"Error caching data in Redis: {str(e)}")
        return False

def invalidate_cache(redis_client, key):
    """
    Invalidate (delete) cached data for a specific key.
    
    Args:
        redis_client: Redis client instance
        key: Cache key to invalidate
        
    Returns:
        Boolean indicating if invalidation was successful
    """
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Error invalidating Redis cache: {str(e)}")
        return False
