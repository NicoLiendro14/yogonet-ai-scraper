#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

IMAGE_NAME="yogonet-scraper"
TAG="latest"
CREDENTIALS_PATH="${PROJECT_DIR}/creds.json"
OUTPUT_DIR="${PROJECT_DIR}/output"

echo "===== Yogonet News Scraper Docker Build & Run ====="
echo "Project directory: $PROJECT_DIR"
echo "Credentials path: $CREDENTIALS_PATH"
echo "Output directory: $OUTPUT_DIR"

if [ ! -f "$CREDENTIALS_PATH" ]; then
    echo "Error: Google Cloud credentials file not found at $CREDENTIALS_PATH"
    echo "Please place your credentials file at the specified location or update the script."
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo -e "\n===== Building Docker Image ====="
docker build -t "${IMAGE_NAME}:${TAG}" -f "${SCRIPT_DIR}/Dockerfile" "$PROJECT_DIR"

if [ $? -ne 0 ]; then
    echo "Error: Docker build failed."
    exit 1
fi

echo -e "\n===== Docker Image Built Successfully ====="
echo "Image: ${IMAGE_NAME}:${TAG}"

echo -e "\n===== Running Docker Container ====="
docker run -it --rm \
    -v "${OUTPUT_DIR}:/app/output" \
    -v "${CREDENTIALS_PATH}:/app/credentials/service_account.json" \
    -e GOOGLE_CLOUD_PROJECT="$(grep -o '"project_id": "[^"]*' "$CREDENTIALS_PATH" | cut -d'"' -f4)" \
    "${IMAGE_NAME}:${TAG}"

echo -e "\n===== Container Execution Complete ====="
echo "Check the output directory for results: $OUTPUT_DIR" 