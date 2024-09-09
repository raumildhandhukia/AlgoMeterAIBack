from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from fastapi import FastAPI
from routes import main, user

app = FastAPI()

# Include the main router
app.include_router(main.router, prefix="/api")
app.include_router(user.router, prefix="/api/user")
@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)