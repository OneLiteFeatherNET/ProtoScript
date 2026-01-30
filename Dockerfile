# Use a Python base image
FROM python:3.13-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# Note: This will install torch with ROCm support as specified in pyproject.toml
RUN uv sync --frozen --no-dev

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8008

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8008", "ProtoScript.wsgi:application"]
