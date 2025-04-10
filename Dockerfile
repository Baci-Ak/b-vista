# ------------------------------------------------
# 🐳 B-Vista Dockerfile: World-Class Multi-Stage Build
# ------------------------------------------------

# 🔧 Stage 1: Frontend Build
FROM node:18 AS frontend-builder

WORKDIR /app/frontend

# Install frontend dependencies first (cached layer)
COPY bvista/frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY bvista/frontend/ ./
RUN npm run build


# 🐍 Stage 2: Backend + Final Image
FROM python:3.11-slim

# Environment config
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BVISTA_PORT=5050

WORKDIR /app

# System packages for Python & Sci stack
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first to optimize layers
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy source code (backend + Python modules)
COPY . .

# 🔗 Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/build bvista/frontend/build

# Install B-Vista package locally (with frontend now included)
RUN pip install .

# Expose the backend port
EXPOSE 5050

# 🚀 Default run command
CMD ["python", "-m", "bvista"]
