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

    async def recognize(self, req: GestureRecognizeRequest, session_id: str = "default") -> tuple[GestureRecognizeResponse, str]:
        start = time.time()
        
        if self.model is None:
            # Crucial: Throw strict error, no fallbacks
            return {"error": "MODEL_NOT_FOUND"}, ""
            
        results = []
        state = self._get_state(session_id)
        
        if time.time() - state.last_seen_time > state.TIMEOUT_SECONDS and state.sentence:
            state.sentence.clear()
            state.last_registered_sign = None

        raw_gestures = []
        
        for hand_idx, hand_landmarks in enumerate(req.landmarks):
            if len(hand_landmarks) != 21:
                continue
                
            # Flatten landmarks to 63 features
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
