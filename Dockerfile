# Use the official Ubuntu base image
FROM alpine:latest

# Install system dependencies
RUN apk update && apk add python3 \
    py3-pip \
    nano \
    gcc \
    python3-dev \
    build-base \
    linux-headers


# Set the working directory
WORKDIR /vController

# Copy the Python file to the working directory
COPY ./vController.py .

# Install Python dependencies
RUN pip install datetime paho-mqtt argparse continuous-threading