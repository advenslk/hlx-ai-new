# ==============================================================
# HELZERX AI SUPPORT - DOCKERFILE
# ==============================================================
FROM python:3.12-slim-bookworm AS base

# Prevent Python from writing .pyc and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app

# Create non-root system user for security
RUN groupadd -r helzerx && useradd -r -g helzerx -d /app -s /sbin/nologin helzerx && \
    mkdir -p /app/logs /app/transcripts /app/knowledge/data && \
    chown -R helzerx:helzerx /app

USER helzerx

# Health check verifies database & AI configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python3 scripts/test_nvidia_connection.py --quiet || exit 1

# Default command to run the Discord Bot
CMD ["python3", "bot/main.py"]
