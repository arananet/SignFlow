# Spec 001: SignFlow Core Engine

SignFlow Core Engine orchestrates the sign language translation pipeline, connecting the web widget to the ML inference engine via a FastAPI backend.

## Overview

The system follows a three-pillar architecture:

```
WIDGET (Frontend)  →  API (Backend)  →  STMC (ML Core)
     ↓                    ↓                  ↓
  WebGL Render       Redis Cache       Pose Generation
   Three.js           FastAPI            PyTorch
```

## Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Widget | Vanilla JS + Three.js | Captures text, renders 3D avatar |
| API | Python FastAPI | Translation endpoint, Redis caching |
| STMC Core | PyTorch | Seq2Seq pose generation model |
| Cache | Redis 7 | Response caching (1 hour TTL) |

## API Contract

### POST `/translate`

**Request:**
```json
{
  "text": "Hello how are you",
  "fps": 30
}
```

**Response:**
```json
{
  "text": "Hello how are you",
  "gloss": "HELLO HOW YOU",
  "fps": 30,
  "frames": [
    {
      "RightArm": [0.1, 0.2, 0.3, 0.9],
      "RightForearm": [0.0, 0.5, 0.0, 0.8],
      "LeftArm": [-0.1, 0.2, -0.3, 0.9],
      "Head": [0.0, 0.0, 0.0, 1.0]
    }
  ]
}
```

### GET `/gloss/{word}`

Returns ASL Gloss for a single word.

### GET `/health`

Returns service status including cache and STMC availability.

## Data Flow

1. User highlights text → Widget captures
2. Widget POSTs to `/translate`
3. API checks Redis cache (key: `translate:{text.lower()}`)
4. Cache miss → NLP converts text to ASL Gloss
5. STMC model generates pose keyframes
6. CoordinateConverter smooths quaternions
7. Response cached for 1 hour
8. Widget receives JSON frames → Three.js renders

## Error Handling

| HTTP Status | Condition | Behavior |
|-------------|-----------|----------|
| 400 | Empty text | Return error message |
| 500 | STMC unavailable | Use mock animation fallback |
| 503 | Redis down | Continue without caching |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `PYTHONUNBUFFERED` | `1` | Disable output buffering |

## Deployment

```bash
docker-compose up
```

Services exposed:
- API: `http://localhost:8000`
- Widget: `http://localhost:3000`
- Redis: `localhost:6379`

