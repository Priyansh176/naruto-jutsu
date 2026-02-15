"""
Unit tests for FeatureExtractor
Tests feature extraction from hand landmarks for gesture recognition.
"""

import unittest
import sys
import numpy as np
from pathlib import Path

# Add project root to path for package imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from naruto_jutsu.src.feature_extractor import FeatureExtractor


class TestFeatureExtractor(unittest.TestCase):
    """Test suite for FeatureExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = FeatureExtractor()
        
        # Mock landmarks for a simple hand pose (21 landmarks, each with x, y, z)
        # Using normalized coordinates (0.0 to 1.0)
        self.mock_hand = [
            (0.5, 0.5, 0.0),   # 0: WRIST
            (0.48, 0.45, 0.0), # 1: THUMB_CMC
            (0.46, 0.40, 0.0), # 2: THUMB_MCP
            (0.44, 0.35, 0.0), # 3: THUMB_IP
            (0.42, 0.30, 0.0), # 4: THUMB_TIP
            (0.52, 0.40, 0.0), # 5: INDEX_FINGER_MCP
            (0.52, 0.30, 0.0), # 6: INDEX_FINGER_PIP
            (0.52, 0.25, 0.0), # 7: INDEX_FINGER_DIP
            (0.52, 0.20, 0.0), # 8: INDEX_FINGER_TIP
            (0.56, 0.42, 0.0), # 9: MIDDLE_FINGER_MCP
            (0.56, 0.30, 0.0), # 10: MIDDLE_FINGER_PIP
            (0.56, 0.25, 0.0), # 11: MIDDLE_FINGER_DIP
            (0.56, 0.20, 0.0), # 12: MIDDLE_FINGER_TIP
            (0.60, 0.44, 0.0), # 13: RING_FINGER_MCP
            (0.60, 0.35, 0.0), # 14: RING_FINGER_PIP
            (0.60, 0.30, 0.0), # 15: RING_FINGER_DIP
            (0.60, 0.25, 0.0), # 16: RING_FINGER_TIP
            (0.64, 0.46, 0.0), # 17: PINKY_MCP
            (0.64, 0.40, 0.0), # 18: PINKY_PIP
            (0.64, 0.35, 0.0), # 19: PINKY_DIP
            (0.64, 0.30, 0.0), # 20: PINKY_TIP
        ]
    
    def test_single_hand_feature_extraction(self):
        """Test feature extraction from a single hand"""
        features = self.extractor.extract(self.mock_hand)
        
        # Should return 33 features for single hand
        self.assertEqual(len(features), 33, "Single hand should produce 33 features")
        
        # All features should be numeric (including numpy types)
        for i, feature in enumerate(features):
            self.assertTrue(isinstance(feature, (int, float, np.float32, np.float64)), 
                          f"Feature {i} should be numeric")
    
    def test_two_hands_feature_extraction(self):
        """Test feature extraction from two hands"""
        # Use same mock hand for both left and right
        features = self.extractor.extract_two_hands(self.mock_hand, self.mock_hand)
        
        # Should return 72 features (33 + 33 + 6 inter-hand)
        self.assertEqual(len(features), 72, "Two hands should produce 72 features")
        
        # All features should be numeric (including numpy types)
        for i, feature in enumerate(features):
            self.assertTrue(isinstance(feature, (int, float, np.float32, np.float64)), 
                          f"Feature {i} should be numeric")
    
    def test_one_hand_missing(self):
        """Test feature extraction when one hand is missing"""
        # Left hand only
        features = self.extractor.extract_two_hands(self.mock_hand, None)
        self.assertEqual(len(features), 72, "Should return 72 features even with one hand")
        
        # Right hand only
        features = self.extractor.extract_two_hands(None, self.mock_hand)
        self.assertEqual(len(features), 72, "Should return 72 features even with one hand")
    
    def test_no_hands(self):
        """Test feature extraction when no hands are detected"""
        features = self.extractor.extract_two_hands(None, None)
        
        # Should return 72 zeros
        self.assertEqual(len(features), 72, "Should return 72 features even with no hands")
        self.assertTrue(all(f == 0 for f in features), "All features should be 0 when no hands")
    
    def test_invalid_landmarks(self):
        """Test handling of invalid landmark data"""
        # Too few landmarks
        invalid_hand = [(0.5, 0.5, 0.0)] * 10  # Only 10 landmarks instead of 21
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            features = self.extractor.extract(invalid_hand)
    
    def test_feature_ranges(self):
        """Test that features are within reasonable ranges"""
        features = self.extractor.extract(self.mock_hand)
        
        # Most features should be normalized (between -1 and 1 or 0 and 1)
        # This is a sanity check - exact ranges depend on feature design
        for i, feature in enumerate(features):
            self.assertTrue(-10 <= feature <= 10, 
                          f"Feature {i} = {feature} is outside reasonable range")


class TestFeatureNormalization(unittest.TestCase):
    """Test feature normalization and consistency"""
    
    def setUp(self):
        self.extractor = FeatureExtractor()
    
    def test_same_input_same_output(self):
        """Test that same input produces same output (deterministic)"""
        mock_hand = [(0.5, 0.5, 0.0)] * 21
        
        features1 = self.extractor.extract(mock_hand)
        features2 = self.extractor.extract(mock_hand)
        
        # Compare arrays properly
        self.assertTrue(np.array_equal(features1, features2), "Same input should produce same features")
    
    def test_mirrored_hands(self):
        """Test that left and right hands produce different features for same pose"""
        # This is a basic sanity check
        mock_hand = [(0.5, 0.5, 0.0)] * 21
        
        # Extract as left then right
        features_lr = self.extractor.extract_two_hands(mock_hand, None)
        features_rl = self.extractor.extract_two_hands(None, mock_hand)
        
        # They should be different (left vs right features are in different positions)
        self.assertFalse(np.array_equal(features_lr, features_rl), 
                          "Left and right hands should produce different feature vectors")


if __name__ == '__main__':
    unittest.main()
