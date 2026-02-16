"""
SignFlow STMC (Sign Transition Motion Continuity) Model

PyTorch implementation for generating smooth transitions between signs.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, List
import numpy as np


class STMCModel(nn.Module):
    """
    Sequence-to-Sequence model with Attention for sign transitions.
    
    Architecture:
    - Encoder: Bi-LSTM for sign embeddings
    - Attention: Bahdanau attention
    - Decoder: LSTM generating transition keyframes
    """
    
    def __init__(
        self,
        embedding_dim: int = 256,
        hidden_dim: int = 512,
        num_layers: int = 2,
        dropout: float = 0.1,
        num_joints: int = 21  # Number of body joints to animate
    ):
        super(STMCModel, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_joints = num_joints
        
        # Encoder (Bi-LSTM)
        self.encoder = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention
        self.attention = nn.Linear(hidden_dim * 2, hidden_dim)
        
        # Decoder
        self.decoder = nn.LSTM(
            hidden_dim * 3,
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Output projection
        self.output_proj = nn.Linear(hidden_dim, num_joints * 4)  # 4 quaternions per joint
        
    def forward(
        self, 
        sign_a_embed: torch.Tensor, 
        sign_b_embed: torch.Tensor,
        transition_length: int = 30
    ) -> torch.Tensor:
        """
        Generate transition between two signs.
        
        Args:
            sign_a_embed: Embedding of first sign [batch, seq_len, embedding_dim]
            sign_b_embed: Embedding of second sign [batch, seq_len, embedding_dim]
            transition_length: Number of frames to generate
            
        Returns:
            Keyframes: [batch, transition_length, num_joints * 4]
        """
        batch_size = sign_a_embed.size(0)
        
        # Encode both signs
        encoder_output_a, (h_a, c_a) = self.encoder(sign_a_embed)
        encoder_output_b, (h_b, c_b) = self.encoder(sign_b_embed)
        
        # Use final states as decoder input
        decoder_hidden = torch.cat([h_a[-1], h_b[-1]], dim=1).unsqueeze(0)
        decoder_hidden = decoder_hidden.repeat(self.num_layers, 1, 1)
        
        decoder_cell = torch.cat([c_a[-1], c_b[-1]], dim=1).unsqueeze(0)
        decoder_cell = decoder_cell.repeat(self.num_layers, 1, 1)
        
        # Generate transition frames
        outputs = []
        current_input = torch.cat([encoder_output_a[:, -1:], encoder_output_b[:, :1]], dim=2)
        
        for t in range(transition_length):
            # Decode
            decoder_output, (decoder_hidden, decoder_cell) = self.decoder(
                current_input, (decoder_hidden, decoder_cell)
            )
            
            # Apply attention
            attn_weights = torch.softmax(
                self.attention(decoder_output), dim=1
            )
            context = torch.sum(attn_weights * encoder_output_a, dim=1, keepdim=True)
            
            # Generate keyframe
            keyframe = self.output_proj(decoder_output)
            outputs.append(keyframe)
            
            # Prepare next input (use predicted as next input for autoregressive)
            current_input = torch.cat([context, keyframe.unsqueeze(1)], dim=2)
        
        return torch.cat(outputs, dim=1)
    
    def predict_transition(
        self,
        sign_a_name: str,
        sign_b_name: str,
        sign_embeddings: dict
    ) -> np.ndarray:
        """
        Predict transition between two named signs.
        
        Args:
            sign_a_name: Name of first sign
            sign_b_name: Name of second sign
            sign_embeddings: Dictionary of sign name -> embedding
            
        Returns:
            Array of keyframe quaternions
        """
        self.eval()
        with torch.no_grad():
            embed_a = sign_embeddings.get(sign_a_name, torch.randn(1, 10, 256))
            embed_b = sign_embeddings.get(sign_b_name, torch.randn(1, 10, 256))
            
            keyframes = self.forward(embed_a, embed_b, transition_length=30)
            
            # Convert to numpy and reshape
            return keyframes.squeeze(0).cpu().numpy().reshape(-1, 4)


class GlossToPoseConverter:
    """
    Convert ASL Gloss notation to pose sequences.
    """
    
    def __init__(self, stmc_model: STMCModel):
        self.model = stmc_model
        self.gloss_vocab = {}
        
    def text_to_gloss(self, text: str) -> List[str]:
        """
        Simple text to gloss conversion.
        In production, use proper NLP for English->ASL grammar.
        """
        words = text.upper().split()
        return words
    
    def gloss_to_poses(self, gloss: List[str]) -> np.ndarray:
        """
        Convert gloss sequence to pose keyframes.
        """
        all_keyframes = []
        
        for i in range(len(gloss) - 1):
            sign_a = gloss[i]
            sign_b = gloss[i + 1]
            
            # Generate transition
            keyframes = self.model.predict_transition(sign_a, sign_b, {})
            all_keyframes.append(keyframes)
        
        return np.vstack(all_keyframes) if all_keyframes else np.array([])


def interpolate_linear(start: np.ndarray, end: np.ndarray, num_frames: int) -> np.ndarray:
    """
    Linear interpolation fallback when ML model unavailable.
    """
    alphas = np.linspace(0, 1, num_frames)
    frames = []
    for alpha in alphas:
        frame = (1 - alpha) * start + alpha * end
        frames.append(frame)
    return np.array(frames)


def smooth_motion(frames: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply Gaussian smoothing to motion keyframes.
    """
    from scipy.ndimage import gaussian_filter1d
    smoothed = np.apply_along_axis(
        gaussian_filter1d, 0, frames, sigma=kernel_size/3
    )
    return smoothed


# Example usage
if __name__ == "__main__":
    # Create model
    model = STMCModel(
        embedding_dim=256,
        hidden_dim=512,
        num_layers=2,
        num_joints=21
    )
    
    print(f"STMC Model Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Test forward pass
    dummy_input_a = torch.randn(1, 10, 256)
    dummy_input_b = torch.randn(1, 10, 256)
    output = model(dummy_input_a, dummy_input_b, transition_length=30)
    print(f"Output shape: {output.shape}")
