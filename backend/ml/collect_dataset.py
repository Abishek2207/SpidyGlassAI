import cv2
import os
import time
import argparse

def collect_dataset(gesture_name: str, duration_sec: int, save_dir: str):
    """
    Records a dataset video for a specific gesture.
    """
    os.makedirs(save_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30
    
    filename = os.path.join(save_dir, f"{gesture_name}_{int(time.time())}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    print(f"Recording '{gesture_name}' for {duration_sec} seconds...")
    print("Press 'q' to stop early.")
    
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        out.write(frame)
        
        elapsed = time.time() - start_time
        remaining = max(0, duration_sec - elapsed)
        
        cv2.putText(frame, f"Recording: {gesture_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"Time left: {remaining:.1f}s", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow("Dataset Collection", frame)
        
        if elapsed >= duration_sec or cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    print(f"Dataset collection complete. Saved to: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect raw video dataset for sign language.")
    parser.add_argument("--gesture", type=str, required=True, help="Name of the gesture (e.g., hello, peace)")
    parser.add_argument("--duration", type=int, default=10, help="Duration to record in seconds")
    parser.add_argument("--out", type=str, default="dataset/raw", help="Output directory")
    
    args = parser.parse_args()
    collect_dataset(args.gesture, args.duration, args.out)
