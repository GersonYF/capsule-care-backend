FROM python:3.10-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y postgresql redis-server supervisor && \
    apt-get clean

# Create directories
RUN mkdir -p /var/log/supervisor

# Set up work directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV POSTGRES_USER=appuser
ENV POSTGRES_PASSWORD=apppassword
ENV POSTGRES_DB=appdb

# Copy Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports
EXPOSE 8000

# Start Supervisor
CMD ["/usr/bin/supervisord"]

