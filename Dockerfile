# Set the base image to use for subsequent instructions
FROM python:3.9

ADD . .

# Copy the Python requirements file to the container
COPY ./requirements.txt /code/requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Set environment variables for the app
ENV PYTHONUNBUFFERED=1

# Set the command to run the app
CMD ["python", "main.py"]
