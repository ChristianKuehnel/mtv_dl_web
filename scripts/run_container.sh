#!/bin/bash

# Build and run the application container, preferring Podman over Docker.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

set -e

IMAGE_NAME="${MTV_DL_WEB_IMAGE:-mtv-dl-web:latest}"
CONTAINER_NAME="${MTV_DL_WEB_CONTAINER:-mtv-dl-web}"
HOST_BIND_ADDRESS="${MTV_DL_WEB_BIND_ADDRESS:-0.0.0.0}"
HOST_PORT="${MTV_DL_WEB_PORT:-8071}"
CONFIG_DIR="${MTV_DL_WEB_CONFIG_DIR:-$PWD/config}"
DOWNLOADS_DIR="${MTV_DL_WEB_DOWNLOADS_DIR:-$PWD/Downloads}"
DATABASE_DIR="${MTV_DL_WEB_DATABASE_DIR:-$PWD/mtv_dl_db}"

if command -v podman >/dev/null 2>&1; then
    CONTAINER_ENGINE="podman"
elif command -v docker >/dev/null 2>&1; then
    CONTAINER_ENGINE="docker"
else
    echo "Neither podman nor docker was found. Please install one of them first."
    exit 1
fi

mkdir -p "$CONFIG_DIR" "$DOWNLOADS_DIR" "$DATABASE_DIR"

"$SCRIPT_DIR/build_container_image.sh"

if "$CONTAINER_ENGINE" ps -a --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"; then
    echo "Removing existing container $CONTAINER_NAME..."
    "$CONTAINER_ENGINE" rm -f "$CONTAINER_NAME" >/dev/null
fi

echo "Starting $CONTAINER_NAME on $HOST_BIND_ADDRESS:$HOST_PORT"
"$CONTAINER_ENGINE" run --rm \
    --name "$CONTAINER_NAME" \
    -p "$HOST_BIND_ADDRESS:$HOST_PORT:8071" \
    -v "$CONFIG_DIR:/config" \
    -v "$DOWNLOADS_DIR:/downloads" \
    -v "$DATABASE_DIR:/database" \
    "$IMAGE_NAME"
