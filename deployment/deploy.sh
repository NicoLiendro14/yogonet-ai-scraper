#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

IMAGE_NAME="yogonet-scraper"
VERSION=$(date +"%Y%m%d-%H%M%S")

source "${PROJECT_DIR}/.env" 2>/dev/null || true

GCP_PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null)}
GCP_PROJECT_ID=$(echo "$GCP_PROJECT_ID" | tr -d '\r\n ')
REGION=${CLOUD_RUN_REGION:-"us-central1"}
REGION=$(echo "$REGION" | tr -d '\r\n ')
ARTIFACT_REGISTRY=${ARTIFACT_REGISTRY_REPO:-"${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/scraper-repo"}
ARTIFACT_REGISTRY=$(echo "$ARTIFACT_REGISTRY" | tr -d '\r\n ')
SERVICE_NAME=${CLOUD_RUN_SERVICE_NAME:-"yogonet-scraper-job"}
SERVICE_NAME=$(echo "$SERVICE_NAME" | tr -d '\r\n ')
CREDENTIALS_SECRET_NAME=${GCP_CREDENTIALS_SECRET_NAME:-"yogonet-scraper-credentials"}
CREDENTIALS_SECRET_NAME=$(echo "$CREDENTIALS_SECRET_NAME" | tr -d '\r\n ')
MAX_ARTICLES=${MAX_ARTICLES:-10}
MAX_ARTICLES=$(echo "$MAX_ARTICLES" | tr -d '\r\n ')
MEMORY_LIMIT=${MEMORY_LIMIT:-"1Gi"}
MEMORY_LIMIT=$(echo "$MEMORY_LIMIT" | tr -d '\r\n ')
CPU_LIMIT=${CPU_LIMIT:-"1"}
CPU_LIMIT=$(echo "$CPU_LIMIT" | tr -d '\r\n ')
TIMEOUT=${TIMEOUT:-"600s"}
TIMEOUT=$(echo "$TIMEOUT" | tr -d '\r\n ')

echo "======== Yogonet Scraper Deployment ========"
echo "GCP Project ID: ${GCP_PROJECT_ID}"
echo "Region: ${REGION}"
echo "Artifact Registry: ${ARTIFACT_REGISTRY}"
echo "Service Name: ${SERVICE_NAME}"
echo "Version: ${VERSION}"

if [ -z "${GCP_PROJECT_ID}" ]; then
  echo "Error: GCP_PROJECT_ID is not set"
  echo "Please set GOOGLE_CLOUD_PROJECT in your .env file or via gcloud config"
  exit 1
fi

IMAGE_URL="${ARTIFACT_REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo "Image URL: ${IMAGE_URL}"

echo "======== Building Docker Image ========"
cd "${PROJECT_DIR}"
docker build -t "${IMAGE_NAME}:${VERSION}" -f docker/Dockerfile .

echo "======== Tagging Image for Artifact Registry ========"
docker tag "${IMAGE_NAME}:${VERSION}" "${IMAGE_URL}"

echo "======== Authenticating with GCP ========"
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

echo "======== Enabling Required APIs ========"
gcloud services enable artifactregistry.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    --project="${GCP_PROJECT_ID}" \
    --quiet

echo "======== Creating Artifact Registry Repository (if it doesn't exist) ========"
gcloud artifacts repositories create scraper-repo \
  --project="${GCP_PROJECT_ID}" \
  --repository-format=docker \
  --location=${REGION} \
  --description="Repository for Yogonet Scraper" \
  --quiet || true

echo "======== Pushing Image to Artifact Registry ========"
docker push "${IMAGE_URL}"

echo "======== Creating Secret for GCP Credentials (if it doesn't exist) ========"
if [ -f "${PROJECT_DIR}/creds.json" ]; then
  gcloud secrets create ${CREDENTIALS_SECRET_NAME} \
    --project="${GCP_PROJECT_ID}" \
    --replication-policy="automatic" \
    --data-file="${PROJECT_DIR}/creds.json" \
    --quiet || true
else
  echo "Warning: creds.json not found at ${PROJECT_DIR}/creds.json"
  echo "Make sure you have a secret named ${CREDENTIALS_SECRET_NAME} in GCP Secret Manager"
fi

echo "======== Deploying Job to Cloud Run ========"
gcloud run jobs create ${SERVICE_NAME} \
  --project="${GCP_PROJECT_ID}" \
  --image=${IMAGE_URL} \
  --region=${REGION} \
  --set-secrets="/app/credentials/service_account.json=${CREDENTIALS_SECRET_NAME}:latest" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${GCP_PROJECT_ID}" \
  --set-env-vars="MAX_ARTICLES=${MAX_ARTICLES}" \
  --memory=${MEMORY_LIMIT} \
  --cpu=${CPU_LIMIT} \
  --task-timeout=${TIMEOUT} \
  --max-retries=3 \
  --execute-now \
  --wait \
  --quiet || \
gcloud run jobs update ${SERVICE_NAME} \
  --project="${GCP_PROJECT_ID}" \
  --image=${IMAGE_URL} \
  --region=${REGION} \
  --set-secrets="/app/credentials/service_account.json=${CREDENTIALS_SECRET_NAME}:latest" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${GCP_PROJECT_ID}" \
  --set-env-vars="MAX_ARTICLES=${MAX_ARTICLES}" \
  --memory=${MEMORY_LIMIT} \
  --cpu=${CPU_LIMIT} \
  --task-timeout=${TIMEOUT} \
  --max-retries=3 \
  --execute-now \
  --wait \
  --quiet

echo "======== Deployment Complete ========"
echo "Job URL: https://console.cloud.google.com/run/jobs/details/${REGION}/${SERVICE_NAME}/executions?project=${GCP_PROJECT_ID}"
