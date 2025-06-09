# Use an official lightweight Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY telnet_server.py .

# Make port 2323 available to the world outside this container
EXPOSE 23

# Run telnet_server.py when the container launches
# -u flag ensures that prints and logs are sent directly to stdout/stderr without buffering
CMD ["python", "-u", "telnet_server.py"]
