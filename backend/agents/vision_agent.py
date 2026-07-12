import cv2
import numpy as np
import base64
import logging

logger = logging.getLogger("visionvoice.vision")

class VisionAgent:
    def __init__(self):
        self.mock_mode = False
        try:
            import mediapipe as mp
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            logger.info("Vision Agent initialized with MediaPipe")
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe: {e}. Falling back to mock mode.")
            self.mock_mode = True

    def process_frame(self, base64_img: str):
        if self.mock_mode:
            # Just return the image back and a dummy gesture
            return {
                "landmarks": [[{"id": 0, "x": 0.5, "y": 0.5, "z": 0}]],
                "processed_image": base64_img
            }
        try:
            # Decode base64 image
            img_data = base64.b64decode(base64_img.split(',')[1] if ',' in base64_img else base64_img)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)
            
            landmarks_data = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    lm_list = []
                    for id, lm in enumerate(hand_landmarks.landmark):
                        lm_list.append({"id": id, "x": lm.x, "y": lm.y, "z": lm.z})
                    landmarks_data.append(lm_list)
                    
                    # Draw landmarks on image for debug/display
                    self.mp_drawing.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            # Encode processed image back to base64
            _, buffer = cv2.imencode('.jpg', img)
            processed_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                "landmarks": landmarks_data,
                "processed_image": f"data:image/jpeg;base64,{processed_base64}"
            }
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return None
