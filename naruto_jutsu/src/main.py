"""
Naruto Jutsu Recognition System – entry point.
Phase 3: Hand tracking + gesture recognition + SEQUENCE DETECTION for jutsus.
Press 'q' to quit, '1'/'2'/'3' to switch between phases.
"""

import cv2
import sys
from pathlib import Path
import time
import numpy as np

# Allow running from project root or from naruto_jutsu
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hand_tracker import HandTracker, HandResult, FingerState
from feature_extractor import FeatureExtractor
from gesture_classifier import GestureClassifier
from sequence_detector import SequenceDetector


def load_gesture_images(images_dir: Path) -> dict:
    """
    Load all gesture images.
    
    Args:
        images_dir: Path to images folder
        
    Returns:
        Dict mapping gesture names to loaded images
    """
    gesture_images = {}
    
    gesture_names = [
        'Tiger', 'Ram', 'Snake', 'Dragon', 'Boar', 'Dog',
        'Monkey', 'Rabbit', 'Ox', 'Bird', 'Horse', 'Rat'
    ]
    
    for name in gesture_names:
        img_path = images_dir / f"{name.lower()}.png"
        if img_path.exists():
            img = cv2.imread(str(img_path))
            if img is not None:
                gesture_images[name] = img
                
    print(f"Loaded {len(gesture_images)} gesture images")
    return gesture_images


