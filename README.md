# SignFlow 🦋

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

```
Traditional Avatar Motion:

[HELLO] → [HOW] → [ARE] → [YOU]
  ⬇️       ⬇️       ⬇️      ⬇️
 Block    Block    Block   Block
   ↓        ↓        ↓       ↓
 Choppy   Choppy   Choppy  Choppy
```

Each sign is treated as a separate, disconnected animation. The result feels robotic and loses the natural flow of sign language.

---

## The SignFlow Solution

```
SignFlow Motion Continuity:

[HELLO] ═══ [HOW] ═══ [ARE] ═══ [YOU]
  ⬇️         ⬇️         ⬇️        ⬇️
 Transition  Transition Transition
   ↓           ↓          ↓         ↓
  Fluid      Fluid      Fluid     Fluid
```

**STMC (Sign Transition Motion Continuity)** analyzes the space between signs and generates smooth, natural transitions that mirror human signing patterns.

---

## Architecture - The 3 Pillars

```mermaid
flowchart LR
    subgraph User
        Text[User highlights text]
    end
    
    subgraph Widget["Widget (Frontend)"]
        DOM[DOM Injection]
        Three[Three.js Render]
    end
    
    subgraph API["Translation API"]
        Fast[FastAPI]
        Redis[(Redis Cache)]
    end
    
    subgraph ML["STMC Core"]
        NLP[NLP Processor]
        STMC[STMC Model]
        Convert[Coordinate Converter]
    end
    
    Text --> DOM --> Fast
    Fast -->|cache hit| Redis
    Fast -->|cache miss| NLP
    NLP --> STMC
    STMC --> Convert
    Convert --> Three
```

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

```mermaid
sequenceDiagram
    participant User
    participant Widget
    participant API
    participant Redis
    participant NLP
    participant STMC
    participant Three

    User->>Widget: Highlights text
    Widget->>API: POST /translate
    
    alt Cache Hit
        API->>Redis: Check cache
        Redis-->>API: Return cached
    else Cache Miss
        API->>NLP: Text → ASL Gloss
        NLP-->>API: Gloss
        API->>STMC: Generate keyframes
        STMC-->>API: Pose data
        API->>Redis: Cache result
    end
    
    API-->>Widget: Return frames
    Widget->>Three: Apply rotations
    Three-->>User: Render 3D
```

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
| ML | PyTorch, TensorFlow |
| 3D Models | GLTF/GLB, Blender |

---

## License

MIT — SignFlow is open source.

---

**Developer:** Eduardo Arana  
**Assistant:** Soda 🥤
