FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Preload models if they exist (non-fatal during build — model is loaded at runtime)
RUN python preload_models.py || echo "No model found at build time — will load at runtime."

# Make startup script executable
RUN chmod +x start.sh

# Smart startup: runs alembic only if real DB is connected, then boots uvicorn
CMD ["sh", "start.sh"]
