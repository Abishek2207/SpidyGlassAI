import cv2
import mediapipe as mp
import torch
import time
import os
import numpy as np

def predict_webcam():
    model_path = "models/sign_language.pt"
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}.")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = torch.load(model_path, map_location=device)
    model.eval()
    
    classes = [
        "Open Palm (Hello)", "Closed Fist", "Thumbs Up", "Pointing", 
        "Peace / Victory", "I Love You (ILY)", "OK", "Call Me", 
        "Three", "Four"
    ]

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    cap = cv2.VideoCapture(0)
    
    print("Starting live prediction. Press 'q' to quit.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        start_time = time.time()
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Extract and normalize
                flat_features = []
                wrist_x = hand_landmarks.landmark[0].x
                wrist_y = hand_landmarks.landmark[0].y
                wrist_z = hand_landmarks.landmark[0].z
                
                for lm in hand_landmarks.landmark:
                    flat_features.extend([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])
                    
                features_np = np.array(flat_features, dtype=np.float32)
                max_val = np.max(np.abs(features_np))
                if max_val > 0:
                    features_np /= max_val
                    
                input_tensor = torch.tensor([features_np]).to(device)
                
                with torch.no_grad():
                    outputs = model(input_tensor)
                    probs = torch.nn.functional.softmax(outputs, dim=1)
                    confidence, predicted_idx = torch.max(probs, 1)
                    
                gesture = classes[predicted_idx.item()]
                conf_val = confidence.item()
                
                fps = 1.0 / (time.time() - start_time)
                
                cv2.putText(frame, f"{gesture} ({conf_val*100:.1f}%)", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
        cv2.imshow("Sign Language Prediction", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    predict_webcam()
