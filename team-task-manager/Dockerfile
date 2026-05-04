# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
 
# Copy package.json first
COPY frontend/package.json ./
 
# Install dependencies — force fresh install, no cache
RUN npm install --prefer-offline=false --no-cache
 
# Copy rest of frontend source
COPY frontend/ ./
 
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
 
# Build the frontend
RUN npm run build
 
# Verify dist was actually created and has content
RUN ls -la dist/ && du -sh dist/
 
# ── Stage 2: Python backend + serve frontend ───────────────────────────────────
FROM python:3.12-slim
WORKDIR /app
 
# Install system deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*
 
# Install Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
 
# Verify uvicorn is installed
RUN uvicorn --version
 
# Copy backend source
COPY backend/ ./
 
# Copy built frontend into backend's static folder
COPY --from=frontend-builder /app/frontend/dist ./static
 
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
