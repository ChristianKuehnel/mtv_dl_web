FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency metadata and lock file for deterministic sync
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Create directories for mounted volumes
RUN mkdir -p /data /downloads /config && \
    chown -R appuser:appuser /app /data /downloads /config

# Expose port
EXPOSE 8000

USER appuser

# Run the application with proper module path
CMD ["uvicorn", "mtv_dl_web.main:app", "--host", "0.0.0.0", "--port", "8000"]
