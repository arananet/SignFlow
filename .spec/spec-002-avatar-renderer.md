# Spec 002: SignFlow Avatar Renderer

The Avatar Renderer takes motion keyframes and renders them as a fluid 3D animated avatar.

## Architecture

1.  **Rendering:** Three.js with React Three Fiber
2.  **Model:** GLTF 3D humanoid model
3.  **Animation:** Skeletal animation with bone manipulation

## Rendering Pipeline

**Input:**

- `keyframes` (array): Array of pose keyframes with timestamps
- `transition` (object): Transition type between signs

**Process:**

1.  **Skeleton Setup:** Load avatar skeleton bones
2.  **Pose Interpolation:** Interpolate between keyframes
3.  **Transition Blending:** Apply transition blending algorithm
4.  **Physics:** Add secondary motion (hair, clothes)
5.  **Lighting:** Apply scene lighting and shadows

**Output:**

- `canvas` (HTMLCanvasElement): Rendered avatar frame
- `stream` (MediaStream): Video stream for export

## Motion Smoothing

```
function smoothMotion(keyframes):
  for each bone in skeleton:
    positions = keyframes.map(k => k.bonePositions[bone])
    smoothed = applyGaussianFilter(positions)
    keyframes.bonePositions[bone] = smoothed
  return keyframes
```

## Performance Targets

- **60 FPS** during playback
- **< 100ms** initial load
- **< 500ms** transition between signs

## Failure Modes

1.  **Missing Bone:** Use default T-pose for that bone
2.  **Performance Drop:** Reduce frame rate, simplify physics
