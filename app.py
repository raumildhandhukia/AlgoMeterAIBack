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

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # only this domain is allowed
    allow_credentials=True,
    allow_methods=["*"],  # you can restrict methods (e.g., GET, POST) if needed
    allow_headers=["*"],  # you can restrict headers if needed
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