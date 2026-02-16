# Spec 003: STMC Transition Model

The STMC (Sign Transition Motion Continuity) model predicts smooth transitions between signs using machine learning.

## Architecture

1.  **ML Framework:** TensorFlow.js
2.  **Model Type:** Sequence-to-Sequence (Seq2Seq) with Attention
3.  **Input:** Sign pair embeddings
4.  **Output:** Transition keyframes

## Model Architecture

```
Input: [Sign_A_Embedding, Sign_B_Embedding]
  ↓
Encoder: Bi-LSTM
  ↓
Attention Layer
  ↓
Decoder: LSTM → Transition Keyframes
  ↓
Output: [Frame_1, Frame_2, ..., Frame_N] (interpolated poses)
```

## Training Data

- **Source:** ASL and LSE sign language datasets
- **Annotation:** Human-labeled sign boundaries and transitions
- **Size:** ~10,000 sign pairs with transitions

## Inference

**Input:**

- `sign_a` (embedding): End pose of current sign
- `sign_b` (embedding): Start pose of next sign

**Process:**

1.  Encode both sign embeddings
2.  Apply attention mechanism
3.  Generate transition frames
4.  Apply temporal smoothing

**Output:**

- `keyframes` (array): Array of interpolated poses

## Fallback

If ML model unavailable, use **linear interpolation** between sign poses.

## Performance

- **< 50ms** inference on modern devices
- **~30 frames** per transition
- **Quantized** for mobile deployment
