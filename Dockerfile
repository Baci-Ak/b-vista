# ------------------------------------------------
# 🐳 B-Vista Dockerfile
# ------------------------------------------------

# 🔧 Stage 1: Frontend Build
FROM node:18 AS frontend-builder

WORKDIR /app/frontend

# Copy only necessary files first (better for cache)
COPY bvista/frontend/package.json bvista/frontend/package-lock.json ./

# Safe install (use npm install if lock file missing)
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy rest of the frontend code and build
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

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# ✅ Copy built frontend assets into the backend package
COPY --from=frontend-builder /app/frontend/build bvista/frontend/build

# Install B-Vista package locally (with frontend now included)
RUN pip install .

# Expose the backend port
EXPOSE 5050

# 🚀 Default command: Run backend
CMD ["python", "-m", "bvista"]
