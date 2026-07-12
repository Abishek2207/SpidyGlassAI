# SpiderGlass AI

SpiderGlass is a production-ready, AI-powered assistive smart-glass platform built for people with speech and hearing impairments. 
It seamlessly fuses real-time gesture recognition (ISL/ASL), continuous STT audio processing, real-time multi-language translation, and contextual LLM understanding into a premium Heads-Up Display (HUD) experience.

## Architecture
The system consists of:
1. **Frontend (Vite + React + Tailwind + Framer Motion)**: A hardware-agnostic HUD interface designed to feel like a premium wearable display (Jarvis/Vision Pro style). It features a subtle particle mesh background, real-time telemetry, and scrolling conversation logs.
2. **Backend (FastAPI + SQLAlchemy + Asyncio)**: A Python service that orchestrates a Multi-Agent architecture. It handles:
   - Temporal Gesture Buffering (Signs → Sentences)
   - Continuous Audio STT Buffering
   - AI Processing Pipeline (Vision Agent, Gesture Agent, Speech Agent, Translation Agent, Conversation Agent, TTS Agent, Memory Agent).
3. **Database (SQLite/Postgres)**: Enterprise audit logging for all interactions via Alembic migrations.
4. **Hardware Abstraction Layer**: `LaptopCameraProvider` and `LaptopAudioProvider` simulate the smart-glass peripherals via WebSocket, allowing easy transition to embedded Android/Linux builds in the future.

## Prerequisites
- Docker & Docker Compose
- Or: Python 3.11+, Node.js 20+

## Getting Started (Docker)
The easiest way to launch SpiderGlass is via Docker:

```bash
# Set your AI API keys
export SARVAM_API_KEY=your_key_here

# Build and start the platform
docker compose up --build
```
Navigate to `http://localhost` to view the HUD interface.

## Getting Started (Local Development)

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate
pip install -r requirements.txt

# Run migrations to setup local SQLite
alembic upgrade head

# Start API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Testing
- **Backend**: Run `pytest` inside the `/backend` directory.
- **Frontend**: Run `npm run test` inside the `/frontend` directory.
