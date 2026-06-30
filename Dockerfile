# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install uv

# Copy project files for building
COPY pyproject.toml .
COPY src/ ./src/

# Install dependencies into a temporary directory
ENV UV_HTTP_TIMEOUT=600
ENV UV_EXTRA_INDEX_URL="https://download.pytorch.org/whl/cpu"
RUN uv pip install --system --target=/install --index-strategy unsafe-best-match -e .
RUN uv pip install --system --target=/install --index-strategy unsafe-best-match fastapi uvicorn python-multipart prometheus-fastapi-instrumentator

# Stage 2: Hugging Face Spaces Runtime
FROM python:3.13-slim

# Hugging Face strictly requires a user with UID 1000
RUN useradd -m -u 1000 user

WORKDIR /app

# Copy installed dependencies from the builder
COPY --from=builder /install /usr/local/lib/python3.13/site-packages
COPY --from=builder /install/bin /usr/local/bin

# Copy application files and grant ownership to HF user
COPY --chown=user pyproject.toml .
COPY --chown=user src/ ./src/
COPY --chown=user configs/ ./configs/
COPY --chown=user artifacts/ ./artifacts/
COPY --chown=user feature_cache/ ./feature_cache/

# Switch to the required HF user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose HF default port
EXPOSE 7860

# Run API on Port 7860 required by Hugging Face Spaces
CMD ["uvicorn", "hiremind.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
