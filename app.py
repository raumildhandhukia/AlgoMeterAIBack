from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from fastapi import FastAPI
from routes import analyze

app = FastAPI()

# Include the analyze router
app.include_router(analyze.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)