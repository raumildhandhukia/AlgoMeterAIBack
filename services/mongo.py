from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import certifi

uri = os.getenv("DB_URI")

def get_mongo_client():
    try:
        client = MongoClient(uri, 
                             server_api=ServerApi('1'),
                             serverSelectionTimeoutMS=5000,  # 5 second timeout
                             connectTimeoutMS=5000,
                             socketTimeoutMS=5000,
                             tlsAllowInvalidCertificates=True,  # Add this line
                             tlsCAFile=certifi.where())  # Add this line
        
        # Force a connection attempt
        client.admin.command('ismaster')
        print("Successfully connected to MongoDB!")
        return client
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None
    except ServerSelectionTimeoutError as e:
        print(f"Server selection timeout: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def close_mongo_client(client):
    if client:
        client.close()
        print("MongoDB connection closed.")

def ping_mongo_client(client):
    if not client:
        print("No MongoDB client provided.")
        return
    try:
        client.admin.command('ping')
        print("Successfully pinged MongoDB deployment.")
    except Exception as e:
        print(f"Failed to ping MongoDB: {e}")
