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

# Copy application files
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Note: Environment variables will be provided by Render.com at runtime
# No need to copy .env.docker since Render injects env vars directly

# Expose FastAPI port (HF Spaces uses 7860 by default)
EXPOSE 7860

# Environment variables (override at runtime)
ENV PYTHONUNBUFFERED=1 \
    PORT=7860

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:7860/', timeout=5)" || exit 1

# Run uvicorn server using startup script
CMD ["./start.sh"]
