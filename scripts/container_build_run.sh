#!/bin/bash

# Build the project container image and run it locally.
# Prefers podman; falls back to docker.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_TAG="localhost/mtv_dl_web:local-check"
CONTAINER_NAME="mtv-dl-web-local-check"
RUNTIME=""

if command -v podman >/dev/null 2>&1; then
    RUNTIME="podman"
elif command -v docker >/dev/null 2>&1; then
    RUNTIME="docker"
else
    echo "Error: neither podman nor docker is installed."
    exit 1
fi

cleanup() {
    set +e
    echo
    echo "Stopping container ${CONTAINER_NAME}..."
    "$RUNTIME" rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM

echo "Using container runtime: ${RUNTIME}"
echo "Building image ${IMAGE_TAG} from ${ROOT_DIR}..."

if [ "$RUNTIME" = "docker" ]; then
    docker build -t "$IMAGE_TAG" "$ROOT_DIR"
else
    podman build -t "$IMAGE_TAG" "$ROOT_DIR"
fi

echo "Starting container ${CONTAINER_NAME}..."
if ! "$RUNTIME" run -d --name "$CONTAINER_NAME" -p 8000:8000 "$IMAGE_TAG" >/dev/null; then
    echo "Error: failed to start container ${CONTAINER_NAME}."
    exit 1
fi

sleep 2
if [ "$("$RUNTIME" inspect -f '{{.State.Running}}' "$CONTAINER_NAME" 2>/dev/null || true)" != "true" ]; then
    echo "Error: container did not stay running."
    "$RUNTIME" logs "$CONTAINER_NAME" || true
    exit 1
fi

echo "Container is running. Streaming logs (CTRL-C to stop and remove container)."
"$RUNTIME" logs -f "$CONTAINER_NAME"
