"""
SignFlow Coordinate Conversion Layer

Converts AI model outputs (SMPL-X, MediaPipe) to Three.js quaternion rotations.

This is the critical "translation layer" between ML spatial data and 3D avatar bones.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json


class CoordinateConverter:
    """
    Converts AI landmark coordinates to Three.js bone rotations.
    
    Supported input formats:
    - SMPL-X: 55 hand joints + 55 hand joints + 104 body joints
    - MediaPipe: 33 body landmarks + 21 hand landmarks x 2
    
    Output:
    - Three.js bone rotations (quaternions x, y, z, w)
    """
    
    # Mapping from MediaPipe landmarks to Three.js bones
    MEDIAPIPE_TO_BONE = {
        # Body (33 points)
        'nose': 'Head',
        'left_eye_inner': 'Head',
        'left_eye': 'Head',
        'left_eye_outer': 'Head',
        'right_eye_inner': 'Head',
        'right_eye': 'Head',
        'right_eye_outer': 'Head',
        'left_ear': 'Head',
        'right_ear': 'Head',
        'mouth_left': 'Head',
        'mouth_right': 'Head',
        
        # Shoulders
        'left_shoulder': 'LeftShoulder',
        'right_shoulder': 'RightShoulder',
        
        # Elbows
        'left_elbow': 'LeftArm',
        'right_elbow': 'RightArm',
        
        # Wrists
        'left_wrist': 'LeftHand',
        'right_wrist': 'RightHand',
        
        # Hip
        'left_hip': 'Spine',
        'right_h hip': 'Spine',
    }
    
    # Standard avatar skeleton (simplified)
    BONE_HIERARCHY = {
        'Root': None,
        'Spine': 'Root',
        'Neck': 'Spine',
        'Head': 'Neck',
        'LeftShoulder': 'Spine',
        'LeftArm': 'LeftShoulder',
        'LeftForearm': 'LeftArm',
        'LeftHand': 'LeftForearm',
        'RightShoulder': 'Spine',
        'RightArm': 'RightShoulder',
        'RightForearm': 'RightArm',
        'RightHand': 'RightForearm',
    }
    
    def __init__(self):
        self.previous_positions = {}
        
    def landmarks_to_quaternions(
        self, 
        landmarks: np.ndarray,
        format: str = 'mediapipe'
    ) -> Dict[str, List[float]]:
        """
        Convert landmark coordinates to bone quaternions.
        
        Args:
            landmarks: Array of [x, y, z] coordinates
            format: 'mediapipe' or 'smplx'
            
        Returns:
            Dict mapping bone names to quaternion [x, y, z, w]
        """
        if format == 'mediapipe':
            return self._mediapipe_to_quaternions(landmarks)
        elif format == 'smplx':
            return self._smplx_to_quaternions(landmarks)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _mediapipe_to_quaternions(
        self, 
        landmarks: np.ndarray
    ) -> Dict[str, List[float]]:
        """Convert MediaPipe landmarks to quaternions."""
        result = {}
        
        # Define key joint positions from MediaPipe
        joints = {
            'right_shoulder': landmarks[12],
            'right_elbow': landmarks[14],
            'right_wrist': landmarks[16],
            'left_shoulder': landmarks[11],
            'left_elbow': landmarks[13],
            'left_wrist': landmarks[15],
            'nose': landmarks[0],
            'neck': (landmarks[11] + landmarks[12]) / 2,  # Midpoint of shoulders
        }
        
        # Calculate arm rotations
        # Right arm
        if 'right_shoulder' in joints and 'right_elbow' in joints:
            upper_arm_vec = joints['right_elbow'] - joints['right_shoulder']
            result['RightArm'] = self._vector_to_quaternion(
                upper_arm_vec, 
                reference=(0, -1, 0)  # T-pose reference
            )
            
        if 'right_elbow' in joints and 'right_wrist' in joints:
            forearm_vec = joints['right_wrist'] - joints['right_elbow']
            result['RightForearm'] = self._vector_to_quaternion(
                forearm_vec,
                reference=(0, -1, 0)
            )
            
        # Left arm
        if 'left_shoulder' in joints and 'left_elbow' in joints:
            upper_arm_vec = joints['left_elbow'] - joints['left_shoulder']
            result['LeftArm'] = self._vector_to_quaternion(
                upper_arm_vec,
                reference=(0, -1, 0)
            )
            
        if 'left_elbow' in joints and 'left_wrist' in joints:
            forearm_vec = joints['left_wrist'] - joints['left_elbow']
            result['LeftForearm'] = self._vector_to_quaternion(
                forearm_vec,
                reference=(0, -1, 0)
            )
            
        # Head (facing direction)
        if 'nose' in joints and 'neck' in joints:
            face_vec = joints['nose'] - joints['neck']
            result['Head'] = self._vector_to_quaternion(
                face_vec,
                reference=(0, 1, 0)
            )
            
        return result
    
    def _smplx_to_quaternions(self, landmarks: np.ndarray) -> Dict[str, List[float]]:
        """Convert SMPL-X output to quaternions."""
        # SMPL-X has more detailed hand joints
        # This is a simplified version
        result = {}
        
        # Body joints (first ~55 points are body)
        # Hands (next 55 each are hands)
        
        # Map SMPL-X joint indices to bones
        smplx_mapping = {
            2: 'Spine',
            3: 'Spine', 
            4: 'Neck',
            5: 'Head',
            17: 'LeftShoulder',
            18: 'LeftArm',
            19: 'LeftForearm',
            20: 'LeftHand',
            25: 'RightShoulder',
            26: 'RightArm',
            27: 'RightForearm',
            28: 'RightHand',
        }
        
        for idx, bone_name in smplx_mapping.items():
            if idx < len(landmarks):
                # Calculate rotation based on joint position
                # This would need actual implementation based on skeleton
                result[bone_name] = [0, 0, 0, 1]  # Identity quaternion
                
        return result
    
    def _vector_to_quaternion(
        self, 
        vector: np.ndarray, 
        reference: Tuple[float, float, float] = (0, -1, 0)
    ) -> List[float]:
        """
        Convert direction vector to quaternion rotation.
        
        Args:
            vector: Direction vector [x, y, z]
            reference: Reference direction in rest pose
            
        Returns:
            Quaternion [x, y, z, w]
        """
        # Normalize
        vector = vector / (np.linalg.norm(vector) + 1e-8)
        ref = np.array(reference) / (np.linalg.norm(reference) + 1e-8)
        
        # Calculate rotation axis
        axis = np.cross(ref, vector)
        axis_norm = np.linalg.norm(axis)
        
        if axis_norm < 1e-8:
            # Vectors are parallel
            return [0, 0, 0, 1]
        
        axis = axis / axis_norm
        
        # Calculate angle
        dot = np.dot(ref, vector)
        angle = np.arccos(np.clip(dot, -1, 1))
        
        # Convert axis-angle to quaternion
        x = axis[0] * np.sin(angle / 2)
        y = axis[1] * np.sin(angle / 2)
        z = axis[2] * np.sin(angle / 2)
        w = np.cos(angle / 2)
        
        return [float(x), float(y), float(z), float(w)]
    
    def smooth_keyframes(
        self, 
        frames: List[Dict[str, List[float]]],
        window_size: int = 5
    ) -> List[Dict[str, List[float]]]:
        """
        Apply Gaussian smoothing to keyframe sequence.
        
        Args:
            frames: List of bone rotation frames
            window_size: Smoothing window
            
        Returns:
            Smoothed keyframes
        """
        if len(frames) < window_size:
            return frames
            
        smoothed = []
        
        for i in range(len(frames)):
            start = max(0, i - window_size // 2)
            end = min(len(frames), i + window_size // 2)
            
            frame = {}
            for bone in frames[i].keys():
                values = np.array([f[bone] for f in frames[start:end] if bone in f])
                if len(values) > 0:
                    # Apply Gaussian-like weighting
                    weights = np.exp(-np.arange(len(values))**2 / (2 * (window_size/3)**2))
                    weights /= weights.sum()
                    smoothed_val = (values * weights.reshape(-1, 1)).sum(axis=0)
                    frame[bone] = smoothed_val.tolist()
                    
            smoothed.append(frame)
            
        return smoothed


class GlossProcessor:
    """
    Process English text to ASL Gloss notation.
    """
    
    # Common English to ASL Gloss mappings
    GLOSS_MAP = {
        'hello': 'HELLO',
        'hi': 'HELLO',
        'goodbye': 'BYE',
        'bye': 'BYE',
        'thank': 'THANK',
        'thanks': 'THANK',
        'you': 'YOU',
        'your': 'YOUR',
        'welcome': 'WELCOME',
        'sorry': 'SORRY',
        'yes': 'YES',
        'no': 'NO',
        'please': 'PLEASE',
        'help': 'HELP',
        'need': 'NEED',
        'want': 'WANT',
        'have': 'HAVE',
        'have': 'HAVE',
        'go': 'GO',
        'come': 'COME',
        'good': 'GOOD',
        'bad': 'BAD',
        'big': 'BIG',
        'small': 'SMALL',
        'love': 'LOVE',
        'like': 'LIKE',
        'eat': 'EAT',
        'drink': 'DRINK',
        'sleep': 'SLEEP',
        'work': 'WORK',
        'home': 'HOME',
        'name': 'NAME',
        'my': 'MY',
        'i': 'I',
        'we': 'WE',
        'they': 'THEY',
        'he': 'HE',
        'she': 'SHE',
        'it': 'IT',
        'contact': 'CONTACT',
        'us': 'US',
    }
    
    def text_to_gloss(self, text: str) -> List[str]:
        """
        Convert English text to ASL Gloss.
        
        Args:
            text: Input text
            
        Returns:
            List of gloss tokens
        """
        # Simple word-by-word mapping
        # Production would use proper NLP/parsing
        words = text.lower().replace('?', '').replace('!', '').replace('.', '').split()
        gloss = []
        
        for word in words:
            if word in self.GLOSS_MAP:
                gloss.append(self.GLOSS_MAP[word])
            else:
                # Unknown word - spell it out or use fallback
                gloss.append(word.upper())
                
        return gloss
    
    def gloss_to_sign_sequence(self, gloss: List[str]) -> List[dict]:
        """
        Convert gloss to sign sequence for animation.
        
        Args:
            gloss: List of gloss tokens
            
        Returns:
            List of sign configurations
        """
        sequence = []
        
        for token in gloss:
            sequence.append({
                'token': token,
                'type': 'sign',  # sign, fingerspell, pause
                'duration': 0.5,  # seconds
            })
            
        return sequence


# Example usage
if __name__ == "__main__":
    # Test coordinate converter
    converter = CoordinateConverter()
    
    # Mock MediaPipe landmarks (33 points, each [x, y, z])
    mock_landmarks = np.random.rand(33, 3)
    
    quaternions = converter.landmarks_to_quaternions(mock_landmarks, 'mediapipe')
    print("Generated quaternions:", json.dumps(quaternions, indent=2))
    
    # Test gloss processor
    processor = GlossProcessor()
    gloss = processor.text_to_gloss("Hello, how are you?")
    print("\nASL Gloss:", gloss)
