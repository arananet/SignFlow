# Spec 003: STMC Transition Model

The STMC (Sign Transition Motion Continuity) model generates smooth pose transitions between signs using PyTorch.

## Overview

| Aspect | Value |
|--------|-------|
| Framework | PyTorch |
| Architecture | Seq2Seq with Bahdanau Attention |
| Location | `stmc_core/stmc_model.py` |
| Output | Quaternion keyframes per joint |

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    STMCModel                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Sign A Embed ──┐                                       │
│                 ├──► Bi-LSTM Encoder ──► Context        │
│  Sign B Embed ──┘           │                           │
│                             ▼                           │
│                    Bahdanau Attention                   │
│                             │                           │
│                             ▼                           │
│                      LSTM Decoder                       │
│                             │                           │
│                             ▼                           │
│              Linear Projection (num_joints * 4)         │
│                             │                           │
│                             ▼                           │
│              Output: [batch, frames, joints*4]          │
│                      (quaternions)                      │
└─────────────────────────────────────────────────────────┘
```

## Class Reference

### `STMCModel(nn.Module)`

**File:** `stmc_core/stmc_model.py`

**Constructor Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `embedding_dim` | int | 256 | Input embedding dimension |
| `hidden_dim` | int | 512 | LSTM hidden state size |
| `num_layers` | int | 2 | LSTM layer count |
| `dropout` | float | 0.1 | Dropout probability |
| `num_joints` | int | 21 | Body joints to animate |

**Layers:**
- `encoder`: `nn.LSTM` — Bidirectional, `batch_first=True`
- `attention`: `nn.Linear(hidden_dim * 2, hidden_dim)`
- `decoder`: `nn.LSTM` — Unidirectional
- `output_proj`: `nn.Linear(hidden_dim, num_joints * 4)`

## Inference API

```python
def forward(
    self, 
    sign_a_embed: torch.Tensor,  # [batch, seq_len, embedding_dim]
    sign_b_embed: torch.Tensor,  # [batch, seq_len, embedding_dim]
    transition_length: int = 30   # frames to generate
) -> torch.Tensor:
    """
    Returns: [batch, transition_length, num_joints * 4]
    """
```

## Supporting Classes

### `CoordinateConverter`

**File:** `stmc_core/coordinate_converter.py`

Converts MediaPipe/SMPL-X landmarks to Three.js quaternions.

**Methods:**
- `landmarks_to_quaternions(landmarks, format)` → `Dict[str, List[float]]`
- `smooth_keyframes(frames, window_size)` → `List[Dict]`

### `GlossProcessor`

Converts English text to ASL Gloss notation.

**Methods:**
- `text_to_gloss(text)` → `List[str]`

## Output Format

Each frame contains quaternion rotations `[x, y, z, w]` for:

```python
[
    'RightArm', 'RightForearm', 'RightHand',
    'LeftArm', 'LeftForearm', 'LeftHand',
    'Head', 'Neck', 'Spine',
    # ... additional joints
]
```

## Performance

| Metric | Target |
|--------|--------|
| Inference Time | < 100ms |
| Frames per Transition | 30 |
| Model Size | ~50MB |

## Fallback

If model unavailable (`STMC_AVAILABLE = False` in API), return mock animation with sinusoidal arm movements.
