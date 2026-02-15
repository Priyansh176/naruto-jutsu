"""
Phase 2: Feature extraction from hand landmarks.
Extracts angles, distances, and finger states to build a feature vector for gesture classification.
Updated to support TWO HANDS for complete Naruto hand signs.
"""

import numpy as np
from typing import List, Tuple, Optional


class FeatureExtractor:
    """
    Extracts features from hand landmarks (21 points, 3D normalized coords).
    Supports both single-hand and two-hand gestures.
    Features include:
    - Finger states (5 binary: open/closed)
    - Finger angles (10: angle at each joint for 5 fingers)
    - Distances between key points (normalized)
    - Palm orientation features
    
    For two hands, features are concatenated: [left_hand_features, right_hand_features, inter_hand_features]
    """

    def __init__(self):
        # MediaPipe hand landmark indices
        self.WRIST = 0
        self.THUMB = [1, 2, 3, 4]
        self.INDEX = [5, 6, 7, 8]
        self.MIDDLE = [9, 10, 11, 12]
        self.RING = [13, 14, 15, 16]
        self.PINKY = [17, 18, 19, 20]
        self.FINGERS = [self.THUMB, self.INDEX, self.MIDDLE, self.RING, self.PINKY]

    def extract_two_hands(self, left_landmarks: Optional[List[Tuple[float, float, float]]], 
                         right_landmarks: Optional[List[Tuple[float, float, float]]]) -> np.ndarray:
        """
        Extract feature vector from TWO hands (left and right).
        
        Args:
            left_landmarks: List of 21 (x, y, z) tuples for left hand (None if not detected)
            right_landmarks: List of 21 (x, y, z) tuples for right hand (None if not detected)
        
        Returns:
            Feature vector as numpy array (66 features for single hand features + inter-hand features)
        """
        features = []
        
        # Extract features for left hand (or zeros if missing)
        if left_landmarks is not None and len(left_landmarks) == 21:
            left_features = self.extract(left_landmarks)
        else:
            left_features = np.zeros(33, dtype=np.float32)
        
        # Extract features for right hand (or zeros if missing)
        if right_landmarks is not None and len(right_landmarks) == 21:
            right_features = self.extract(right_landmarks)
        else:
            right_features = np.zeros(33, dtype=np.float32)
        
        features.extend(left_features)
        features.extend(right_features)
        
        # Inter-hand features (distance and relative position between hands)
        if left_landmarks is not None and right_landmarks is not None:
            left_array = np.array(left_landmarks)
            right_array = np.array(right_landmarks)
            
            # Distance between wrists
            wrist_dist = self._euclidean_distance(left_array[self.WRIST], right_array[self.WRIST])
            features.append(wrist_dist)
            
            # Distance between left index tip and right index tip
            index_dist = self._euclidean_distance(left_array[self.INDEX[-1]], right_array[self.INDEX[-1]])
            features.append(index_dist)
            
            # Relative position (x, y, z difference between wrists)
            wrist_diff = right_array[self.WRIST] - left_array[self.WRIST]
            features.extend(wrist_diff)  # 3 features (x, y, z)
        else:
            # No inter-hand features if either hand is missing
            features.extend([0.0] * 6)  # 6 inter-hand features
        
        return np.array(features, dtype=np.float32)

    def extract(self, landmarks: List[Tuple[float, float, float]]) -> np.ndarray:
        """
        Extract feature vector from 21 hand landmarks.
        
        Args:
            landmarks: List of 21 (x, y, z) tuples (normalized coordinates)
        
        Returns:
            Feature vector as numpy array (shape: 1D array of floats)
        """
        if len(landmarks) != 21:
            raise ValueError(f"Expected 21 landmarks, got {len(landmarks)}")
        
        landmarks_array = np.array(landmarks)
        features = []
        
        # 1. Finger curl/bend features (5 fingers × 2 angles = 10 features)
        for finger in self.FINGERS:
            features.extend(self._get_finger_angles(landmarks_array, finger))
        
        # 2. Finger tip distances from wrist (5 features)
        wrist = landmarks_array[self.WRIST]
        for finger in self.FINGERS:
            tip = landmarks_array[finger[-1]]
            dist = self._euclidean_distance(wrist, tip)
            features.append(dist)
        
        # 3. Finger spread angles (4 features: between adjacent fingers)
        finger_tips = [self.THUMB[-1], self.INDEX[-1], self.MIDDLE[-1], self.RING[-1], self.PINKY[-1]]
        for i in range(len(finger_tips) - 1):
            angle = self._angle_between_points(
                landmarks_array[finger_tips[i]],
                landmarks_array[self.WRIST],
                landmarks_array[finger_tips[i + 1]]
            )
            features.append(angle)
        
        # 4. Palm size (distance between key palm points, 3 features)
        features.append(self._euclidean_distance(landmarks_array[5], landmarks_array[17]))  # index to pinky base
        features.append(self._euclidean_distance(landmarks_array[0], landmarks_array[9]))   # wrist to middle base
        features.append(self._euclidean_distance(landmarks_array[5], landmarks_array[0]))   # index base to wrist
        
        # 5. Thumb-index distance (important for many gestures, 1 feature)
        features.append(self._euclidean_distance(
            landmarks_array[self.THUMB[-1]], 
            landmarks_array[self.INDEX[-1]]
        ))
        
        # 6. Finger orientation relative to palm (5 features: one per finger)
        palm_normal = self._get_palm_normal(landmarks_array)
        for finger in self.FINGERS:
            base = landmarks_array[finger[0]]
            tip = landmarks_array[finger[-1]]
            finger_vec = tip - base
            # Dot product indicates alignment with palm normal
            features.append(np.dot(finger_vec, palm_normal))
        
        # 7. Normalized z-coordinates of finger tips (depth, 5 features)
        for finger in self.FINGERS:
            features.append(landmarks_array[finger[-1]][2])
        
        return np.array(features, dtype=np.float32)
    
    def _get_finger_angles(self, landmarks: np.ndarray, finger_indices: List[int]) -> List[float]:
        """
        Calculate two bend angles for a finger:
        - Angle at MCP joint (base)
        - Angle at PIP joint (middle)
        """
        angles = []
        if len(finger_indices) >= 3:
            # MCP angle (base joint)
            angle1 = self._angle_between_points(
                landmarks[self.WRIST],
                landmarks[finger_indices[0]],
                landmarks[finger_indices[1]]
            )
            angles.append(angle1)
            
            # PIP angle (middle joint)
            angle2 = self._angle_between_points(
                landmarks[finger_indices[0]],
                landmarks[finger_indices[1]],
                landmarks[finger_indices[2]]
            )
            angles.append(angle2)
        else:
            angles = [0.0, 0.0]
        
        return angles
    
    def _angle_between_points(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """
        Calculate angle at p2 formed by p1-p2-p3 (in radians).
        """
        v1 = p1 - p2
        v2 = p3 - p2
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        
        return angle
    
    def _euclidean_distance(self, p1: np.ndarray, p2: np.ndarray) -> float:
        """Calculate Euclidean distance between two 3D points."""
        return np.linalg.norm(p1 - p2)
    
    def _get_palm_normal(self, landmarks: np.ndarray) -> np.ndarray:
        """
        Estimate palm normal vector using cross product of palm vectors.
        """
        # Use wrist, index base, and pinky base to define palm plane
        wrist = landmarks[self.WRIST]
        index_base = landmarks[self.INDEX[0]]
        pinky_base = landmarks[self.PINKY[0]]
        
        v1 = index_base - wrist
        v2 = pinky_base - wrist
        
        normal = np.cross(v1, v2)
        norm = np.linalg.norm(normal)
        if norm > 1e-8:
            normal = normal / norm
        
        return normal
    
    def get_feature_count(self) -> int:
        """Return the total number of features extracted for single hand."""
        # 10 (finger angles) + 5 (tip-wrist dist) + 4 (spread angles) + 3 (palm size) 
        # + 1 (thumb-index) + 5 (finger orientation) + 5 (z-coords) = 33 features
        return 33
    
    def get_two_hands_feature_count(self) -> int:
        """Return the total number of features extracted for two hands."""
        # 33 (left hand) + 33 (right hand) + 6 (inter-hand features) = 72 features
        return 72
