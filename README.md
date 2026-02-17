# SignFlow

<img src="assets/logo.svg" alt="SignFlow Logo" width="200"/>

**Motion Continuity for Natural Sign Language Avatars**

> "The future of sign language is fluid, connected, and beautiful."

---

## Why SignFlow?

Traditional sign language avatars often feel **"stiff"** because they treat signs as individual blocks—choppy, robotic, and hard for native signers to understand.

**SignFlow solves this with Motion Continuity (STMC):**

- Focuses on the **transitions between signs** — the "connective tissue" of movement
- Creates fluid, natural motion that mirrors how native signers actually communicate
- Significantly easier for deaf and hard-of-hearing users to understand

---

## The Problem

    [HELLO] --> [HOW] --> [ARE] --> [YOU]
      |         |        |        |
    Block    Block    Block   Block
      |         |        |        |
    Choppy   Choppy   Choppy  Choppy

Each sign is treated as a separate, disconnected animation. The result feels robotic and loses the natural flow of sign language.

---

## The SignFlow Solution

    [HELLO] === [HOWT === [ARE] === [YOU]
      |          |          |          |
  Transition  Transition  Transition  Transition
      |          |          |          |
     Fluid     Fluid     Fluid      Fluid

STMC (Sign Transition Motion Continuity) analyzes the space between signs and generates smooth, natural transitions.

---

## Architecture - The 3 Pillars

    WIDGET          API             STMC
    (Frontend)  --> (Backend)   -->  (ML AI)
        |              |              |
        |              |              |
        v              v              v
   WebGL Render   Redis Cache   Pose Generation
    3D Avatar    Translation   Text-to-Gloss

**Pipeline:**
1. User highlights text → Widget captures
2. Widget → API (FastAPI)
3. API checks Redis cache
4. Cache miss → NLP → STMC Model → Coordinates
5. Return JSON frames → Widget renders 3D avatar

### 1. The Web Widget (Frontend)
- **Framework:** Vanilla JS + Three.js
- **Purpose:** Embeddable web component that captures text, renders 3D avatar
- **Output:** WebGL animation rendered in browser

### 2. The Translation API (Backend)
- **Framework:** Python FastAPI
- **Purpose:** Bridge between widget and ML engine
- **Features:** Redis caching for instant responses

### 3. The Inference Engine (ML Core)
- **Framework:** PyTorch
- **Purpose:** Text-to-Gloss + Gloss-to-Pose generation
- **Model:** STMC (Sign Transition Motion Continuity)

---

## Data Flow

    1. User highlights text
           |
           v
    2. Widget captures & POST to /translate
           |
           v
    3. API checks Redis cache
           |
           +--> Cache hit --> Return frames
           |
           v (cache miss)
    4. NLP: Text --> ASL Gloss
           |
           v
    5. STMC Model generates poses
           |
           v
    6. Return JSON frames to widget
           |
           v
    7. Three.js renders 3D avatar

---

## API Data Contract

```json
{
  "text": "Hello",
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

---

## Getting Started

```bash
git clone https://github.com/arananet/SignFlow.git
cd SignFlow
docker-compose up
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Widget | Vanilla JS, Three.js, WebGL |
| API | Python, FastAPI, Redis |
| ML | PyTorch |
| 3D Models | GLTF/GLB, Blender |

---

## License

MIT — SignFlow is open source.

---

**Developer:** Eduardo Arana  
**Assistant:** Soda 🥤
