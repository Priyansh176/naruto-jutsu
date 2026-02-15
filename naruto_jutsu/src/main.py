"""
Naruto Jutsu Recognition System – entry point.
Phase 1: Hand tracking with webcam, 21 landmarks, 2 hands, FPS and finger state.
Press 'q' to quit.
"""

import cv2
import sys
from pathlib import Path

# Allow running from project root or from naruto_jutsu
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hand_tracker import HandTracker, HandResult, FingerState


def draw_ui_overlay(frame, hand_results: list, fps: float) -> None:
    """Draw FPS and finger state text on frame."""
    h, w = frame.shape[:2]
    # FPS (top-left)
    cv2.putText(
        frame, f"FPS: {fps:.1f}",
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2
    )
    # Target: >= 15 FPS
    color_fps = (0, 255, 0) if fps >= 15 else (0, 0, 255)
    cv2.putText(frame, "Target: 15 FPS", (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_fps, 1)

    # Finger state per hand (below FPS). Capital = open, lowercase = closed.
    y_offset = 90
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
        (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1
    )


def run_hand_tracking(camera_id: int = 0) -> None:
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print("Could not open webcam. Try another camera_id (e.g. 1).")
        return

    tracker = HandTracker(max_num_hands=2)
    print("Phase 1: Hand tracking. Show your hands to the camera. Press 'q' to quit.")
    print("Target: >= 15 FPS, < 300 ms latency.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)  # mirror for natural UX

            hand_results: list[HandResult] = tracker.process(frame)
            tracker.draw_landmarks(frame, hand_results)
            fps = tracker.update_fps()
            draw_ui_overlay(frame, hand_results, fps)

            cv2.imshow("Naruto Jutsu – Hand Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        tracker.close()


if __name__ == "__main__":
    run_hand_tracking(camera_id=0)
