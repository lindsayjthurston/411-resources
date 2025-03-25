#!/bin/bash

# Variables
IMAGE_NAME="my_boxing_app"
CONTAINER_TAG="latest"
HOST_PORT=5001
CONTAINER_PORT=5000
DB_VOLUME_PATH="$(pwd)/db"
BUILD=true

# Check if we need to build the Docker image
if [ "$BUILD" = true ]; then
  echo "Building Docker image..."
  docker build -t ${IMAGE_NAME}:${CONTAINER_TAG} -f Dockerfile .
else
  echo "Skipping Docker image build..."
fi

# Check if the database directory exists; if not, create it
if [ ! -d "${DB_VOLUME_PATH}" ]; then
  echo "Creating database directory at ${DB_VOLUME_PATH}..."
  mkdir -p "${DB_VOLUME_PATH}"
fi

# Stop and remove the running container if it exists
if [ "$(docker ps -q -a -f name=${IMAGE_NAME}_container)" ]; then
    echo "Stopping running container: ${IMAGE_NAME}_container"
    docker stop ${IMAGE_NAME}_container

    # Check if the stop was successful
    if [ $? -eq 0 ]; then
        echo "Removing container: ${IMAGE_NAME}_container"
        docker rm ${IMAGE_NAME}_container
    else
        echo "Failed to stop container: ${IMAGE_NAME}_container"
        exit 1
    fi
else
    echo "No running container named ${IMAGE_NAME}_container found."
fi

# Run the Docker container with the necessary ports and volume mappings
echo "Running Docker container..."
docker run -d \
    --name ${IMAGE_NAME}_container \
    -p ${HOST_PORT}:${CONTAINER_PORT} \
    -v ${DB_VOLUME_PATH}:/app/db \
    ${IMAGE_NAME}:${CONTAINER_TAG}

if [ $? -eq 0 ]; then
    echo "Docker container is running on port ${HOST_PORT}."
else
    echo "Failed to start the Docker container."
    exit 1
fi

echo "Docker container is running on port ${HOST_PORT}."
