# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install --legacy-peer-deps
RUN npm install
COPY frontend/ ./
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# ── Stage 2: Python backend + serve frontend ───────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Copy built frontend into backend's static folder
COPY --from=frontend-builder /app/frontend/dist ./static

ENV PYTHONUNBUFFERED=1

EXPOSE 8000
# JSON array form is required so the process receives OS signals directly
# (PID 1) rather than being wrapped in /bin/sh -c, which would swallow SIGTERM
# and cause the healthcheck to time out before the app finishes starting.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

 
