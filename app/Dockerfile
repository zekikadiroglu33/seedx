# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    ffmpeg \
    v4l-utils \
    libgl1 \
    libglib2.0-0 \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Add the current directory to PYTHONPATH
ENV PYTHONPATH=/app

# API server
EXPOSE 8000

# Fix the CMD instruction to properly run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
