# ------------------------------------------------
# 🐳 B-Vista Dockerfile: World-Class Build
# ------------------------------------------------

    FROM python:3.11-slim

    # Set environment variables
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        BVISTA_PORT=5050
    
    # Set working directory
    WORKDIR /app
    
    # Install system packages required for scientific stack
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        && rm -rf /var/lib/apt/lists/*
    
    # Install Python dependencies (we copy first to use Docker layer cache)
    COPY requirements.txt .
    
    RUN pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt
    
    # Copy B-Vista source code into container
    COPY . .
    
    # Install B-Vista package from source
    RUN pip install .
    
    # Expose the backend server port
    EXPOSE 5050
    
    # Default command: Launch B-Vista backend server silently
    CMD ["python", "-m", "bvista.backend.app", "--silent"]
    