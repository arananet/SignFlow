# Spec 001: SignFlow Core Engine

SignFlow Core Engine performs sign language tokenization and motion synthesis using STMC (Sign Transition Motion Continuity).

## Architecture

1.  **Framework:** Node.js + React (Frontend)
2.  **3D Rendering:** Three.js + @react-three/fiber
3.  **ML:** TensorFlow.js for transition prediction
4.  **State:** None (stateless rendering)

## Core Logic

**Input:**

- `text` (string): Text to convert to sign language

**Process:**

1.  **Sign Segmentation:** Tokenize text into atomic signs
2.  **Transition Analysis:** For each sign pair, predict transition type
3.  **Motion Synthesis:** Generate smooth motion keyframes
4.  **Avatar Rendering:** Render 3D avatar with smooth transitions

**Output:**

- `video` (MediaStream): Signed animation
- `duration` (number): Total duration in seconds

## STMC Algorithm

```
For each sign in sequence:
  1. Load sign keyframes (start, hold, end)
  2. Calculate transition to next sign
  3. Generate interpolated frames
  4. Apply physics smoothing
```

## Failure Modes

1.  **Unknown Sign:** Skip and log warning, continue with next sign
2.  **ML Model Error:** Fallback to linear interpolation
3.  **Render Error:** Return static image of sign

## Deployment

- **Frontend:** Vercel/Cloudflare Pages
- **ML Model:** Bundled with TensorFlow.js
- **CI/CD:** GitHub Actions
