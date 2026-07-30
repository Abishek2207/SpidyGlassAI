import base64
import time
import logging
import numpy as np
from typing import Optional
from app.modules.camera.schema import CameraFrameRequest, CameraFrameResponse, DetectedHand, DetectedObject, DetectedFace
from app.core.exceptions import ValidationException

logger = logging.getLogger("spiderglass.camera")


def _try_import_vision_libs():
    """Attempt to import CV2, MediaPipe, and Ultralytics; return None if unavailable."""
    try:
        import cv2
        import mediapipe as mp
        from ultralytics import YOLO
        return cv2, mp, YOLO
    except ImportError:
        logger.warning("Vision libs not available — camera running in mock mode.")
        return None, None, None


cv2, mp, YOLO = _try_import_vision_libs()

# Initialise MediaPipe and YOLO once at module load
_mp_hands = None
_hands_detector = None
_mp_face = None
_face_detector = None
_mp_drawing = None
_yolo_model = None

if mp is not None and YOLO is not None:
    _mp_hands = mp.solutions.hands
    _hands_detector = _mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )
    _mp_face = mp.solutions.face_detection
    _face_detector = _mp_face.FaceDetection(
        min_detection_confidence=0.6,
        model_selection=0
    )
    _mp_drawing = mp.solutions.drawing_utils
    try:
        _yolo_model = YOLO("yolov8n.pt")
    except Exception as e:
        logger.error(f"Failed to load YOLO model: {e}")


class CameraService:
    def __init__(self):
        self.frame_count = 0
        self.last_objects = []

    async def process_frame(self, req: CameraFrameRequest) -> CameraFrameResponse:
        start = time.time()
        self.frame_count += 1

        # ── Mock mode ─────────────────────────────────────────────────────────
        if cv2 is None or _hands_detector is None:
            return CameraFrameResponse(
                hands_detected=0,
                hands=[],
                objects=[],
                faces=[],
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
        
        detected_hands = []
        detected_faces = []
        detected_objects = self.last_objects
        annotated = frame.copy()
        h, w, _ = frame.shape

        # 1. Hand Detection
        hand_results = _hands_detector.process(rgb_frame)
        if hand_results.multi_hand_landmarks:
            for i, (hand_lm, handedness) in enumerate(zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness)):
                _mp_drawing.draw_landmarks(annotated, hand_lm, _mp_hands.HAND_CONNECTIONS)
                landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in hand_lm.landmark]
                detected_hands.append(DetectedHand(
                    hand_index=i,
                    handedness=handedness.classification[0].label,
                    landmarks=landmarks,
                ))

        # 2. Face Detection
        face_results = _face_detector.process(rgb_frame)
        if face_results.detections:
            for detection in face_results.detections:
                bboxC = detection.location_data.relative_bounding_box
                x_min, y_min = bboxC.xmin, bboxC.ymin
                width_b, height_b = bboxC.width, bboxC.height
                x_max, y_max = x_min + width_b, y_min + height_b
                detected_faces.append(DetectedFace(
                    confidence=detection.score[0],
                    bbox=[x_min, y_min, x_max, y_max]
                ))
                ix, iy, ix2, iy2 = int(x_min * w), int(y_min * h), int(x_max * w), int(y_max * h)
                cv2.rectangle(annotated, (ix, iy), (ix2, iy2), (255, 0, 255), 2)
                cv2.putText(annotated, f"Face {int(detection.score[0]*100)}%", (ix, iy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

        # 3. Object Detection (YOLO) - Every 5 frames to save CPU
        if _yolo_model is not None and self.frame_count % 5 == 0:
            yolo_results = _yolo_model(frame, verbose=False)
            new_objects = []
            for r in yolo_results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxyn = box.xyxyn[0].tolist() 
                    label = _yolo_model.names[cls_id]
                    
                    if conf > 0.5:
                        new_objects.append(DetectedObject(
                            label=label,
                            confidence=conf,
                            bbox=xyxyn
                        ))
            self.last_objects = new_objects
            detected_objects = new_objects

        # Draw YOLO objects
        for obj in detected_objects:
            x_min, y_min, x_max, y_max = obj.bbox
            ix, iy, ix2, iy2 = int(x_min * w), int(y_min * h), int(x_max * w), int(y_max * h)
            cv2.rectangle(annotated, (ix, iy), (ix2, iy2), (0, 255, 255), 2)
            cv2.putText(annotated, f"{obj.label} {int(obj.confidence*100)}%", (ix, iy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # Encode annotated frame back to base64
        _, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
        annotated_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")

        return CameraFrameResponse(
            hands_detected=len(detected_hands),
            hands=detected_hands,
            objects=detected_objects,
            faces=detected_faces,
            annotated_image_base64=annotated_b64,
            processing_time_ms=int((time.time() - start) * 1000),
        )
