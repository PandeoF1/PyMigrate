# Use the official Python base image
FROM python:3.9-slim-buster

# Update the package list and install SSHFS and NFS client tools
RUN apt-get update && \
    apt-get install -y sshfs nfs-common screen inetutils-ping curl netcat && \
    apt-get clean

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]
