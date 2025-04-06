from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from fastapi import FastAPI
from routes import main, user
from fastapi.middleware.cors import CORSMiddleware
from middleware.rate_limiter import rate_limit_middleware

DOMAIN = os.getenv("DOMAIN")

app = FastAPI()

# Define allowed origins
origins = [
    "https://www.algometerai.com",
    "https://algometerai.com",
    "https://leetcode.com",
    "https://www.leetcode.com",
    "http://localhost:3000",  # For local development
    "http://127.0.0.1:3000"   # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specific domains are allowed, not wildcard
    allow_credentials=True,  # Allow credentials (cookies)
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Length"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Include the main router
app.include_router(main.router, prefix="/api")

# app.include_router(user.router, prefix="/api/user")
# @app.get("/")
# async def root():
#     return {"message": "Hello Raumil"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)