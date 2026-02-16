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

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from stmc_core.coordinate_converter import CoordinateConverter, GlossProcessor
    STMC_AVAILABLE = True
except ImportError:
    STMC_AVAILABLE = False
    print("Warning: STMC core not available, using mock data")

app = FastAPI(
    title="SignFlow API",
    description="Sign Language Translation API",
    version="0.1.0"
)

# CORS middleware - Allow any website to embed your widget
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any website to embed your widget
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

# Initialize processors (when available)
converter = CoordinateConverter() if STMC_AVAILABLE else None
gloss_processor = GlossProcessor() if STMC_AVAILABLE else None

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

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """
    Translate text to sign language animation
    
    Pipeline:
    1. Text → ASL Gloss (NLP)
    2. Gloss → Pose Keyframes (STMC Model)
    3. Poses → Quaternions (Coordinate Converter)
    
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
    
    # === STEP 1: Text to Gloss ===
    if gloss_processor:
        gloss = gloss_processor.text_to_gloss(text)
        gloss_str = ' '.join(gloss)
    else:
        gloss_str = text.upper()
    
    # === STEP 2 & 3: Generate poses and convert to quaternions ===
    # TODO: Load PyTorch Model and run inference
    # For now, generate mock animation
    
    frames = []
    num_frames = request.fps
    
    for i in range(num_frames):
        # Animate the arms for demonstration
        phase = (i / num_frames) * 3.14159 * 2  # Full cycle
        
        frame = Frame(
            RightArm=[0.1 * (1 + 0.3 * phase), 0.2, 0.3, 0.9],
            RightForearm=[0.0, 0.5 + 0.2 * phase, 0.0, 0.8],
            RightHand=[0.0, 0.0, 0.0, 1.0],
            LeftArm=[-0.1 * (1 + 0.3 * phase), 0.2, -0.3, 0.9],
            LeftForearm=[0.0, -0.5 - 0.2 * phase, 0.0, 0.8],
            LeftHand=[0.0, 0.0, 0.0, 1.0],
            Head=[0.0, 0.1 * phase, 0.0, 1.0]
        )
        frames.append(frame)
    
    # Apply smoothing
    if converter and len(frames) > 5:
        frame_dicts = [f.dict() for f in frames]
        smoothed = converter.smooth_keyframes(frame_dicts, window_size=5)
        frames = [Frame(**f) for f in smoothed]
    
    response = TranslationResponse(
        text=text,
        gloss=gloss_str,
        fps=request.fps,
        frames=frames
    )
    
    # Cache the result (1 hour)
    if cache:
        cache.setex(f"translate:{text.lower()}", 3600, response.model_dump_json())
    
    return response

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
