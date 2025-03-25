#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

IMAGE_NAME="yogonet-scraper"
VERSION=$(date +"%Y%m%d-%H%M%S")

source "${PROJECT_DIR}/.env" 2>/dev/null || true

GCP_PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"nice-storm-454804-h9"}
GCP_PROJECT_ID=$(echo "$GCP_PROJECT_ID" | tr -d '\r\n ')
MAX_ARTICLES=${MAX_ARTICLES:-10}
MAX_ARTICLES=$(echo "$MAX_ARTICLES" | tr -d '\r\n ')

echo "======== Yogonet Scraper Local Deployment ========"
echo "GCP Project ID: ${GCP_PROJECT_ID}"
echo "Version: ${VERSION}"

LOCAL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"
echo "Image: ${LOCAL_IMAGE_NAME}"

echo "======== Building Docker Image ========"
cd "${PROJECT_DIR}"
docker build -t "${LOCAL_IMAGE_NAME}" -f docker/Dockerfile .

echo "======== Running Job Locally ========"
echo "Starting the scraper locally with Docker..."

mkdir -p "${PROJECT_DIR}/output"

docker run --rm \
  -v "${PROJECT_DIR}/output:/app/output" \
  -v "${PROJECT_DIR}/creds.json:/app/credentials/service_account.json" \
  -e GOOGLE_CLOUD_PROJECT="${GCP_PROJECT_ID}" \
  -e MAX_ARTICLES="${MAX_ARTICLES}" \
  "${LOCAL_IMAGE_NAME}"

echo "======== Job Completed Locally ========"
echo "Check the output directory for results:"
ls -la "${PROJECT_DIR}/output/" 