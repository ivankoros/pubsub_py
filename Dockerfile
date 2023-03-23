# Set the base image to use for subsequent instructions
FROM python:3.9-slim-buster

# Set the working directory for the application
WORKDIR /app

# Copy the Python requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Set environment variables for the app
ENV PYTHONUNBUFFERED=1

# Set the command to run the app
CMD ["python", "main.py"]
