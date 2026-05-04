# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
 
COPY frontend/package.json ./
RUN npm install --prefer-offline=false --no-cache
 
COPY frontend/ ./
 
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build
RUN ls -la dist/ && du -sh dist/
 
# ── Stage 2: Python backend + serve frontend ───────────────────────────────────
FROM python:3.12-slim
WORKDIR /app
 
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*
 
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN uvicorn --version
 
COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist ./static
 
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
EXPOSE 8000
 
# Write a start script that expands $PORT at runtime
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"' >> /start.sh && \
    chmod +x /start.sh
 
ENTRYPOINT ["/bin/sh", "/start.sh"]
