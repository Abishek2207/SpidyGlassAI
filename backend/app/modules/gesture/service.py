import time
import os
import logging
import torch
from typing import List
from app.modules.gesture.schema import (
    GestureRecognizeRequest, GestureRecognizeResponse, GestureResult, Landmark
)

logger = logging.getLogger("spiderglass.gesture")

class GestureSessionState:
    def __init__(self):
        self.buffer = []
        self.last_registered_sign = None
        self.sentence = []
        self.last_seen_time = time.time()
        self.FRAMES_TO_HOLD = 10     
        self.TIMEOUT_SECONDS = 3.0   


class GestureService:
    def __init__(self):
        self.sessions: dict[str, GestureSessionState] = {}
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Mapping index to ISL labels
        self.classes = [
            "Open Palm (Hello)", "Closed Fist", "Thumbs Up", "Pointing", 
            "Peace / Victory", "I Love You (ILY)", "OK", "Call Me", 
            "Three", "Four"
        ]
        
        # Load the PyTorch Model
        model_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "sign_language.pt")
        if os.path.exists(model_path):
            try:
                self.model = torch.load(model_path, map_location=self.device)
                self.model.eval()
                logger.info("Loaded PyTorch gesture model.")
            except Exception as e:
                logger.error(f"Failed to load PyTorch model: {e}")
        else:
            logger.warning(f"PyTorch model not found at {model_path}")

    def _get_state(self, session_id: str) -> GestureSessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = GestureSessionState()
        return self.sessions[session_id]

    def _demo_classify(self, landmarks) -> tuple[str, float]:
        # Simple heuristic based on MediaPipe y-coordinates
        # MediaPipe origin is top-left, so lower y value means "higher" on screen
        fingers_up = {
            "thumb": landmarks[4].y < landmarks[3].y,
            "index": landmarks[8].y < landmarks[6].y,
            "middle": landmarks[12].y < landmarks[10].y,
            "ring": landmarks[16].y < landmarks[14].y,
            "pinky": landmarks[20].y < landmarks[18].y,
        }
        
        up_count = sum(fingers_up.values())
        
        if up_count == 5:
            return "HELLO", 0.99
        elif up_count == 0:
            return "STOP", 0.95
        elif fingers_up["thumb"] and up_count == 1:
            return "YES", 0.90
        elif fingers_up["index"] and fingers_up["middle"] and up_count == 2:
            return "THANK YOU", 0.85
        else:
            return "NO", 0.80

    async def recognize(self, req: GestureRecognizeRequest, session_id: str = "default") -> tuple[GestureRecognizeResponse, str]:
        start = time.time()
        
        results = []
        state = self._get_state(session_id)
        
        if time.time() - state.last_seen_time > state.TIMEOUT_SECONDS and state.sentence:
            state.sentence.clear()
            state.last_registered_sign = None

        raw_gestures = []
        
        for hand_idx, hand_landmarks in enumerate(req.landmarks):
            if len(hand_landmarks) != 21:
                continue
                
            if self.model is None:
                # DEMO MODE
                gesture, conf_val = self._demo_classify(hand_landmarks)
                raw_gestures.append(gesture)
                results.append(GestureResult(
                    gesture=gesture,
                    confidence=conf_val,
                    latency=int((time.time() - start) * 1000),
                    model_version="Demo Classification (ML model not loaded)",
                    hand_index=hand_idx,
                ))
            else:
                # REAL INFERENCE
                flat_features = []
                for lm in hand_landmarks:
                    flat_features.extend([lm.x, lm.y, lm.z])
                    
                input_tensor = torch.tensor([flat_features], dtype=torch.float32).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model(input_tensor)
                    probabilities = torch.nn.functional.softmax(outputs, dim=1)
                    confidence, predicted_idx = torch.max(probabilities, 1)
                    
                    gesture = self.classes[predicted_idx.item()]
                    conf_val = confidence.item()
                    
                    raw_gestures.append(gesture)
                    results.append(GestureResult(
                        gesture=gesture,
                        confidence=conf_val,
                        latency=int((time.time() - start) * 1000),
                        model_version="v1.0.0",
                        hand_index=hand_idx,
                    ))

        if raw_gestures:
            state.last_seen_time = time.time()
            primary_gesture = raw_gestures[0]
            
            state.buffer.append(primary_gesture)
            if len(state.buffer) > state.FRAMES_TO_HOLD:
                state.buffer.pop(0)
                
            if len(state.buffer) == state.FRAMES_TO_HOLD and all(g == primary_gesture for g in state.buffer):
                if primary_gesture != state.last_registered_sign:
                    state.sentence.append(primary_gesture)
                    state.last_registered_sign = primary_gesture
        else:
            state.buffer.clear()

        resp = GestureRecognizeResponse(
            results=results
        )
        
        sentence_str = " ".join(state.sentence)
        return resp, sentence_str
