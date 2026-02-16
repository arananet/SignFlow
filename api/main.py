"""
SignFlow API - FastAPI Backend

Translation API that bridges the web widget with the ML engine.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import redis
import json
import os

app = FastAPI(
    title="SignFlow API",
    description="Sign Language Translation API",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis cache
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    cache = redis.from_url(redis_url, decode_responses=True)
except:
    cache = None

# Data Models
class TranslationRequest(BaseModel):
    text: str
    fps: Optional[int] = 30

class Frame(BaseModel):
    RightArm: Optional[List[float]] = None
    RightForearm: Optional[List[float]] = None
    RightHand: Optional[List[float]] = None
    LeftArm: Optional[List[float]] = None
    LeftForearm: Optional[List[float]] = None
    LeftHand: Optional[List[float]] = None
    Head: Optional[List[float]] = None
    Neck: Optional[List[float]] = None

class TranslationResponse(BaseModel):
    text: str
    gloss: str
    fps: int
    frames: List[Frame]

# Routes
@app.get("/")
async def root():
    return {
        "service": "SignFlow API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "cache": "connected" if cache else "disconnected"
    }

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """
    Translate text to sign language animation
    
    Data Contract:
    {
      "text": "Hello",
      "fps": 30,
      "frames": [
        { "RightArm": [x, y, z, w], ... }
      ]
    }
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Check cache first
    if cache:
        cached = cache.get(f"translate:{text.lower()}")
        if cached:
            return TranslationResponse(**json.loads(cached))
    
    # TODO: Call STMC engine
    # For now, return mock data
    gloss = text.upper()
    
    # Generate mock frames
    frames = []
    for i in range(request.fps):
        frame = Frame(
            RightArm=[0.1, 0.2, 0.3, 0.9],
            RightForearm=[0.0, 0.5, 0.0, 0.8],
            RightHand=[0.0, 0.0, 0.0, 1.0],
            LeftArm=[-0.1, 0.2, -0.3, 0.9],
            LeftForearm=[0.0, -0.5, 0.0, 0.8],
            LeftHand=[0.0, 0.0, 0.0, 1.0],
            Head=[0.0, 0.0, 0.0, 1.0]
        )
        frames.append(frame)
    
    response = TranslationResponse(
        text=text,
        gloss=gloss,
        fps=request.fps,
        frames=frames
    )
    
    # Cache the result
    if cache:
        cache.setex(f"translate:{text.lower()}", 3600, response.model_dump_json())
    
    return response

@app.get("/gloss/{word}")
async def get_gloss(word: str):
    """Convert English word to ASL Gloss"""
    # TODO: Implement text-to-gloss conversion
    return {
        "word": word,
        "gloss": word.upper()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
