"""
FILE 24: DOCKERFILE INFRASTRUCTURE
==================================
Production Docker image for Opus Maximus Island Engine.
GPU-enabled, optimized for theological entry generation.

[EDIT 23 ADVISORY]:
For local development on high-performance hardware (e.g., ASUS ROG Zephyrus Duo),
DIRECT EXECUTION is recommended over Docker to avoid container virtualization overhead.
Run directly: python3 006-cli-orchestration.py generate ...
Use this Dockerfile for cloud/server deployments only.

File 14 of 20: Infrastructure (Docker)
"""

# ============================================================================
# Dockerfile - Production Image
# ============================================================================
DOCKERFILE = """
FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python and dependencies
# Added git for potential dynamic installs, procps for monitoring
RUN apt-get update && apt-get install -y \\
    python3.10 \\
    python3-pip \
    git \\
    procps \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with appropriate permissions
RUN mkdir -p /app/GENERATED_ENTRIES_MASTER \\
    && mkdir -p /app/OPUS_MAXIMUS_INDIVIDUALIZED \\
    && mkdir -p /app/models \\
    && mkdir -p /app/logs \\
    && mkdir -p /app/.cache

# Set environment variables optimized for CUDA
ENV PYTHONUNBUFFERED=1
ENV OPUS_DEBUG=false
ENV OPUS_LOG_LEVEL=INFO
ENV CUDA_VISIBLE_DEVICES=0
# PyTorch memory settings to avoid fragmentation in container
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Expose port for dashboard
EXPOSE 8501

# Health check ensuring python can at least start
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Default command uses the CLI orchestrator
CMD ["python3", "-m", "opus_maximus.cli"]
"""

# ============================================================================
# .dockerignore
# ============================================================================
DOCKERIGNORE = """
__pycache__/
*.pyc
*.pyo
*.egg-info/
.git/
.gitignore
README.md
*.md
.env
.env.local
venv/
env/
.vscode/
.idea/
*.log
# Ignore large data directories to keep build context light
GENERATED_ENTRIES_MASTER/
ARCHIVES/
.cache/
models/*.bin
*.gguf
.pytest_cache/
dist/
build/
"""

# ============================================================================
# docker-compose.yml - Multi-container orchestration
# ============================================================================
DOCKER_COMPOSE = """
version: '3.8'  # Updated to a more standard recent version

services:
  # Main Opus Maximus application
  opus_maximus:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: opus-maximus-main
    environment:
      - OPUS_DEBUG=false
      - OPUS_LOG_LEVEL=INFO
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      # Mount local directories for persistence and model access
      - ./GENERATED_ENTRIES_MASTER:/app/GENERATED_ENTRIES_MASTER
      - ./OPUS_MAXIMUS_INDIVIDUALIZED:/app/OPUS_MAXIMUS_INDIVIDUALIZED
      - ./models:/app/models
      - ./logs:/app/logs
    ports:
      - "8501:8501" # Dashboard
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    networks:
      - opus_network

  # ChromaDB vector database (Optional, can run embedded)
  chroma:
    image: ghcr.io/chroma-core/chroma:latest
    container_name: opus-chroma
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
    restart: unless-stopped
    networks:
      - opus_network

  # Prometheus for metrics scraping
  prometheus:
    image: prom/prometheus:latest
    container_name: opus-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped
    networks:
      - opus_network

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    container_name: opus-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin  # Change in production
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
    networks:
      - opus_network

volumes:
  chroma_data:
  prometheus_data:
  grafana_data:

networks:
  opus_network:
    driver: bridge
"""