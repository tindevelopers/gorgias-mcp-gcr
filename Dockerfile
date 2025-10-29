FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create startup script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Create a non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose port for HTTP healthcheck
EXPOSE 3000

# Set environment variables
ENV PORT=3000
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Use the startup script as entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
