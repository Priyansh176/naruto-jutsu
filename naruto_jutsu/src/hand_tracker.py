"""
Phase 1: Hand tracking using MediaPipe Hands.
Tracks up to 2 hands, 21 landmarks each, with finger state extraction and FPS.
"""

import cv2
import mediapipe as mp
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

# MediaPipe hand landmark indices (21 total)
# 0: WRIST, 1-4: THUMB, 5-8: INDEX, 9-12: MIDDLE, 13-16: RING, 17-20: PINKY
FINGER_TIP_IDS = [4, 8, 12, 16, 20]   # thumb, index, middle, ring, pinky
FINGER_PIP_IDS = [3, 6, 10, 14, 18]   # base of each finger (for open/closed)


@dataclass
class FingerState:
    """Open (True) or closed (False) per finger: thumb, index, middle, ring, pinky."""
    thumb: bool
    index: bool
    middle: bool
    ring: bool
    pinky: bool

    def to_tuple(self) -> Tuple[bool, ...]:
        return (self.thumb, self.index, self.middle, self.ring, self.pinky)


@dataclass
class HandResult:
    """Result for one hand: handedness, landmarks (x,y,z), and finger state."""
    handedness: str  # "Left" or "Right"
    landmarks: List[Tuple[float, float, float]]  # 21 (x, y, z) normalized
    finger_state: FingerState


class HandTracker:
    """
    MediaPipe-based hand tracker.
    - Detects up to 2 hands, 21 landmarks each (x, y, z).
    - Draws landmarks and connections on frame.
    - Exposes finger open/closed state.
    """

    def __init__(
        self,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_complexity: int = 1,
    ):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=model_complexity,
        )
        self._fps_start = None
        self._fps_frame_count = 0
        self._fps_value = 0.0

    def _get_finger_state(self, landmarks) -> FingerState:
        """Heuristic: finger is open if tip is above PIP (smaller y in image coords)."""
        open_flags = []
        for tip_id, pip_id in zip(FINGER_TIP_IDS, FINGER_PIP_IDS):
            tip = landmarks[tip_id]
            pip = landmarks[pip_id]
            # Thumb: use x difference for horizontal movement
            if tip_id == 4:
                open_flags.append(tip.x > pip.x if landmarks[0].x < 0.5 else tip.x < pip.x)
            else:
                open_flags.append(tip.y < pip.y)
        return FingerState(
            thumb=open_flags[0],
            index=open_flags[1],
            middle=open_flags[2],
            ring=open_flags[3],
            pinky=open_flags[4],
        )

    def process(self, frame_bgr: cv2.Mat) -> List[HandResult]:
        """
        Process one BGR frame. Returns list of HandResult (up to 2 hands).
        Landmarks are normalized (0–1) x, y and relative z.
        """
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        hand_results: List[HandResult] = []

        if not results.multi_hand_landmarks:
            return hand_results

        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = "Unknown"
            if results.multi_handedness:
                handedness = results.multi_handedness[idx].classification[0].label

            points = [
                (lm.x, lm.y, lm.z)
                for lm in hand_landmarks.landmark
            ]
            finger_state = self._get_finger_state(hand_landmarks.landmark)
            hand_results.append(HandResult(
                handedness=handedness,
                landmarks=points,
                finger_state=finger_state,
            ))

        return hand_results

    def draw_landmarks(self, frame_bgr: cv2.Mat, hand_results: List[HandResult]) -> None:
        """
        Draw landmarks and connections on frame (in-place).
        Uses MediaPipe drawing utils when we have raw multi_hand_landmarks;
        here we draw from HandResult so we need to convert back to normalized coords
        for mp_draw, or draw manually. We draw manually so we only need HandResult.
        """
        h, w, _ = frame_bgr.shape
        for hand in hand_results:
            for i, (x, y, z) in enumerate(hand.landmarks):
                px, py = int(x * w), int(y * h)
                cv2.circle(frame_bgr, (px, py), 4, (0, 255, 0), -1)
            # Draw connections (simplified: key bones)
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),           # thumb
                (0, 5), (5, 6), (6, 7), (7, 8),           # index
                (0, 9), (9, 10), (10, 11), (11, 12),      # middle
                (0, 13), (13, 14), (14, 15), (15, 16),    # ring
                (0, 17), (17, 18), (18, 19), (19, 20),    # pinky
                (5, 9), (9, 13), (13, 17),                 # palm
            ]
            for i, j in connections:
                if i < len(hand.landmarks) and j < len(hand.landmarks):
                    pt1 = (int(hand.landmarks[i][0] * w), int(hand.landmarks[i][1] * h))
                    pt2 = (int(hand.landmarks[j][0] * w), int(hand.landmarks[j][1] * h))
                    cv2.line(frame_bgr, pt1, pt2, (0, 200, 0), 2)

    def draw_landmarks_mp(self, frame_bgr: cv2.Mat, results) -> None:
        """Draw using MediaPipe's drawer when you have raw results (used in main loop)."""
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame_bgr,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(0, 200, 0), thickness=2),
                )

    def update_fps(self) -> float:
        """Update FPS counter; call once per frame. Returns current FPS."""
        self._fps_frame_count += 1
        now = time.perf_counter()
        if self._fps_start is None:
            self._fps_start = now
            return 0.0
        elapsed = now - self._fps_start
        if elapsed >= 0.5:
            self._fps_value = self._fps_frame_count / elapsed
            self._fps_frame_count = 0
            self._fps_start = now
        return self._fps_value

    def close(self) -> None:
        self.hands.close()

    def __enter__(self) -> "HandTracker":
        return self

    def __exit__(self, *args) -> None:
        self.close()
