import time
import math
import logging
from typing import List
from app.modules.gesture.schema import (
    GestureRecognizeRequest, GestureRecognizeResponse, GestureResult, Landmark
)

logger = logging.getLogger("spiderglass.gesture")

# ISL gesture classifier using geometric rules on hand landmarks
# Landmark indices follow MediaPipe HandLandmark convention:
# 0=Wrist, 4=Thumb tip, 8=Index tip, 12=Middle tip, 16=Ring tip, 20=Pinky tip
# 3=Thumb IP, 5=Index MCP, 6=Index PIP, 9=Middle MCP, etc.

FINGER_TIP_IDS = [4, 8, 12, 16, 20]
FINGER_PIP_IDS = [3, 6, 10, 14, 18]  # PIP joint for index-pinky; IP for thumb


def _distance(a: Landmark, b: Landmark) -> float:
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def _is_finger_extended(landmarks: List[Landmark], tip_id: int, pip_id: int) -> bool:
    """Returns True if a finger tip is above its PIP joint (extended)."""
    return landmarks[tip_id].y < landmarks[pip_id].y


def _fingers_up(landmarks: List[Landmark]) -> List[bool]:
    """Returns a list of booleans [thumb, index, middle, ring, pinky] for extended fingers."""
    extended = []
    # Thumb: compare tip x vs IP x (mirrored webcam)
    extended.append(landmarks[4].x < landmarks[3].x)
    # Other fingers: tip y < pip y
    for tip, pip in zip(FINGER_TIP_IDS[1:], FINGER_PIP_IDS[1:]):
        extended.append(_is_finger_extended(landmarks, tip, pip))
    return extended


def _classify_isl_gesture(landmarks: List[Landmark]) -> tuple[str, float]:
    """
    Rule-based ISL gesture classification.
    Returns (gesture_name, confidence).
    """
    fingers = _fingers_up(landmarks)
    thumb, index, middle, ring, pinky = fingers
    count = sum(fingers)

    wrist = landmarks[0]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    thumb_tip = landmarks[4]

    # ── Specific ISL gestures ─────────────────────────────────────────────────
    if count == 0:
        return "Closed Fist", 0.92

    if count == 5:
        return "Open Palm (Hello)", 0.95

    # Thumbs Up
    if thumb and not index and not middle and not ring and not pinky:
        return "Thumbs Up", 0.93

    # Point / Index finger
    if not thumb and index and not middle and not ring and not pinky:
        return "Pointing", 0.91

    # Peace / Victory
    if not thumb and index and middle and not ring and not pinky:
        return "Peace / Victory", 0.90

    # I Love You (ILY)
    if thumb and index and not middle and not ring and pinky:
        return "I Love You (ILY)", 0.89

    # OK sign: thumb and index close, others open
    tip_dist = _distance(thumb_tip, index_tip)
    wrist_to_index = _distance(wrist, index_tip)
    if tip_dist < wrist_to_index * 0.25 and middle and ring and pinky:
        return "OK", 0.88

    # Call Me: thumb and pinky extended
    if thumb and not index and not middle and not ring and pinky:
        return "Call Me", 0.87

    # Three fingers (ISL number 3)
    if not thumb and index and middle and ring and not pinky:
        return "Three", 0.86

    # Four fingers
    if not thumb and index and middle and ring and pinky:
        return "Four", 0.85

    # Number Two
    if not thumb and index and middle and not ring and not pinky:
        cross = _distance(index_tip, middle_tip)
        if cross < 0.04:
            return "Two (Crossed)", 0.82
        return "Two", 0.84

    return "Unknown Gesture", 0.50


class GestureSessionState:
    def __init__(self):
        self.buffer = []
        self.last_registered_sign = None
        self.sentence = []
        self.last_seen_time = time.time()
        self.FRAMES_TO_HOLD = 10     # Need 10 consecutive frames of same sign
        self.TIMEOUT_SECONDS = 3.0   # Clear if no hands for 3s


class GestureService:
    def __init__(self):
        self.sessions: dict[str, GestureSessionState] = {}

    def _get_state(self, session_id: str) -> GestureSessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = GestureSessionState()
        return self.sessions[session_id]

    async def recognize(self, req: GestureRecognizeRequest, session_id: str = "default") -> tuple[GestureRecognizeResponse, str]:
        """
        Returns a tuple: (GestureResponse, Current Sentence)
        """
        start = time.time()
        results = []
        state = self._get_state(session_id)
        
        # Timeout to finish a sentence
        if time.time() - state.last_seen_time > state.TIMEOUT_SECONDS and state.sentence:
            state.sentence.clear()
            state.last_registered_sign = None

        raw_gestures = []
        for hand_idx, hand_landmarks in enumerate(req.landmarks):
            if len(hand_landmarks) != 21:
                continue
            gesture, confidence = _classify_isl_gesture(hand_landmarks)
            raw_gestures.append(gesture)
            results.append(GestureResult(
                gesture=gesture,
                confidence=confidence,
                hand_index=hand_idx,
            ))

        if raw_gestures:
            state.last_seen_time = time.time()
            primary_gesture = raw_gestures[0]
            
            if primary_gesture != "Unknown Gesture":
                state.buffer.append(primary_gesture)
                
                # Keep buffer size to FRAMES_TO_HOLD
                if len(state.buffer) > state.FRAMES_TO_HOLD:
                    state.buffer.pop(0)
                    
                # If all recent frames match the gesture, register it as a word
                if len(state.buffer) == state.FRAMES_TO_HOLD and all(g == primary_gesture for g in state.buffer):
                    if primary_gesture != state.last_registered_sign:
                        # Append new word to sentence!
                        state.sentence.append(primary_gesture)
                        state.last_registered_sign = primary_gesture
            else:
                state.buffer.clear()
        else:
            state.buffer.clear()

        resp = GestureRecognizeResponse(
            results=results,
            processing_time_ms=int((time.time() - start) * 1000),
        )
        
        sentence_str = " ".join(state.sentence)
        return resp, sentence_str