def draw_sequence_images(frame, sequence: list, current_index: int, gesture_images: dict,
                         completed_gestures: list, y_position: int = 100) -> None:
    """
    Draw sequence images horizontally with highlighting and dimming.
    
    Args:
        frame: Video frame to draw on
        sequence: List of gesture names in order
        current_index: Index of current gesture to perform (-1 if none started)
        gesture_images: Dict of loaded gesture images
        completed_gestures: List of completed gesture names
        y_position: Y position to start drawing
    """
    h, w = frame.shape[:2]
    img_size = 120  # Size of each gesture image
    spacing = 20
    arrow_width = 30
    
    # Calculate total width
    total_width = (img_size * len(sequence)) + (spacing * (len(sequence) - 1)) + ((len(sequence) - 1) * arrow_width)
    start_x = (w - total_width) // 2
    
    for i, gesture_name in enumerate(sequence):
        x_pos = start_x + i * (img_size + spacing + arrow_width)
        
        # Get gesture image
        if gesture_name in gesture_images:
            img = gesture_images[gesture_name].copy()
            img = cv2.resize(img, (img_size, img_size))
            
            # Apply effects based on state
            if gesture_name in completed_gestures:
                # Dim and desaturate completed gestures
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
                img = cv2.addWeighted(img, 0.3, np.zeros_like(img), 0.7, 0)
                border_color = (100, 100, 100)  # Gray
                border_thickness = 2
            elif i == current_index:
                # Highlight current gesture
                border_color = (0, 255, 0)  # Bright green
                border_thickness = 5
            else:
                # Normal (upcoming gestures)
                border_color = (255, 255, 255)  # White
                border_thickness = 2
            
            # Place image on frame
            y1, y2 = y_position, y_position + img_size
            x1, x2 = x_pos, x_pos + img_size
            
            if y2 <= h and x2 <= w:
                frame[y1:y2, x1:x2] = img
                
                # Draw border
                cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, border_thickness)
                
                # Add gesture name
                text_size = cv2.getTextSize(gesture_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                text_x = x1 + (img_size - text_size[0]) // 2
                text_y = y2 + 20
                
                # Background for text
                cv2.rectangle(frame, 
                             (text_x - 5, text_y - text_size[1] - 2),
                             (text_x + text_size[0] + 5, text_y + 5),
                             (0, 0, 0), -1)
                
                text_color = (100, 100, 100) if gesture_name in completed_gestures else (255, 255, 255)
                cv2.putText(frame, gesture_name, (text_x, text_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
            
            # Draw arrow between gestures
            if i < len(sequence) - 1:
                arrow_x = x2 + spacing
                arrow_y = y_position + img_size // 2
                arrow_color = (100, 100, 100) if i < len(completed_gestures) else (200, 200, 200)
                cv2.arrowedLine(frame, (arrow_x, arrow_y), 
                               (arrow_x + arrow_width - 10, arrow_y),
                               arrow_color, 3, tipLength=0.5)


def draw_ui_overlay(frame, hand_results: list, fps: float, mode: str = "phase1", 
                    gesture_info: dict = None, sequence_info: dict = None, 
                    jutsu_detected: dict = None, gesture_images: dict = None) -> None:
    """
    Draw FPS and finger state text on frame.
    
    Args:
        frame: Video frame to draw on
        hand_results: List of HandResult objects
        fps: Current FPS value
        mode: "phase1" (tracking only), "phase2" (gesture recognition), or "phase3" (sequence detection)
        gesture_info: Dict with 'gesture', 'confidence', 'latency_ms' for phase2/phase3
        sequence_info: Dict with sequence progress for phase3
        jutsu_detected: Dict with jutsu info when a sequence is completed
        gesture_images: Dict of loaded gesture images for visual sequence display
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
    mode_text = {
        "phase1": "Mode: Phase 1 (Tracking)",
        "phase2": "Mode: Phase 2 (Recognition)",
        "phase3": "Mode: Phase 3 (Sequence Detection)"
    }.get(mode, "Mode: Unknown")
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
    
    # Phase 3: Sequence detection display
    if mode == "phase3":
        # Display sequence images if in targeted mode
        if sequence_info and sequence_info.get('target_mode') and gesture_images:
            target_jutsu = sequence_info.get('target_jutsu')
            if target_jutsu:
                sequence = target_jutsu['sequence']
                completed = sequence_info.get('gestures', [])
                current_idx = len(completed)  # Next gesture to perform
                
                # Draw sequence images
                draw_sequence_images(frame, sequence, current_idx, gesture_images, 
                                    completed, y_position=50)
        
        # Display jutsu detection (if any)
        if jutsu_detected:
            # Large jutsu name with effects
            jutsu_text = jutsu_detected['name']
            japanese_text = jutsu_detected['japanese']
            
            text_size = cv2.getTextSize(jutsu_text, cv2.FONT_HERSHEY_SIMPLEX, 1.8, 3)[0]
            text_x = (w - text_size[0]) // 2
            text_y = h // 2
            
            # Background rectangle with jutsu color
            padding = 30
            color = tuple(reversed(jutsu_detected['effects']['color']))  # BGR format
            cv2.rectangle(frame, 
                          (text_x - padding, text_y - text_size[1] - padding),
                          (text_x + text_size[0] + padding, text_y + padding + 40),
                          color, -1)
            cv2.rectangle(frame,
                          (text_x - padding, text_y - text_size[1] - padding),
                          (text_x + text_size[0] + padding, text_y + padding + 40),
                          (255, 255, 255), 3)
            
            # Jutsu name
            cv2.putText(frame, jutsu_text, (text_x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 3)
            
            # Japanese name below
            jp_size = cv2.getTextSize(japanese_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
            jp_x = (w - jp_size[0]) // 2
            cv2.putText(frame, japanese_text, (jp_x, text_y + 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        
        # Display time and confidence in bottom left
        if sequence_info and sequence_info.get('active'):
            elapsed = sequence_info['elapsed']
            cv2.putText(frame, f"Time: {elapsed:.1f}s", (10, h - 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    # Controls
    controls = "Q: Quit | 1: Phase 1 | 2: Phase 2 | 3: Phase 3 | M: Menu"
    cv2.putText(frame, controls, (10, h - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)


def select_jutsu_menu(sequence_detector: SequenceDetector) -> str:
    """
    Display jutsu selection menu in console.
    
    Args:
        sequence_detector: SequenceDetector instance with loaded jutsus
        
    Returns:
        Selected jutsu name or empty string to cancel
    """
    print("\n" + "=" * 60)
    print("SELECT JUTSU TO PERFORM")
    print("=" * 60)
    
    for i, jutsu in enumerate(sequence_detector.jutsus, 1):
        seq_str = " → ".join(jutsu['sequence'])
        print(f"{i}. {jutsu['name']}")
        print(f"   {jutsu['japanese']}")
        print(f"   Sequence: {seq_str}")
        print(f"   Time: {jutsu['time_window']:.1f}s")
        print()
    
    print("0. Free Mode (detect all jutsus)")
    print("=" * 60)
    
    try:
        choice = input("\nEnter number (0-{0}): ".format(len(sequence_detector.jutsus)))
        choice = int(choice)
        
        if choice == 0:
            return "FREE_MODE"
        elif 1 <= choice <= len(sequence_detector.jutsus):
            return sequence_detector.jutsus[choice - 1]['name']
        else:
            print("Invalid choice!")
            return ""
    except (ValueError, KeyboardInterrupt):
        print("\nCancelled")
        return ""


def run_hand_tracking(camera_id: int = 0, start_mode: str = "phase3", 
                      window_width: int = 1280, window_height: int = 720) -> None:
    """
    Main application loop with hand tracking, gesture recognition, and sequence detection.
    
    Args:
        camera_id: Camera device ID
        start_mode: "phase1" (tracking), "phase2" (gesture recognition), or "phase3" (sequence detection)
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
    sequence_detector = SequenceDetector()  # Phase 3: Sequence detection
    
    # Load gesture images
    images_dir = Path(__file__).resolve().parent.parent / "images"
    gesture_images = load_gesture_images(images_dir)
    
    current_mode = start_mode
    
    # Create named window
    window_name = "Naruto Jutsu Recognition System"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, window_width, window_height)
    
    # Check if model is loaded for phase2/phase3
    if current_mode in ["phase2", "phase3"] and not classifier.is_loaded():
        print("⚠ No trained model found. Switching to Phase 1 mode.")
        print("  To use Phase 2/3: Run capture_data.py then train_model.py first.")
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
    print("  3: Switch to Phase 3 (Sequence detection)")
    print("  M: Open jutsu selection menu")
    print("  Q: Quit")
    print("=" * 60)
    
    if current_mode == "phase1":
        print("\nPhase 1: Hand tracking. Show your hands to the camera.")
        print("Target: >= 15 FPS, < 300 ms latency.")
    elif current_mode == "phase2":
        print("\nPhase 2: Real-time gesture recognition. Perform a Naruto hand sign.")
        print("Target: >= 90% accuracy, < 300 ms latency.")
    else:
        print("\nPhase 3: Jutsu sequence detection. Perform hand sign sequences!")
        print("\nPress 'M' to select a specific jutsu to perform.")
        print("Available jutsus:")
        for jutsu in sequence_detector.jutsus:
            seq_str = " → ".join(jutsu['sequence'])
            print(f"  - {jutsu['name']}: {seq_str}")
        print("Target: Detect sequences within time window.")
        
        # Auto-select first jutsu on startup
        if sequence_detector.jutsus:
            first_jutsu = sequence_detector.jutsus[0]['name']
            sequence_detector.set_target_jutsu(first_jutsu, instant_detection=True)
            print(f"\n[AUTO-SELECTED] {first_jutsu}")
            print("Perform the sequence shown on screen. Press 'M' to change jutsu.")

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
            
            # Gesture recognition (Phase 2 and Phase 3)
            gesture_info = None
            sequence_info = None
            jutsu_detected = None
            
            if current_mode in ["phase2", "phase3"] and hand_results and classifier.is_loaded():
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
                    
                    # Phase 3: Sequence detection
                    if current_mode == "phase3":
                        # Feed gesture to sequence detector
                        detected = sequence_detector.update(gesture, confidence)
                        
                        if detected:
                            # Jutsu completed!
                            jutsu_detected = detected
                            print(f"\n🔥 JUTSU DETECTED: {detected['name']} ({detected['japanese']}) 🔥\n")
                        
                        # Get sequence progress for display
                        sequence_info = sequence_detector.get_current_progress()
                
                except Exception as e:
                    print(f"Recognition error: {e}")
            
            # Draw UI
            draw_ui_overlay(frame, hand_results, fps, current_mode, gesture_info, 
                            sequence_info, jutsu_detected, gesture_images)

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
                    sequence_detector.reset()  # Reset sequence when switching modes
                    print("\n→ Switched to Phase 2 (Gesture recognition)")
                else:
                    print("\n⚠ No model loaded. Run train_model.py first.")
            elif key == ord("3"):
                if classifier.is_loaded():
                    current_mode = "phase3"
                    sequence_detector.reset()  # Reset sequence when switching modes
                    # Auto-select first jutsu
                    if sequence_detector.jutsus:
                        first_jutsu = sequence_detector.jutsus[0]['name']
                        sequence_detector.set_target_jutsu(first_jutsu, instant_detection=True)
                    print("\n→ Switched to Phase 3 (Sequence detection)")
                    print("Available jutsus:")
                    for jutsu in sequence_detector.jutsus:
                        seq_str = " → ".join(jutsu['sequence'])
                        print(f"  - {jutsu['name']}: {seq_str}")
                else:
                    print("\n⚠ No model loaded. Run train_model.py first.")
            elif key == ord("m") or key == ord("M"):
                # Open jutsu selection menu
                if current_mode == "phase3":
                    selected = select_jutsu_menu(sequence_detector)
                    if selected == "FREE_MODE":
                        sequence_detector.clear_target()
                        print("\n→ Free Mode: Detecting all jutsus")
                    elif selected:
                        sequence_detector.set_target_jutsu(selected, instant_detection=True)
                        print(f"\n→ Selected: {selected}")
                        print("Perform the sequence shown on screen.")
                else:
                    print("\n⚠ Jutsu menu only available in Phase 3")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        tracker.close()
        print("\nSession ended.")


if __name__ == "__main__":
    # Start in Phase 3 mode if model exists, otherwise Phase 1
    models_dir = Path(__file__).resolve().parent.parent / "models"
    start_mode = "phase3" if (models_dir.exists() and list(models_dir.glob("*.pkl"))) else "phase1"
    run_hand_tracking(camera_id=0, start_mode=start_mode, window_width=1280, window_height=720)
