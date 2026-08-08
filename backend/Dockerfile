# ==============================================================================
# SentinelX AI Backend Dockerfile
# Production-ready Python 3.11 slim image with non-root security execution
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_DIR=/app/models \
    DATASETS_DIR=/app/datasets \
    REPORTS_DIR=/app/reports \
    LOGS_DIR=/app/logs

# Install minimal OS dependencies for Postgres, cURL, and building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

WORKDIR /app

# Install Python dependencies first (leverage Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source, migrations, and entrypoint script
COPY . .

# Create volume directories and set ownership to non-root user
RUN mkdir -p /app/models /app/datasets /app/reports /app/logs && \
    chown -R appuser:appgroup /app && \
    chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Docker Healthcheck
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Container Entrypoint & Command
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
