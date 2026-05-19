#!/bin/bash

# Build the application container image, preferring Podman over Docker.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

set -e

IMAGE_NAME="${MTV_DL_WEB_IMAGE:-mtv-dl-web:latest}"

if command -v podman >/dev/null 2>&1; then
    CONTAINER_ENGINE="podman"
elif command -v docker >/dev/null 2>&1; then
    CONTAINER_ENGINE="docker"
else
    echo "Neither podman nor docker was found. Please install one of them first."
    exit 1
fi

echo "Using $CONTAINER_ENGINE"
echo "Building $IMAGE_NAME..."
if [ "$CONTAINER_ENGINE" = "podman" ]; then
    "$CONTAINER_ENGINE" build --format docker -t "$IMAGE_NAME" .
else
    "$CONTAINER_ENGINE" build -t "$IMAGE_NAME" .
fi
