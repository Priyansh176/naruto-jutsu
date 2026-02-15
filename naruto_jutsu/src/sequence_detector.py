"""
Sequence Detector for Naruto Jutsu Recognition System
Implements FSM-based detection of ordered gesture sequences.
"""

import json
import time
from typing import Optional, Dict, List, Tuple
from pathlib import Path


class SequenceDetector:
    """
    Finite State Machine for detecting ordered gesture sequences.
    
    Tracks gesture sequences in real-time with time windows and confidence validation.
    Emits jutsu detection events when complete sequences are recognized.
    """
    
    def __init__(self, jutsus_file: str = None):
        """
        Initialize the sequence detector.
        
        Args:
            jutsus_file: Path to jutsus.json configuration file
        """
        if jutsus_file is None:
            # Default to naruto_jutsu/jutsus.json
            jutsus_file = Path(__file__).parent.parent / "jutsus.json"
        
        self.jutsus_file = jutsus_file
        self.jutsus = []
        self.settings = {}
        self.load_jutsus()
        
        # FSM state
        self.current_sequence = []  # List of (gesture, timestamp) tuples
        self.sequence_start_time = None
        self.last_gesture = None
        self.last_gesture_time = None
        self.gesture_hold_start = None
        
        # Detection state
        self.active_jutsu = None  # Currently being tracked
        self.detected_jutsu = None  # Last completed jutsu
        self.detection_time = None
        
        # Targeted mode: track only specific jutsu
        self.target_jutsu = None  # If set, only detect this jutsu
        self.instant_detection = False  # If True, skip gesture hold time
        
    def load_jutsus(self):
        """Load jutsu definitions from JSON file."""
        try:
            with open(self.jutsus_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.jutsus = data.get('jutsus', [])
                self.settings = data.get('settings', {})
                
            print(f"Loaded {len(self.jutsus)} jutsus from {self.jutsus_file}")
            for jutsu in self.jutsus:
                seq_str = " → ".join(jutsu['sequence'])
                print(f"  - {jutsu['name']}: {seq_str}")
                
        except FileNotFoundError:
            print(f"ERROR: Jutsus file not found: {self.jutsus_file}")
            self.jutsus = []
            self.settings = {}
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in jutsus file: {e}")
            self.jutsus = []
            self.settings = {}
    
    def get_setting(self, key: str, default):
        """Get a setting value with fallback to default."""
        return self.settings.get(key, default)
    
    def reset(self):
        """Reset the FSM to initial state."""
        self.current_sequence = []
        self.sequence_start_time = None
        self.last_gesture = None
        self.last_gesture_time = None
        self.gesture_hold_start = None
        self.active_jutsu = None
    
    def set_target_jutsu(self, jutsu_name: str, instant_detection: bool = True):
        """Set a specific jutsu to track (targeted mode).
        
        Args:
            jutsu_name: Name of jutsu to track (e.g., "Fire Style: Fireball Jutsu")
            instant_detection: If True, register gestures instantly without hold time
        """
        # Find jutsu by name
        found = None
        for jutsu in self.jutsus:
            if jutsu['name'] == jutsu_name:
                found = jutsu
                break
        
        if found:
            self.target_jutsu = found
            self.instant_detection = instant_detection
            self.reset()
            print(f"[TARGET] Tracking: {jutsu_name}")
            print(f"[TARGET] Sequence: {' → '.join(found['sequence'])}")
            print(f"[TARGET] Instant detection: {instant_detection}")
        else:
            print(f"[ERROR] Jutsu not found: {jutsu_name}")
            self.target_jutsu = None
    
    def clear_target(self):
        """Clear targeted mode, return to detecting all jutsus."""
        self.target_jutsu = None
        self.instant_detection = False
        self.reset()
        print("[TARGET] Cleared - detecting all jutsus")
    
    def update(self, gesture: str, confidence: float) -> Optional[Dict]:
        """
        Update the sequence detector with a new gesture prediction.
        
        Args:
            gesture: Predicted gesture name
            confidence: Prediction confidence (0-1)
            
        Returns:
            Dict with jutsu info if a sequence was completed, None otherwise
        """
        current_time = time.time()
        
        # Get thresholds from settings
        conf_threshold = self.get_setting('confidence_threshold', 0.7)
        hold_time = 0.0 if self.instant_detection else self.get_setting('gesture_hold_time', 0.5)
        reset_on_invalid = self.get_setting('reset_on_invalid', True)
        
        # Ignore low-confidence predictions
        if confidence < conf_threshold:
            return None
        
        # Check if gesture changed
        if gesture != self.last_gesture:
            # New gesture detected
            self.last_gesture = gesture
            self.last_gesture_time = current_time
            self.gesture_hold_start = current_time
            return None
        
        # Same gesture - check if held long enough
        hold_duration = current_time - self.gesture_hold_start
        if hold_duration < hold_time:
            return None
        
        # Gesture confirmed (held long enough with high confidence)
        
        # Check if this is a duplicate (already added to sequence)
        if self.current_sequence and self.current_sequence[-1][0] == gesture:
            # Already tracking this gesture
            return None
        
        # Add gesture to sequence
        if not self.current_sequence:
            self.sequence_start_time = current_time
        
        self.current_sequence.append((gesture, current_time))
        print(f"[SEQ] Added: {gesture} (confidence: {confidence:.2f}, sequence: {[g for g, _ in self.current_sequence]})")
        
        # Check for matching jutsus
        matched_jutsu = self._check_sequence()
        
        if matched_jutsu:
            # Complete sequence detected!
            self.detected_jutsu = matched_jutsu
            self.detection_time = current_time
            print(f"[JUTSU DETECTED] {matched_jutsu['name']} ({matched_jutsu['japanese']})")
            
            # Reset for next sequence
            self.reset()
            
            return matched_jutsu
        
        # Check for timeout
        if self.sequence_start_time:
            elapsed = current_time - self.sequence_start_time
            max_window = self._get_max_time_window()
            
            if elapsed > max_window:
                print(f"[SEQ] Timeout: {elapsed:.1f}s > {max_window:.1f}s, resetting")
                self.reset()
        
        # Check for invalid sequence
        if reset_on_invalid and not self._is_valid_partial():
            print(f"[SEQ] Invalid sequence, resetting")
            self.reset()
        
        return None
    
    def _check_sequence(self) -> Optional[Dict]:
        """
        Check if current sequence matches any jutsu.
        
        Returns:
            Jutsu dict if complete match found, None otherwise
        """
        if not self.current_sequence:
            return None
        
        current_gestures = [g for g, _ in self.current_sequence]
        
        # If in targeted mode, only check target jutsu
        jutsus_to_check = [self.target_jutsu] if self.target_jutsu else self.jutsus
        
        for jutsu in jutsus_to_check:
            if current_gestures == jutsu['sequence']:
                # Check time window
                elapsed = time.time() - self.sequence_start_time
                if elapsed <= jutsu['time_window']:
                    return jutsu
                else:
                    print(f"[SEQ] Matched {jutsu['name']} but too slow: {elapsed:.1f}s > {jutsu['time_window']:.1f}s")
        
        return None
    
    def _is_valid_partial(self) -> bool:
        """
        Check if current sequence is a valid prefix of any jutsu.
        
        Returns:
            True if sequence could lead to a jutsu, False otherwise
        """
        if not self.current_sequence:
            return True
        
        current_gestures = [g for g, _ in self.current_sequence]
        
        # If in targeted mode, only check target jutsu
        jutsus_to_check = [self.target_jutsu] if self.target_jutsu else self.jutsus
        
        for jutsu in jutsus_to_check:
            seq = jutsu['sequence']
            if len(current_gestures) <= len(seq):
                # Check if current sequence matches the prefix
                if seq[:len(current_gestures)] == current_gestures:
                    return True
        
        return False
    
    def _get_max_time_window(self) -> float:
        """Get the maximum time window from all jutsus."""
        if not self.jutsus:
            return self.get_setting('default_time_window', 5.0)
        return max(j['time_window'] for j in self.jutsus)
    
    def get_current_progress(self) -> Dict:
        """
        Get current sequence progress for UI display.
        
        Returns:
            Dict with current sequence info
        """
        # If in targeted mode, return target jutsu info even when no sequence started
        if self.target_jutsu and not self.current_sequence:
            return {
                'active': True,
                'gestures': [],
                'elapsed': 0.0,
                'possible_jutsus': [{
                    'name': self.target_jutsu['name'],
                    'next_gesture': self.target_jutsu['sequence'][0],
                    'remaining': self.target_jutsu['sequence'],
                    'time_left': self.target_jutsu['time_window'],
                    'sequence': self.target_jutsu['sequence']
                }],
                'target_mode': True,
                'target_jutsu': self.target_jutsu
            }
        
        if not self.current_sequence:
            return {
                'active': False,
                'gestures': [],
                'elapsed': 0.0,
                'possible_jutsus': [],
                'target_mode': bool(self.target_jutsu),
                'target_jutsu': self.target_jutsu
            }
        
        current_gestures = [g for g, _ in self.current_sequence]
        elapsed = time.time() - self.sequence_start_time if self.sequence_start_time else 0.0
        
        # Find possible matching jutsus
        possible = []
        for jutsu in self.jutsus:
            seq = jutsu['sequence']
            if len(current_gestures) < len(seq):
                if seq[:len(current_gestures)] == current_gestures:
                    remaining = seq[len(current_gestures):]
                    possible.append({
                        'name': jutsu['name'],
                        'next_gesture': remaining[0] if remaining else None,
                        'remaining': remaining,
                        'time_left': jutsu['time_window'] - elapsed
                    })
        
        return {
            'active': True,
            'gestures': current_gestures,
            'elapsed': elapsed,
            'possible_jutsus': possible,
            'target_mode': bool(self.target_jutsu),
            'target_jutsu': self.target_jutsu
        }
    
    def get_last_detection(self) -> Optional[Tuple[Dict, float]]:
        """
        Get the last detected jutsu and when it was detected.
        
        Returns:
            Tuple of (jutsu_dict, timestamp) or None
        """
        if self.detected_jutsu and self.detection_time:
            return (self.detected_jutsu, self.detection_time)
        return None
    
    def clear_last_detection(self):
        """Clear the last detection (after displaying it)."""
        self.detected_jutsu = None
        self.detection_time = None


if __name__ == "__main__":
    # Test the sequence detector
    print("=== Sequence Detector Test ===\n")
    
    detector = SequenceDetector()
    
    # Test Fireball sequence: Snake → Ram → Tiger
    print("\n--- Testing Fireball Jutsu ---")
    print("Expected: Snake → Ram → Tiger\n")
    
    detector.update("Snake", 0.9)
    time.sleep(0.6)  # Hold gesture
    result = detector.update("Snake", 0.9)
    
    time.sleep(0.5)
    detector.update("Ram", 0.85)
    time.sleep(0.6)
    result = detector.update("Ram", 0.85)
    
    time.sleep(0.5)
    detector.update("Tiger", 0.92)
    time.sleep(0.6)
    result = detector.update("Tiger", 0.92)
    
    if result:
        print(f"\n✓ DETECTED: {result['name']}")
        print(f"  Japanese: {result['japanese']}")
        print(f"  Effects: {result['effects']}")
    else:
        print("\n✗ No jutsu detected")
    
    # Test invalid sequence
    print("\n--- Testing Invalid Sequence ---")
    print("Trying: Dog → Bird → Tiger (invalid)\n")
    
    detector.reset()
    detector.update("Dog", 0.9)
    time.sleep(0.6)
    detector.update("Dog", 0.9)
    
    time.sleep(0.5)
    detector.update("Bird", 0.85)
    time.sleep(0.6)
    result = detector.update("Bird", 0.85)
    
    progress = detector.get_current_progress()
    print(f"\nProgress: {progress}")
    
    if progress['possible_jutsus']:
        print("\nPossible completions:")
        for p in progress['possible_jutsus']:
            print(f"  - {p['name']}: next = {p['next_gesture']}")
