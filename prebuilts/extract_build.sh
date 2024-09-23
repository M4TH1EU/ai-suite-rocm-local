#!/bin/bash

# Set variables
IMAGE_NAME="prebuilts-rocm:6.2"
CONTAINER_NAME="prebuilts-rocm"
FILES_TO_COPY=["/tmp/bitsandbytes/dist/", "/tmp/llama-cpp-python/dist/"]
WHERE_TO_PASTE="./build_output/"

# Run the Docker container
docker run -d --name $CONTAINER_NAME $IMAGE_NAME

# Check if the container is running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Container $CONTAINER_NAME is running."

    # Copy the files from the container to the host
    for file in $FILES_TO_COPY; do
        docker cp $CONTAINER_NAME:$file $WHERE_TO_PASTE
    done

    echo "Files copied to $WHERE_TO_PASTE."
else
    echo "Failed to start container $CONTAINER_NAME."
fi

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME