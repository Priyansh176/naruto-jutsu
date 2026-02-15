"""
Phase 2: Data capture tool for gesture training data.
Records hand landmarks and saves to CSV with gesture labels.
Updated for TWO HANDS and reference image overlays.
Features: Manual and AUTOMATIC capture modes with countdown.
Target: ≥ 200 samples per gesture.
"""

import cv2
import csv
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Allow running from project root or from naruto_jutsu/src
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hand_tracker import HandTracker, HandResult
from feature_extractor import FeatureExtractor


class DataCaptureApp:
    """
    Interactive data capture tool for collecting gesture training samples with BOTH HANDS.
    """
    
    def __init__(self, camera_id: int = 0, window_width: int = 1280, window_height: int = 720):
        self.camera_id = camera_id
        self.window_width = window_width
        self.window_height = window_height
        # TWO hands with lower confidence thresholds for better detection
        self.tracker = HandTracker(
            max_num_hands=2,
            min_detection_confidence=0.3,  # Lower for better two-hand detection
            min_tracking_confidence=0.3,
            model_complexity=1  # Full model for better accuracy
        )
        self.feature_extractor = FeatureExtractor()
        
        # Load gesture definitions
        gestures_file = Path(__file__).resolve().parent.parent / "gestures.json"
        with open(gestures_file, 'r') as f:
            data = json.load(f)
            self.gestures = data['gestures']
        
        self.current_gesture_idx = 0
        self.current_gesture_name = self.gestures[0]['name']
        self.samples_collected = {g['name']: 0 for g in self.gestures}
        
        # Auto-capture state
        self.auto_mode = False
        self.auto_interval = 0.2  # seconds between captures (faster: 5 samples/sec)
        self.countdown_duration = 3  # seconds for countdown
        self.countdown_start_time = None
        self.last_capture_time = None
        self.is_countdown_active = False
        
        # Load reference images
        self.images_dir = Path(__file__).resolve().parent.parent / "images"
        self.reference_images = {}
        self.load_reference_images()
        
        # CSV output
        self.data_dir = Path(__file__).resolve().parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file = self.data_dir / f"gesture_data_2hands_{timestamp}.csv"
        self.init_csv()
        
        print("=== Naruto Jutsu Data Capture Tool (TWO HANDS) ===")
        print("Controls:")
        print("  SPACE: Capture sample (manual mode)")
        print("  A: Start AUTO-CAPTURE mode (0.2s interval after 3s countdown)")
        print("  S: Stop AUTO-CAPTURE mode")
        print("  N: Next gesture")
        print("  P: Previous gesture")
        print("  Q: Quit and save")
        print("\nAUTO-CAPTURE: Press A, get ready during countdown, samples auto-collected!")
        print("Fast mode: ~5 samples/second - collect 200 samples in ~40 seconds!")
        print("Target: 200+ samples per gesture for good accuracy")
        print(f"Window size: {window_width}x{window_height}")
        print(f"\nData will be saved to: {self.csv_file}")
        print("=" * 60)
    
    def load_reference_images(self):
        """Load reference images for each gesture."""
        if not self.images_dir.exists():
            print(f"⚠ Images directory not found: {self.images_dir}")
            print("  Reference images will not be displayed.")
            return
        
        for gesture in self.gestures:
            if 'image' in gesture:
                image_path = self.images_dir / gesture['image']
                if image_path.exists():
                    img = cv2.imread(str(image_path))
                    if img is not None:
                        # Resize to a standard size for overlay (e.g., 300x300)
                        img_resized = cv2.resize(img, (300, 300))
                        self.reference_images[gesture['name']] = img_resized
                    else:
                        print(f"⚠ Could not load image: {image_path}")
                else:
                    print(f"⚠ Image not found: {image_path}")
        
        print(f"✓ Loaded {len(self.reference_images)}/{len(self.gestures)} reference images")
    
    def init_csv(self):
        """Initialize CSV file with header."""
        feature_count = self.feature_extractor.get_two_hands_feature_count()
        header = [f"feature_{i}" for i in range(feature_count)] + ["gesture_label", "timestamp"]
        
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    
    def save_sample(self, hand_results: List[HandResult]):
        """Extract features from BOTH hands and save to CSV."""
        try:
            # Separate left and right hands
            left_hand = None
            right_hand = None
            
            for hand in hand_results:
                if hand.handedness == "Left":
                    left_hand = hand.landmarks
                elif hand.handedness == "Right":
                    right_hand = hand.landmarks
            
            # Extract two-hand features
            features = self.feature_extractor.extract_two_hands(left_hand, right_hand)
            timestamp = datetime.now().isoformat()
            
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                row = list(features) + [self.current_gesture_name, timestamp]
                writer.writerow(row)
            
            self.samples_collected[self.current_gesture_name] += 1
            print(f"✓ Captured {self.current_gesture_name} "
                  f"(Total: {self.samples_collected[self.current_gesture_name]})")
        
        except Exception as e:
            print(f"Error saving sample: {e}")
    
    def next_gesture(self):
        """Switch to next gesture in list."""
        self.current_gesture_idx = (self.current_gesture_idx + 1) % len(self.gestures)
        self.current_gesture_name = self.gestures[self.current_gesture_idx]['name']
        print(f"\n→ Switched to: {self.current_gesture_name}")
        print(f"  {self.gestures[self.current_gesture_idx]['description']}")
    
    def prev_gesture(self):
        """Switch to previous gesture in list."""
        self.current_gesture_idx = (self.current_gesture_idx - 1) % len(self.gestures)
        self.current_gesture_name = self.gestures[self.current_gesture_idx]['name']
        print(f"\n← Switched to: {self.current_gesture_name}")
        print(f"  {self.gestures[self.current_gesture_idx]['description']}")
    
    def start_auto_capture(self):
        """Start auto-capture mode with countdown."""
        if not self.auto_mode:
            self.is_countdown_active = True
            self.countdown_start_time = time.time()
            print(f"\n🔴 AUTO-CAPTURE starting in {self.countdown_duration} seconds...")
            print(f"   Get ready to hold the '{self.current_gesture_name}' sign!")
    
    def stop_auto_capture(self):
        """Stop auto-capture mode."""
        if self.auto_mode or self.is_countdown_active:
            self.auto_mode = False
            self.is_countdown_active = False
            self.countdown_start_time = None
            self.last_capture_time = None
            print("\n⏸ AUTO-CAPTURE stopped")
    
    def update_auto_capture(self, hand_results: List[HandResult]) -> bool:
        """
        Update auto-capture state and capture if needed.
        Returns True if a sample was captured.
        """
        current_time = time.time()
        
        # Handle countdown
        if self.is_countdown_active:
            elapsed = current_time - self.countdown_start_time
            if elapsed >= self.countdown_duration:
                # Countdown finished, start auto-capture
                self.is_countdown_active = False
                self.auto_mode = True
                self.last_capture_time = current_time
                print(f"\n✅ AUTO-CAPTURE active! Capturing every {self.auto_interval}s")
                print("   Press S to stop")
                return False
            return False
        
        # Handle auto-capture
        if self.auto_mode:
            if self.last_capture_time is None:
                self.last_capture_time = current_time
            
            elapsed = current_time - self.last_capture_time
            if elapsed >= self.auto_interval:
                if len(hand_results) > 0:
                    self.save_sample(hand_results)
                    self.last_capture_time = current_time
                    return True
                else:
                    # Skip if no hands detected, but don't reset timer
                    self.last_capture_time = current_time
        
        return False
    
    def get_countdown_remaining(self) -> Optional[float]:
        """Get remaining countdown time in seconds, or None if not counting down."""
        if not self.is_countdown_active:
            return None
        elapsed = time.time() - self.countdown_start_time
        remaining = self.countdown_duration - elapsed
        return max(0, remaining)
    
    def draw_ui(self, frame, hand_results: List[HandResult], fps: float):
        """Draw UI overlay showing current gesture, reference image, and instructions."""
        h, w = frame.shape[:2]
        
        # Reference image overlay (top-right corner)
        gesture = self.gestures[self.current_gesture_idx]
        if gesture['name'] in self.reference_images:
            ref_img = self.reference_images[gesture['name']]
            ref_h, ref_w = ref_img.shape[:2]
            
            # Position in top-right corner with padding
            x_offset = w - ref_w - 20
            y_offset = 20
            
            # Add semi-transparent background
            overlay = frame.copy()
            cv2.rectangle(overlay, (x_offset - 10, y_offset - 10), 
                         (x_offset + ref_w + 10, y_offset + ref_h + 10), 
                         (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # Overlay the reference image
            frame[y_offset:y_offset+ref_h, x_offset:x_offset+ref_w] = ref_img
            
            # Border around reference image
            cv2.rectangle(frame, (x_offset, y_offset), 
                         (x_offset + ref_w, y_offset + ref_h), 
                         (0, 255, 0), 3)
            
            # Label above reference image
            cv2.putText(frame, "Reference:", (x_offset, y_offset - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # FPS (top-left)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Current gesture (large, centered at top)
        gesture_text = f"Gesture: {gesture['name']}"
        text_size = cv2.getTextSize(gesture_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        text_x = (w - text_size[0]) // 2
        cv2.putText(frame, gesture_text, (text_x, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        # Description
        desc_text = gesture['description']
        desc_size = cv2.getTextSize(desc_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]
        desc_x = (w - desc_size[0]) // 2
        cv2.putText(frame, desc_text, (desc_x, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        # Hand detection status with count
        left_detected = any(h.handedness == "Left" for h in hand_results)
        right_detected = any(h.handedness == "Right" for h in hand_results)
        
        left_status = "Left: ✓" if left_detected else "Left: ✗"
        right_status = "Right: ✓" if right_detected else "Right: ✗"
        
        left_color = (0, 255, 0) if left_detected else (0, 0, 255)
        right_color = (0, 255, 0) if right_detected else (0, 0, 255)
        
        cv2.putText(frame, left_status, (10, h - 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, left_color, 2)
        cv2.putText(frame, right_status, (200, h - 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, right_color, 2)
        
        # Sample count
        count = self.samples_collected[gesture['name']]
        count_color = (0, 255, 0) if count >= 200 else (0, 165, 255)
        cv2.putText(frame, f"Samples: {count} / 200+", (10, h - 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, count_color, 2)
        
        # Auto-capture status / Countdown display (center, large)
        countdown = self.get_countdown_remaining()
        if countdown is not None:
            # Show countdown
            countdown_text = f"{int(countdown) + 1}" if countdown > 0 else "GO!"
            text_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 8.0, 15)[0]
            text_x = (w - text_size[0]) // 2
            text_y = h // 2 + 50
            
            # Pulsing effect based on countdown
            pulse = int(30 * (1 + 0.5 * (countdown % 1)))
            
            # Background
            cv2.rectangle(frame, 
                         (text_x - 50, text_y - text_size[1] - 50),
                         (text_x + text_size[0] + 50, text_y + 50),
                         (0, 0, 0), -1)
            
            # Countdown text
            color = (0, 255, 255) if countdown > 0 else (0, 255, 0)
            cv2.putText(frame, countdown_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 8.0, color, 15)
            
            # Label
            label = "Get Ready!" if countdown > 0 else "Capturing!"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
            label_x = (w - label_size[0]) // 2
            cv2.putText(frame, label, (label_x, text_y + 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)
        
        elif self.auto_mode:
            # Show auto-capture active indicator
            mode_text = "AUTO-CAPTURE ON"
            cv2.putText(frame, mode_text, (w - 280, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Show next capture timer
            if self.last_capture_time:
                time_since = time.time() - self.last_capture_time
                time_until = max(0, self.auto_interval - time_since)
                timer_text = f"Next: {time_until:.1f}s"
                cv2.putText(frame, timer_text, (w - 280, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Controls
        controls = "SPACE: Capture | A: Auto | S: Stop | N: Next | P: Prev | Q: Quit"
        cv2.putText(frame, controls, (10, h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 2)
        
        # Progress bar (total samples across all gestures)
        total_samples = sum(self.samples_collected.values())
        target_total = len(self.gestures) * 200
        progress = min(1.0, total_samples / target_total)
        bar_width = w - 40
        bar_height = 25
        bar_x, bar_y = 20, h - 50
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                      (100, 100, 100), 2)
        cv2.rectangle(frame, (bar_x, bar_y), 
                      (bar_x + int(bar_width * progress), bar_y + bar_height), 
                      (0, 255, 0), -1)
        cv2.putText(frame, f"Total: {total_samples} / {target_total}", 
                    (bar_x, bar_y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def run(self):
        """Main capture loop with larger window."""
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print("Could not open webcam. Try another camera_id.")
            return
        
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.window_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.window_height)
        
        # Create named window and resize
        window_name = "Data Capture - Naruto Jutsu (TWO HANDS)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.window_width, self.window_height)
        
        # Show initial gesture
        print(f"\nStarting with: {self.current_gesture_name}")
        print(f"  {self.gestures[self.current_gesture_idx]['description']}")
        print("\n⚠ Important: Make sure BOTH hands are visible for best results!")
        
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                
                # Resize frame to target size if needed
                if frame.shape[1] != self.window_width or frame.shape[0] != self.window_height:
                    frame = cv2.resize(frame, (self.window_width, self.window_height))
                
                frame = cv2.flip(frame, 1)  # Mirror for natural UX
                
                # Process hand tracking (2 hands)
                hand_results = self.tracker.process(frame)
                self.tracker.draw_landmarks(frame, hand_results)
                fps = self.tracker.update_fps()
                
                # Update auto-capture (captures automatically if active)
                self.update_auto_capture(hand_results)
                
                # Draw UI
                self.draw_ui(frame, hand_results, fps)
                
                # Show frame
                cv2.imshow(window_name, frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord(' '):  # Space bar to capture (manual mode)
                    if not self.auto_mode and not self.is_countdown_active:
                        if len(hand_results) > 0:
                            self.save_sample(hand_results)
                        else:
                            print("⚠ No hands detected. Cannot capture sample.")
                elif key == ord('a'):  # Start auto-capture
                    self.start_auto_capture()
                elif key == ord('s'):  # Stop auto-capture
                    self.stop_auto_capture()
                elif key == ord('n'):
                    if not self.auto_mode and not self.is_countdown_active:
                        self.next_gesture()
                    else:
                        print("⚠ Cannot switch gesture during auto-capture. Press S to stop first.")
                elif key == ord('p'):
                    if not self.auto_mode and not self.is_countdown_active:
                        self.prev_gesture()
                    else:
                        print("⚠ Cannot switch gesture during auto-capture. Press S to stop first.")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.tracker.close()
            
            # Print summary
            print("\n" + "=" * 60)
            print("Data capture complete!")
            print(f"Data saved to: {self.csv_file}")
            print(f"\nFeature count per sample: {self.feature_extractor.get_two_hands_feature_count()}")
            print("\nSamples collected per gesture:")
            for gesture_name, count in self.samples_collected.items():
                status = "✓" if count >= 200 else "⚠"
                print(f"  {status} {gesture_name}: {count}")
            print("=" * 60)


def main():
    """Entry point for data capture tool."""
    # Larger window for better visibility
    app = DataCaptureApp(camera_id=0, window_width=1280, window_height=720)
    app.run()


if __name__ == "__main__":
    main()
