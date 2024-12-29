# Use Python base image as the foundation
FROM python:3.10-slim

# Install system dependencies (like 'top' and git)
RUN apt-get update -yq && apt-get upgrade -yq && \
    apt-get install -y git procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PIP_DISABLE_VERSION_CHECK=1

# Copy Python requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --compile --no-cache-dir

# Copy application files and set the Python path
COPY . app
ENV PYTHONPATH /app

# Expose port for the Python app
EXPOSE 8056

# Set default entrypoint to run the Python app
ENTRYPOINT ["python", "app/app/main.py"]