FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Preload heavy AI models into the container image
RUN python preload_models.py

# Make startup script executable
RUN chmod +x start.sh

# Smart startup: runs alembic only if real DB is connected, then boots uvicorn
CMD ["sh", "start.sh"]
