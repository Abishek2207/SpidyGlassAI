import base64
import time
import logging
import numpy as np
from typing import Optional
from app.modules.camera.schema import CameraFrameRequest, CameraFrameResponse, DetectedHand
from app.core.exceptions import ValidationException

logger = logging.getLogger("spiderglass.camera")


def _try_import_vision_libs():
    """Attempt to import CV2 and MediaPipe; return None if unavailable."""
    try:
        import cv2
        import mediapipe as mp
        return cv2, mp
    except ImportError:
        logger.warning("OpenCV/MediaPipe not available — camera running in mock mode.")
        return None, None


cv2, mp = _try_import_vision_libs()

# Initialise MediaPipe Hands once at module load
_mp_hands = None
_hands_detector = None

if mp is not None:
    _mp_hands = mp.solutions.hands
    _hands_detector = _mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )
    _mp_drawing = mp.solutions.drawing_utils


class CameraService:

    async def process_frame(self, req: CameraFrameRequest) -> CameraFrameResponse:
        start = time.time()

        # ── Mock mode ─────────────────────────────────────────────────────────
        if cv2 is None or _hands_detector is None:
            return CameraFrameResponse(
                hands_detected=0,
                hands=[],
                annotated_image_base64=req.image_base64,
                processing_time_ms=int((time.time() - start) * 1000),
            )

        # ── Decode image ──────────────────────────────────────────────────────
        try:
            img_bytes = base64.b64decode(req.image_base64.split(",")[-1])
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("Could not decode image")
        except Exception as e:
            raise ValidationException(f"Invalid image data: {e}")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = _hands_detector.process(rgb_frame)

        detected_hands = []
        annotated = frame.copy()

        if results.multi_hand_landmarks:
            for i, (hand_lm, handedness) in enumerate(
                zip(results.multi_hand_landmarks, results.multi_handedness)
            ):
                # Draw landmarks on annotated frame
                _mp_drawing.draw_landmarks(
                    annotated, hand_lm, _mp_hands.HAND_CONNECTIONS
                )

                landmarks = [
                    {"x": lm.x, "y": lm.y, "z": lm.z}
                    for lm in hand_lm.landmark
                ]
                detected_hands.append(DetectedHand(
                    hand_index=i,
                    handedness=handedness.classification[0].label,
                    landmarks=landmarks,
                ))

        # Encode annotated frame back to base64
        _, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
        annotated_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")

        logger.debug(f"Camera: detected {len(detected_hands)} hand(s)")
        return CameraFrameResponse(
            hands_detected=len(detected_hands),
            hands=detected_hands,
            annotated_image_base64=annotated_b64,
            processing_time_ms=int((time.time() - start) * 1000),
        )
