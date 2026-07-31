# SpidyGlass AI

SpidyGlass AI is a full-stack, AI-powered assistive communication platform that uses real-time computer vision and speech recognition to translate gestures and voice into actionable text and audio using PyTorch, MediaPipe, and Sarvam AI.

## Architecture

- **Frontend**: React 19, Vite, Tailwind CSS, Zustand, MediaPipe Hands (Client-side tracking)
- **Backend**: FastAPI, PostgreSQL / SQLite (Demo Mode Fallback), Redis, PyTorch, Sarvam AI Integrations
- **Agent Mesh**: Distributed node architecture for Speech, Vision, Translation, and LLM Orchestration.

## Windows 11 Setup Guide

The project is fully configured for automated setup on Windows 11. 

### Prerequisites

1. **Python 3.12+**: Download from [python.org](https://www.python.org/downloads/windows/).
   - **CRITICAL**: During installation, you MUST check the box that says **"Add Python 3.x to PATH"** at the bottom of the installer window.
2. **Node.js (v18+)**: Required for the frontend application.
3. **Docker Desktop (Optional)**: Can be used to automatically start PostgreSQL and Redis. If you don't use Docker, the application will elegantly fall back to SQLite for local development.
4. **Environment Variables**: The `setup` script will automatically create a `.env` file if one is missing in the `backend/` directory.

### Automated Installation

You can use either the PowerShell script or the Batch script. They perform identical tasks: checking Python, creating a virtual environment, upgrading pip, installing all dependencies, running database migrations, checking system health, and starting the backend `app.main:app` server.

**Using PowerShell (Recommended)**
```powershell
.\setup.ps1
```
*(Note: If you get an Execution Policy error, run `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process` first).*

**Using Command Prompt (CMD)**
```cmd
setup.bat
```

### Verification

The scripts will automatically run `verify_environment.py`, which performs health checks on:
- Python, pip, Node, & Git
- Database connection (PostgreSQL/SQLite)
- Redis connection
- Sarvam API keys
- PyTorch Model availability

### Running the Frontend

Once the backend is running, open a new terminal for the frontend:

```powershell
cd frontend
npm install
npm run dev
```

### Troubleshooting

- **`MODEL_NOT_FOUND`**: If you see this in the Vision dashboard, it means you need to place your PyTorch model at `backend/models/sign_language.pt`. The backend will gracefully degrade without crashing.
- **`SERVICE_NOT_CONFIGURED`**: If you see this in the Speech, Assistant or Translation dashboard, your `SARVAM_API_KEY` is missing from the `backend/.env` file. Demo Mode Fallbacks will be active.
