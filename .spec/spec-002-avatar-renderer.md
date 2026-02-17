# Spec 002: SignFlow Avatar Renderer

The Avatar Renderer uses vanilla Three.js to render sign language animations on a skeletal 3D avatar.

## Overview

| Aspect | Technology |
|--------|------------|
| Rendering | Three.js (vanilla, no React) |
| Model Format | GLTF/GLB humanoid |
| Animation | Skeletal bone manipulation via quaternions |
| Language | TypeScript |

## TypeScript Interfaces

```typescript
// Quaternion rotation per bone
export interface Frame {
  [bone: string]: number[]; // [x, y, z, w]
}

// Animation data from API
export interface AnimationData {
  text: string;
  fps: number;
  frames: Frame[];
}
```

## Class Architecture

### `AvatarRenderer`

**File:** `widget/src/engine/renderer.ts`

**Properties:**
- `scene: THREE.Scene` — 3D scene container
- `camera: THREE.PerspectiveCamera` — 45° FOV, positioned at (0, 1.5, 4)
- `renderer: THREE.WebGLRenderer` — Antialiased, shadow-enabled
- `skeleton: THREE.Skeleton` — Humanoid bone hierarchy
- `bones: Map<string, THREE.Bone>` — Named bone lookup
- `mixer: THREE.AnimationMixer` — Animation playback controller

**Methods:**
- `createSkeleton(): THREE.Skeleton` — Builds bone hierarchy
- `createAvatarMesh(): void` — Attaches skinned mesh to skeleton
- `playAnimation(data: AnimationData): void` — Applies JSON frames to bones
- `animate(): void` — Render loop (requestAnimationFrame)

## Bone Hierarchy

```
Root
└── Spine
    ├── Neck
    │   └── Head
    ├── LeftShoulder
    │   └── LeftArm
    │       └── LeftForearm
    │           └── LeftHand (+ 5 fingers)
    └── RightShoulder
        └── RightArm
            └── RightForearm
                └── RightHand (+ 5 fingers)
```

## Rendering Pipeline

1. **Initialize:** Create scene, camera, renderer, lights
2. **Load Model:** GLTFLoader fetches avatar.glb
3. **Map Bones:** Traverse model, populate `bones` Map
4. **Receive Animation:** API returns `AnimationData`
5. **Apply Frames:** For each frame, set bone quaternions
6. **Render Loop:** `requestAnimationFrame` at 60 FPS

## Lighting Setup

- Ambient light: `0xffffff` intensity `0.6`
- Directional light: `0xffffff` intensity `0.8`, position `(5, 10, 5)`, shadows enabled

## Performance Targets

| Metric | Target |
|--------|--------|
| Frame Rate | 60 FPS |
| Initial Load | < 100ms |
| Avatar Model | < 2MB |

## Fallback Behavior

- **Model Load Failure:** Render placeholder avatar (geometric primitives)
- **Missing Bone:** Use identity quaternion `[0, 0, 0, 1]`
- **Performance Drop:** Reduce to 30 FPS
