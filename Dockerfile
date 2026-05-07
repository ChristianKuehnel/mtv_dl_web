FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set PATH to include uv
ENV PATH="/root/.cargo/bin:$PATH"

# Copy pyproject.toml for dependency resolution
COPY pyproject.toml .

# Install dependencies with uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["uvicorn", "src/main:app", "--host", "0.0.0.0", "--port", "8000"]