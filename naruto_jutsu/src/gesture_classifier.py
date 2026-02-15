"""
Phase 2: Gesture classifier module.
Wraps a trained ML model (Random Forest) to predict gesture labels from hand features.
"""

import pickle
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import time


class GestureClassifier:
    """
    Gesture classifier that loads a trained model and predicts gesture labels.
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize classifier with a trained model.
        
        Args:
            model_path: Path to saved model file (.pkl). If None, looks for default model.
        """
        self.model = None
        self.label_encoder = None
        self.gesture_names = None
        self.model_loaded = False
        
        if model_path is None:
            # Look for default model in models/ directory
            models_dir = Path(__file__).resolve().parent.parent / "models"
            if models_dir.exists():
                model_files = list(models_dir.glob("gesture_classifier_*.pkl"))
                if model_files:
                    model_path = sorted(model_files)[-1]  # Use most recent
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def load_model(self, model_path: Path):
        """Load a trained model from disk."""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.gesture_names = model_data['gesture_names']
            self.model_loaded = True
            
            print(f"✓ Model loaded from: {model_path}")
            print(f"  Gestures: {', '.join(self.gesture_names)}")
        
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            self.model_loaded = False
    
    def predict(self, features: np.ndarray, return_probabilities: bool = False) -> Tuple[str, float, Optional[dict]]:
        """
        Predict gesture from feature vector.
        
        Args:
            features: Feature vector (1D array, size 33)
            return_probabilities: If True, return probability distribution over all gestures
        
        Returns:
            Tuple of (predicted_gesture, confidence, probabilities_dict or None)
        """
        if not self.model_loaded:
            return "No Model", 0.0, None
        
        try:
            # Reshape features for sklearn (expects 2D array)
            features_2d = features.reshape(1, -1)
            
            # Get prediction and probabilities
            prediction = self.model.predict(features_2d)[0]
            probabilities = self.model.predict_proba(features_2d)[0]
            
            # Decode label
            gesture_name = self.label_encoder.inverse_transform([prediction])[0]
            confidence = probabilities[prediction]
            
            prob_dict = None
            if return_probabilities:
                prob_dict = {
                    self.label_encoder.inverse_transform([i])[0]: prob
                    for i, prob in enumerate(probabilities)
                }
            
            return gesture_name, confidence, prob_dict
        
        except Exception as e:
            print(f"Prediction error: {e}")
            return "Error", 0.0, None
    
    def predict_with_timing(self, features: np.ndarray) -> Tuple[str, float, float]:
        """
        Predict gesture and measure latency.
        
        Returns:
            Tuple of (predicted_gesture, confidence, latency_ms)
        """
        start_time = time.perf_counter()
        gesture, confidence, _ = self.predict(features)
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        return gesture, confidence, latency_ms
    
    def is_loaded(self) -> bool:
        """Check if model is loaded and ready."""
        return self.model_loaded
    
    def get_gesture_names(self) -> list:
        """Get list of gesture names the model can recognize."""
        return self.gesture_names if self.gesture_names else []
