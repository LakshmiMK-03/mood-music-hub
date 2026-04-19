# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code and main entry point
COPY src/ ./src/
COPY main.py .

# Environment variables (Defaults - override in HF Settings)
ENV PYTHONPATH=/app
ENV PORT=7860
ENV HOST=0.0.0.0
ENV DEBUG=False

# Expose the port
EXPOSE 7860

# Run the application
CMD ["python", "main.py"]
