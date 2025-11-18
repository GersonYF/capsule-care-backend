# Base image
FROM python:3.11-slim

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql \
    redis-server \
    supervisor \
    && apt-get clean

# Create a non-root user
RUN useradd -m appuser

# Create working directory
WORKDIR /app

# Copy app code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# Supervisor logs
RUN mkdir -p /var/log/supervisor

# Expose port for Flask
EXPOSE 8000

# Switch user
USER appuser

# Run supervisor
CMD ["/usr/bin/supervisord", "-c", "/supervisord.conf"]
