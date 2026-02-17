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
import sys

API_URL = os.getenv("API_URL", "unknown")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from stmc_core.coordinate_converter import CoordinateConverter, GlossProcessor
    STMC_AVAILABLE = True
except ImportError:
    STMC_AVAILABLE = False
    print("Warning: STMC core not available, using mock data")
    
    # Mock classes for when STMC is not available
    class CoordinateConverter:
        def smooth_keyframes(self, frames, window_size=5):
            return frames
    
    class GlossProcessor:
        def text_to_gloss(self, text):
            return text.upper().split()

app = FastAPI(
    title="SignFlow API",
    description="Sign Language Translation API",
    version="0.1.0"
)

# CORS middleware - Allow any website to embed your widget
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Redis cache
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    cache = redis.from_url(redis_url, decode_responses=True)
except:
    cache = None

# Initialize processors (when available)
converter = CoordinateConverter() if STMC_AVAILABLE else None
gloss_processor = GlossProcessor() if STMC_AVAILABLE else None

# Data Models
class TranslationRequest(BaseModel):
    text: str
    target: Optional[str] = "ASL"
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
        "status": "running",
        "stmc_available": STMC_AVAILABLE
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "cache": "connected" if cache else "disconnected",
        "stmc": STMC_AVAILABLE
    }

@app.get("/test")
async def test():
    """Simple test endpoint"""
    return {"status": "ok", "message": "Backend is working!"}

@app.post("/test-post")
async def test_post(data: dict):
    """Test POST endpoint"""
    return {"status": "ok", "received": data}

@app.get("/debug")
async def debug():
    """Debug endpoint to check API status"""
    return {
        "status": "ok",
        "api_url": API_URL,
        "cache": "connected" if cache else "disconnected",
        "stmc_available": STMC_AVAILABLE,
        "converter": "initialized" if converter else "none",
        "gloss_processor": "initialized" if gloss_processor else "none"
    }

@app.post("/translate")
async def translate(request: TranslationRequest):
    import traceback
    try:
        text = request.text.strip() or "hello"
        
        # Simple mock response
        return {
            "text": text,
            "gloss": text.upper(),
            "fps": request.fps or 30,
            "frames": []
        }
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return {"error": str(e)}, 500

@app.get("/gloss/{word}")
async def get_gloss(word: str):
    """Convert English word to ASL Gloss"""
    if gloss_processor:
        gloss = gloss_processor.text_to_gloss(word)
        return {
            "word": word,
            "gloss": ' '.join(gloss)
        }
    return {
        "word": word,
        "gloss": word.upper()
    }

@app.post("/generate")
async def generate_from_gloss(gloss: List[str], fps: int = 30):
    """
    Generate animation directly from ASL Gloss.
    
    This bypasses NLP and goes straight to pose generation.
    """
    # TODO: Run STMC model on gloss sequence
    # For now, return placeholder
    return {
        "gloss": gloss,
        "fps": fps,
        "message": "STMC model integration pending"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
