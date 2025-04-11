# ------------------------------------------------
# 🐳 B-Vista Dockerfile: Using Prebuilt Frontend
# ------------------------------------------------

    FROM python:3.11-slim

    # Environment config
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        BVISTA_PORT=5050
    
    WORKDIR /app
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        && rm -rf /var/lib/apt/lists/*
    
    # Install Python dependencies
    COPY requirements.txt .
    RUN pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt
    
    # Copy full project including prebuilt frontend
    COPY . .
    
    # Install B-Vista package
    RUN pip install .
    
    # Expose the backend port
    EXPOSE 5050
    
    # Run the backend
    CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--worker-class", "gevent", "--timeout", "120", "bvista.backend.app:app"]



    