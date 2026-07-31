# SpidyGlass AI — ML Pipeline Documentation

## Pipeline Architecture

```
Laptop Camera
    ↓
MediaPipe Hands (CDN, runs in-browser)
    ↓
21 Hand Landmarks (per frame)
    ↓
63 Features (X, Y, Z per landmark)
    ↓
Feature Normalization (wrist-centred, unit scale)
    ↓
PyTorch SignLanguageNN (backend inference)
    ↓
Prediction + Confidence Score
    ↓
JSON Response → Frontend Display
```

---

## Step 1 — Collect Dataset (Required First)

Run this once per gesture. Repeat for **each gesture class**:

```bash
cd backend/ml

# Collect 10 seconds of raw video for each gesture
python collect_dataset.py --gesture hello     --duration 10 --out dataset/raw
python collect_dataset.py --gesture fist      --duration 10 --out dataset/raw
python collect_dataset.py --gesture thumbsup  --duration 10 --out dataset/raw
python collect_dataset.py --gesture pointing  --duration 10 --out dataset/raw
python collect_dataset.py --gesture peace     --duration 10 --out dataset/raw
python collect_dataset.py --gesture iloveyou  --duration 10 --out dataset/raw
python collect_dataset.py --gesture ok        --duration 10 --out dataset/raw
python collect_dataset.py --gesture callme    --duration 10 --out dataset/raw
python collect_dataset.py --gesture three     --duration 10 --out dataset/raw
python collect_dataset.py --gesture four      --duration 10 --out dataset/raw
```

---

## Step 2 — Extract Landmarks from Videos

Run `record_landmarks.py` for each gesture, using its integer label (0–9):

```bash
python record_landmarks.py --input dataset/raw --output dataset/train/train_landmarks.csv --label 0
# ... repeat for each label
```

This extracts all 21-landmark frames from the videos and writes a CSV of shape:
`[label, x0, y0, z0, ..., x20, y20, z20]` (64 columns total).

Separate validation data can be split manually and saved to:
`dataset/validation/val_landmarks.csv`

---

## Step 3 — Train the Model

```bash
python train.py
```

**Features:**
- Adam optimizer with `ReduceLROnPlateau` scheduler
- CrossEntropyLoss
- Early stopping (patience=10)
- Checkpoint saved to `models/sign_language.pt`
- TensorBoard logs written to `runs/`

Monitor training live:
```bash
tensorboard --logdir runs/
```

---

## Step 4 — Validate

```bash
python validation.py
```

**Outputs:**
- Accuracy, Precision, Recall, F1 Score
- Top-1 and Top-3 Accuracy
- Confusion Matrix saved to `exports/confusion_matrix.png`

---

## Step 5 — Export to ONNX

```bash
python export_onnx.py
```

Saves:
- `models/sign_language.onnx`
- `exports/sign_language.onnx`

---

## Step 6 — Live Webcam Prediction (Standalone Test)

```bash
python predict.py
```

Opens webcam and displays real-time gesture + confidence overlay.

---

## Step 7 — Benchmark Inference Speed

```bash
python benchmark.py
```

Reports Mean, P50, P95, P99, Max latency and estimated FPS.

---

## Step 8 — Backend Integration

Once `models/sign_language.pt` exists, restart the backend:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

The backend **startup lifespan** will automatically:
1. Load `.env` via `python-dotenv`
2. Connect database
3. Connect Redis
4. Load `sign_language.pt` → reports `"model": "loaded"` on `/health`
5. Verify Sarvam API key → reports `"sarvam": "connected"` or exact error

---

## Gesture Labels

| Label | Gesture |
|-------|---------|
| 0 | Open Palm (Hello) |
| 1 | Closed Fist |
| 2 | Thumbs Up |
| 3 | Pointing |
| 4 | Peace / Victory |
| 5 | I Love You (ILY) |
| 6 | OK |
| 7 | Call Me |
| 8 | Three |
| 9 | Four |

---

## ⚠️ Important Note

> **The training scripts are production-ready and complete. However, `sign_language.pt` cannot be generated automatically — it requires real webcam dataset collection (Steps 1–2) followed by training (Step 3). There is no shortcut: a neural network must be trained on real data.**

Once trained, the backend will load and serve real predictions with no fake or hardcoded logic.

---

## API Response Format

```json
{
  "results": [
    {
      "gesture": "Peace / Victory",
      "confidence": 0.983,
      "latency": 14,
      "model_version": "v1.0.0",
      "hand_index": 0
    }
  ]
}
```

## Health Endpoint

```json
GET /health

{
  "camera": "connected",
  "mediapipe": "active",
  "model": "loaded",
  "sarvam": "connected",
  "database": "connected",
  "redis": "connected",
  "websocket": "running",
  "gpu": "CPU",
  "memory": "45%",
  "latency": "12ms",
  "model_version": "v1.0.0"
}
```
