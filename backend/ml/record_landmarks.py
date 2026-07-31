import cv2
import mediapipe as mp
import os
import csv
import argparse
import glob

def process_videos_to_landmarks(input_dir: str, output_csv: str, label: int):
    """
    Processes raw videos to extract MediaPipe landmarks and saves them to a CSV file.
    Output CSV format: label, x0, y0, z0, x1, y1, z1, ..., x20, y20, z20
    """
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    # Check if we need to write the header
    write_header = not os.path.exists(output_csv)
    
    with open(output_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            header = ['label']
            for i in range(21):
                header.extend([f'x{i}', f'y{i}', f'z{i}'])
            writer.writerow(header)
            
        video_files = glob.glob(os.path.join(input_dir, "*.mp4"))
        
        if not video_files:
            print(f"No video files found in {input_dir}")
            return
            
        print(f"Processing {len(video_files)} videos...")
        total_frames = 0
        valid_frames = 0
        
        for video_file in video_files:
            cap = cv2.VideoCapture(video_file)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                total_frames += 1
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Flatten landmarks
                        row = [label]
                        for lm in hand_landmarks.landmark:
                            row.extend([lm.x, lm.y, lm.z])
                        
                        writer.writerow(row)
                        valid_frames += 1
            cap.release()
            
    print(f"Processing complete. Extracted {valid_frames}/{total_frames} frames with hands.")
    print(f"Saved to: {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract landmarks from dataset videos.")
    parser.add_argument("--input", type=str, required=True, help="Directory containing raw .mp4 videos")
    parser.add_argument("--output", type=str, default="dataset/processed/landmarks.csv", help="Output CSV file path")
    parser.add_argument("--label", type=int, required=True, help="Integer label for the gesture in these videos")
    
    args = parser.parse_args()
    process_videos_to_landmarks(args.input, args.output, args.label)
