#!/bin/bash

# Set variables
IMAGE_NAME="bitsandbytes-rocm-build:6.1.2"
CONTAINER_NAME="bitsandbytes-rocm-build"
FILE_IN_CONTAINER="/tmp/bitsandbytes/dist/"
FILE_ON_HOST="./build_output/"

# Run the Docker container
docker run -d --name $CONTAINER_NAME $IMAGE_NAME

# Check if the container is running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Container $CONTAINER_NAME is running."

    # Copy the file from the container to the host
    docker cp $CONTAINER_NAME:$FILE_IN_CONTAINER $FILE_ON_HOST

    if [ $? -eq 0 ]; then
        echo "File copied successfully to $FILE_ON_HOST"
    else
        echo "Failed to copy file."
    fi
else
    echo "Failed to start container $CONTAINER_NAME."
fi

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

echo "Now you can install bitsandbytes locally using \"pip install\" with the file in the build_output/ folder"
