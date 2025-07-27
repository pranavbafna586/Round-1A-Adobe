# PDF Outline Extractor Docker Configuration
#
# This Dockerfile creates a containerized environment for running the PDF outline
# extraction tool. It provides a consistent, portable execution environment that
# includes all necessary dependencies and proper file system mappings.
#
# The container is built on Python 3.10 slim image for optimal size and performance.
# It supports volume mounting for input/output directories to facilitate file processing.
#
# Build command:
#   docker build -t pdf_extractor .
#
# Run command:
#   docker run -v %cd%/input:/app/input -v %cd%/output:/app/output pdf_extractor

# Use Python 3.10 slim base image for Linux AMD64 architecture
# This ensures compatibility and optimal performance across different platforms
FROM --platform=linux/amd64 python:3.10-slim

# Set the working directory inside the container
# All subsequent commands will be executed from this directory
WORKDIR /app

# Copy all project files into the container
# This includes source code, configuration files, and directory structure
COPY . .

# Install Python dependencies from requirements.txt
# --no-cache-dir flag reduces image size by not storing package cache
RUN pip install --no-cache-dir -r requirements.txt

# Define the default command to execute when container starts
# This runs the main PDF processing script
CMD ["python", "main.py"]
