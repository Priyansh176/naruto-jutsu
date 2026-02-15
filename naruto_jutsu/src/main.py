"""
Naruto Jutsu Recognition System – entry point.
Phase 2: Hand tracking + real-time gesture recognition with TWO HANDS.
Press 'q' to quit, '1' for Phase 1 mode (tracking only), '2' for Phase 2 mode (recognition).
"""

import cv2
import sys
from pathlib import Path
import time

# Allow running from project root or from naruto_jutsu
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hand_tracker import HandTracker, HandResult, FingerState
from feature_extractor import FeatureExtractor
from gesture_classifier import GestureClassifier


def draw_ui_overlay(frame, hand_results: list, fps: float, mode: str = "phase1", 
                    gesture_info: dict = None) -> None:
    """
    Draw FPS and finger state text on frame.
    
    Args:
        frame: Video frame to draw on
        hand_results: List of HandResult objects
        fps: Current FPS value
        mode: "phase1" (tracking only) or "phase2" (gesture recognition)
        gesture_info: Dict with 'gesture', 'confidence', 'latency_ms' for phase2
    """
    h, w = frame.shape[:2]
    
    # FPS (top-left)
    cv2.putText(
        frame, f"FPS: {fps:.1f}",
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2
    )
    # Target: >= 15 FPS
    color_fps = (0, 255, 0) if fps >= 15 else (0, 0, 255)
    cv2.putText(frame, "Target: 15 FPS", (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_fps, 1)

    # Mode indicator
    mode_text = "Mode: Phase 1 (Tracking)" if mode == "phase1" else "Mode: Phase 2 (Recognition)"
    cv2.putText(frame, mode_text, (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)
    
    if mode == "phase2" and gesture_info:
        # Gesture recognition display (centered, large)
        gesture = gesture_info.get('gesture', 'Unknown')
        confidence = gesture_info.get('confidence', 0.0)
        latency_ms = gesture_info.get('latency_ms', 0.0)
        
        # Large gesture name (centered)
        gesture_text = f"{gesture}"
        text_size = cv2.getTextSize(gesture_text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 3)[0]
        text_x = (w - text_size[0]) // 2
        text_y = h // 2
        
        # Background rectangle for better visibility
        padding = 20
        cv2.rectangle(frame, 
                      (text_x - padding, text_y - text_size[1] - padding),
                      (text_x + text_size[0] + padding, text_y + padding),
                      (0, 0, 0), -1)
        cv2.rectangle(frame,
                      (text_x - padding, text_y - text_size[1] - padding),
                      (text_x + text_size[0] + padding, text_y + padding),
                      (0, 255, 0), 2)
        
        cv2.putText(frame, gesture_text, (text_x, text_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 3)
        
        # Confidence bar below gesture name
        conf_text = f"Confidence: {confidence * 100:.1f}%"
        conf_size = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        conf_x = (w - conf_size[0]) // 2
        conf_y = text_y + 40
        
        color_conf = (0, 255, 0) if confidence >= 0.7 else (0, 165, 255) if confidence >= 0.5 else (0, 0, 255)
        cv2.putText(frame, conf_text, (conf_x, conf_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_conf, 2)
        
        # Latency (target < 300ms)
        latency_text = f"Latency: {latency_ms:.1f} ms"
        color_latency = (0, 255, 0) if latency_ms < 300 else (0, 0, 255)
        cv2.putText(frame, latency_text, (10, h - 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_latency, 2)
    
    else:
        # Phase 1: Finger state per hand (below FPS). Capital = open, lowercase = closed.
        y_offset = 120
        for i, hand in enumerate(hand_results):
            fs = hand.finger_state
            parts = [
                "T" if fs.thumb else "t", "I" if fs.index else "i",
                "M" if fs.middle else "m", "R" if fs.ring else "r", "P" if fs.pinky else "p",
            ]
            state_str = " ".join(parts)
            label = f"{hand.handedness}: {state_str}"
            cv2.putText(
                frame, label,
                (10, y_offset + i * 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1
            )
        # Legend
        cv2.putText(
            frame, "T=Thumb I=Index M=Middle R=Ring P=Pinky (cap=open)",
            (10, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1
        )
    
    # Controls
    controls = "Q: Quit | 1: Phase 1 | 2: Phase 2"
    cv2.putText(frame, controls, (10, h - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)


def run_hand_tracking(camera_id: int = 0, start_mode: str = "phase2", 
                      window_width: int = 1280, window_height: int = 720) -> None:
    """
    Main application loop with hand tracking and gesture recognition.
    
    Args:
        camera_id: Camera device ID
        start_mode: "phase1" (tracking only) or "phase2" (with gesture recognition)
        window_width: Window width in pixels
        window_height: Window height in pixels
    """
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print("Could not open webcam. Try another camera_id (e.g. 1).")
        return

    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, window_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, window_height)

    tracker = HandTracker(max_num_hands=2)  # TWO hands for gesture recognition
    feature_extractor = FeatureExtractor()
    classifier = GestureClassifier()
    
    current_mode = start_mode
    
    # Create named window
    window_name = "Naruto Jutsu Recognition System"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, window_width, window_height)
    
    # Check if model is loaded for phase2
    if current_mode == "phase2" and not classifier.is_loaded():
        print("⚠ No trained model found. Switching to Phase 1 mode.")
        print("  To use Phase 2: Run capture_data.py then train_model.py first.")
        current_mode = "phase1"
    
    print("=" * 60)
    print("Naruto Jutsu Recognition System (TWO HANDS)")
    print("=" * 60)
    print(f"Starting in: {current_mode.upper()}")
    print(f"Window size: {window_width}x{window_height}")
    if current_mode == "phase2":
        print(f"Recognized gestures: {', '.join(classifier.get_gesture_names())}")
    print("\nControls:")
    print("  1: Switch to Phase 1 (Hand tracking only)")
    print("  2: Switch to Phase 2 (Gesture recognition)")
    print("  Q: Quit")
    print("=" * 60)
    
    if current_mode == "phase1":
        print("\nPhase 1: Hand tracking. Show your hands to the camera.")
        print("Target: >= 15 FPS, < 300 ms latency.")
    else:
        print("\nPhase 2: Real-time gesture recognition. Perform a Naruto hand sign.")
        print("Target: >= 90% accuracy, < 300 ms latency.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            
            # Resize frame to target size if needed
            if frame.shape[1] != window_width or frame.shape[0] != window_height:
                frame = cv2.resize(frame, (window_width, window_height))
            
            frame = cv2.flip(frame, 1)  # mirror for natural UX

            hand_results: list[HandResult] = tracker.process(frame)
            tracker.draw_landmarks(frame, hand_results)
            fps = tracker.update_fps()
            
            # Gesture recognition (Phase 2 only)
            gesture_info = None
            if current_mode == "phase2" and hand_results and classifier.is_loaded():
                try:
                    # Separate left and right hands
                    left_hand = None
                    right_hand = None
                    
                    for hand in hand_results:
                        if hand.handedness == "Left":
                            left_hand = hand.landmarks
                        elif hand.handedness == "Right":
                            right_hand = hand.landmarks
                    
                    # Extract features from both hands
                    features = feature_extractor.extract_two_hands(left_hand, right_hand)
                    
                    # Predict gesture with timing
                    gesture, confidence, latency_ms = classifier.predict_with_timing(features)
                    
                    gesture_info = {
                        'gesture': gesture,
                        'confidence': confidence,
                        'latency_ms': latency_ms
                    }
                except Exception as e:
                    print(f"Recognition error: {e}")
            
            # Draw UI
            draw_ui_overlay(frame, hand_results, fps, current_mode, gesture_info)

            cv2.imshow(window_name, frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("1"):
                current_mode = "phase1"
                print("\n→ Switched to Phase 1 (Hand tracking)")
            elif key == ord("2"):
                if classifier.is_loaded():
                    current_mode = "phase2"
                    print("\n→ Switched to Phase 2 (Gesture recognition)")
                else:
                    print("\n⚠ No model loaded. Run train_model.py first.")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        tracker.close()
        print("\nSession ended.")


if __name__ == "__main__":
    # Start in Phase 2 mode if model exists, otherwise Phase 1
    models_dir = Path(__file__).resolve().parent.parent / "models"
    start_mode = "phase2" if (models_dir.exists() and list(models_dir.glob("*.pkl"))) else "phase1"
    run_hand_tracking(camera_id=0, start_mode=start_mode, window_width=1280, window_height=720)
