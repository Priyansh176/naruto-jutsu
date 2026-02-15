"""
Performance Validation Script for Naruto Jutsu Recognition System

Tests system performance against target metrics:
- FPS: >= 15 FPS
- Latency: < 300ms
- CPU usage: Reasonable levels
"""

import cv2
import time
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hand_tracker import HandTracker
from feature_extractor import FeatureExtractor
from gesture_classifier import GestureClassifier


class PerformanceValidator:
    """Validates system performance metrics"""
    
    def __init__(self, camera_id=0, test_duration=30):
        """
        Initialize performance validator.
        
        Args:
            camera_id: Camera index to use
            test_duration: How long to run test (seconds)
        """
        self.camera_id = camera_id
        self.test_duration = test_duration
        
        # Performance metrics
        self.fps_samples = []
        self.latency_samples = []
        
        # Initialize components
        self.tracker = HandTracker(max_num_hands=2)
        self.feature_extractor = FeatureExtractor()
        self.classifier = GestureClassifier()
        
        print("=" * 70)
        print("Naruto Jutsu Recognition System - Performance Validation")
        print("=" * 70)
        print()
        print(f"Test Configuration:")
        print(f"  Camera ID: {camera_id}")
        print(f"  Test Duration: {test_duration}s")
        print(f"  Classifier Loaded: {self.classifier.is_loaded()}")
        print()
    
    def test_hand_tracking_fps(self):
        """Test hand tracking FPS (baseline performance)"""
        print("-" * 70)
        print("Test 1: Hand Tracking FPS")
        print("-" * 70)
        print("Testing hand tracking performance without gesture recognition...")
        print()
        
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print("❌ ERROR: Could not open camera")
            return False
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        fps_samples = []
        start_time = time.time()
        frame_count = 0
        
        window_name = "Performance Test - Hand Tracking"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
        
        print("Press 'q' to skip to next test")
        
        while True:
            elapsed = time.time() - start_time
            if elapsed >= self.test_duration:
                break
            
            ok, frame = cap.read()
            if not ok:
                break
            
            frame = cv2.flip(frame, 1)
            
            # Process frame
            hand_results = self.tracker.process(frame)
            self.tracker.draw_landmarks(frame, hand_results)
            fps = self.tracker.update_fps()
            
            fps_samples.append(fps)
            frame_count += 1
            
            # Display
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv2.putText(frame, f"Time: {elapsed:.1f}s / {self.test_duration}s", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Hand Tracking Test", (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            cv2.imshow(window_name, frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Results
        avg_fps = np.mean(fps_samples) if fps_samples else 0
        min_fps = np.min(fps_samples) if fps_samples else 0
        max_fps = np.max(fps_samples) if fps_samples else 0
        
        print(f"Frames processed: {frame_count}")
        print(f"Average FPS: {avg_fps:.2f}")
        print(f"Min FPS: {min_fps:.2f}")
        print(f"Max FPS: {max_fps:.2f}")
        
        # Check against target
        target_fps = 15.0
        passed = avg_fps >= target_fps
        
        if passed:
            print(f"✅ PASS: Average FPS ({avg_fps:.2f}) meets target (>= {target_fps})")
        else:
            print(f"❌ FAIL: Average FPS ({avg_fps:.2f}) below target (>= {target_fps})")
        
        print()
        return passed
    
    def test_gesture_recognition_performance(self):
        """Test full pipeline (tracking + recognition) performance"""
        print("-" * 70)
        print("Test 2: Full Pipeline Performance (Tracking + Recognition)")
        print("-" * 70)
        
        if not self.classifier.is_loaded():
            print("⚠ WARNING: Classifier not loaded. Skipping gesture recognition test.")
            print()
            return True
        
        print("Testing complete system with gesture recognition...")
        print()
        
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print("❌ ERROR: Could not open camera")
            return False
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        fps_samples = []
        latency_samples = []
        start_time = time.time()
        frame_count = 0
        gesture_count = 0
        
        window_name = "Performance Test - Full Pipeline"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
        
        print("Press 'q' to skip to next test")
        
        while True:
            elapsed = time.time() - start_time
            if elapsed >= self.test_duration:
                break
            
            ok, frame = cap.read()
            if not ok:
                break
            
            frame = cv2.flip(frame, 1)
            
            # Process hand tracking
            hand_results = self.tracker.process(frame)
            self.tracker.draw_landmarks(frame, hand_results)
            fps = self.tracker.update_fps()
            
            fps_samples.append(fps)
            frame_count += 1
            
            # Gesture recognition (if hands detected)
            gesture_text = "No hands"
            latency = 0
            
            if hand_results and len(hand_results) > 0:
                try:
                    # Extract hands
                    left_hand = None
                    right_hand = None
                    
                    for hand in hand_results:
                        if hand.handedness == "Left":
                            left_hand = hand.landmarks
                        elif hand.handedness == "Right":
                            right_hand = hand.landmarks
                    
                    # Extract features
                    features = self.feature_extractor.extract_two_hands(left_hand, right_hand)
                    
                    # Predict with timing
                    gesture, confidence, latency = self.classifier.predict_with_timing(features)
                    
                    latency_samples.append(latency)
                    gesture_count += 1
                    gesture_text = f"{gesture} ({confidence*100:.0f}%)"
                
                except Exception as e:
                    gesture_text = f"Error: {str(e)[:20]}"
            
            # Display
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv2.putText(frame, f"Gesture: {gesture_text}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            if latency > 0:
                latency_color = (0, 255, 0) if latency < 300 else (0, 0, 255)
                cv2.putText(frame, f"Latency: {latency:.1f}ms", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, latency_color, 2)
            cv2.putText(frame, f"Time: {elapsed:.1f}s / {self.test_duration}s", (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Full Pipeline Test", (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            cv2.imshow(window_name, frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Results
        avg_fps = np.mean(fps_samples) if fps_samples else 0
        min_fps = np.min(fps_samples) if fps_samples else 0
        avg_latency = np.mean(latency_samples) if latency_samples else 0
        max_latency = np.max(latency_samples) if latency_samples else 0
        
        print(f"Frames processed: {frame_count}")
        print(f"Gestures recognized: {gesture_count}")
        print(f"Average FPS: {avg_fps:.2f}")
        print(f"Min FPS: {min_fps:.2f}")
        print(f"Average Latency: {avg_latency:.2f}ms")
        print(f"Max Latency: {max_latency:.2f}ms")
        
        # Check against targets
        target_fps = 15.0
        target_latency = 300.0
        
        fps_passed = avg_fps >= target_fps
        latency_passed = avg_latency < target_latency
        
        if fps_passed:
            print(f"✅ PASS: FPS ({avg_fps:.2f}) meets target (>= {target_fps})")
        else:
            print(f"❌ FAIL: FPS ({avg_fps:.2f}) below target (>= {target_fps})")
        
        if latency_passed:
            print(f"✅ PASS: Latency ({avg_latency:.2f}ms) meets target (< {target_latency}ms)")
        else:
            print(f"❌ FAIL: Latency ({avg_latency:.2f}ms) exceeds target (< {target_latency}ms)")
        
        print()
        return fps_passed and latency_passed
    
    def run_all_tests(self):
        """Run all performance tests"""
        print()
        print("Starting performance validation...")
        print()
        
        results = []
        
        # Test 1: Hand tracking FPS
        results.append(("Hand Tracking FPS", self.test_hand_tracking_fps()))
        
        # Test 2: Full pipeline
        results.append(("Full Pipeline Performance", self.test_gesture_recognition_performance()))
        
        # Final summary
        print("=" * 70)
        print("Final Results")
        print("=" * 70)
        
        all_passed = True
        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name}")
            if not passed:
                all_passed = False
        
        print("=" * 70)
        print()
        
        if all_passed:
            print("🎉 All performance tests passed!")
            print()
            return 0
        else:
            print("⚠ Some performance tests failed. Review results above.")
            print()
            return 1


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Performance validation for Jutsu Recognition System')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    parser.add_argument('--duration', type=int, default=30, help='Test duration in seconds (default: 30)')
    
    args = parser.parse_args()
    
    validator = PerformanceValidator(camera_id=args.camera, test_duration=args.duration)
    exit_code = validator.run_all_tests()
    
    sys.exit(exit_code)
