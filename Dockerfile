FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data and logs directories
RUN mkdir -p /data /logs

# Create non-root user for security
RUN useradd -m -u 1000 honeypot && \
    chown -R honeypot:honeypot /app /data /logs

# Switch to non-root user
USER honeypot

# Expose honeypot ports
EXPOSE 2222 8080 2121 2323 2525

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('127.0.0.1', 2222), timeout=5)" || exit 1

# Run honeypot engine
CMD ["python", "-m", "honeypot_engine.engine"]
