# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the FastAPI app runs on
EXPOSE 8001

# Start both applications using a shell command
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port 8001 & python gudangin.py"]