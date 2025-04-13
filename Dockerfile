# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for image processing later)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create the uploads directory within the container image if it doesn't exist
# Although app.py creates it, this ensures it's present in the image layer
RUN mkdir -p /app/uploads

# Expose the port Gunicorn will run on
EXPOSE 8080

# Define the command to run the application using Gunicorn
# Use 0.0.0.0 to accept connections from outside the container
# The number of workers (-w 4) is a starting point, adjust based on load/instance size
# Cloud Run automatically provides the PORT environment variable, Gunicorn uses it by default
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]