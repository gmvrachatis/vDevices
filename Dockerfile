# Use the official Ubuntu base image
FROM alpine:latest

# Install system dependencies
RUN apk update && apk add python3 \
    py3-pip \
    python3-dev \
    nano \
    gcc \
    build-base \
    linux-headers


# Set the working directory
WORKDIR /vThermostat

# Copy the Python file to the working directory
COPY ./vThermostat.py .


# Install Python dependencies
RUN pip install datetime paho-mqtt argparse continuous-threading