# Dockerfile for persistent cloud deployment of TDS Quiz Solver
# Base image includes Playwright browsers (Chromium) already installed.
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set workdir
WORKDIR /app

# Copy dependency file first for layer caching
COPY requirements.txt ./

# Install Python dependencies (no cache to reduce layer size)
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

# Copy application source
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Environment variables (override at runtime)
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Health check (optional for some platforms)
# HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
#   CMD curl -f http://localhost:8000/ || exit 1

# Run uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
