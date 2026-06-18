# --- STAGE 1: Build the React Frontend Dashboard ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- STAGE 2: Spin up the Python Telemetry Engine ---
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies needed for heavy ML frameworks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend specifications
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade -r backend/requirements.txt

# Copy the entire project layout over
COPY . .

# Pull the compiled React production bundle straight into the Python environment
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose Hugging Face's mandatory environment port
EXPOSE 7860

# Switch context into the backend directory so saved_model paths match perfectly
WORKDIR /app/backend

# Launch your backend simulation pipeline from inside the backend directory
CMD ["python", "server.py"]
