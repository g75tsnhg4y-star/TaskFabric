# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy our Python scripts into the container
COPY . /app

# Install the required dependencies
RUN pip install --no-cache-dir fastapi uvicorn redis pydantic