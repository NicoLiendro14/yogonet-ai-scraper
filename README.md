# Yogonet News Scraper

A Google Cloud Run job that performs web scraping, data processing, and automated deployment using Python.

## Project Structure

```
.
├── deployment/          # Deployment scripts
│   └── deploy.sh        # Script for Google Cloud Run deployment
├── docker/              # Docker files
│   ├── Dockerfile       # Dockerfile for building the image
│   ├── build-and-run.sh # Bash script to build and run the Docker container
│   └── build-and-run.ps1 # PowerShell script to build and run the Docker container
├── output/              # Output directory (created at runtime)
├── src/                 # Source code
│   ├── database/        # BigQuery integration code
│   │   └── bigquery_client.py  # BigQuery client
│   ├── processing/      # Data processing code
│   │   └── data_processor.py  # Data processing with Pandas
│   ├── scraper/         # Web scraping code
│   │   └── yogonet_scraper.py  # Yogonet scraper
│   └── main.py          # Main entry point
├── .env.example         # Example environment variables file
└── requirements.txt     # Project dependencies
```

## Features

### 1. Web Scraping with Selenium

The scraper extracts the following information from each Yogonet (https://www.yogonet.com/international/) article:
- **Title**: Main article headline
- **Kicker**: Text above the main headline
- **Image**: Article image URL
- **Link**: URL to the full article

### 3. Data Processing with Pandas

Post-processes the scraped data to calculate the following metrics:
- **Word count** in each title
- **Character count** in each title
- **List of words that start with a capital letter** in each title

### 4. BigQuery Integration

Uploads the processed data to Google BigQuery for further analysis:
- Automatically creates datasets and tables if they don't exist
- Uses Google Cloud service account credentials for authentication
- Handles data type conversion for proper BigQuery storage

### 5. Dockerization

Complete containerization of the application for portable execution:
- Includes Chrome browser installation for headless web scraping
- Environment variable configuration for flexible settings
- Built-in health checks and error handling
- Optimized layer caching for faster builds
- Scripts for building and running the container

### 6. Deployment Automation

Automated deployment to Google Cloud Run:
- Single script for the entire deployment process
- Builds and tags Docker image
- Uploads image to Google Artifact Registry
- Creates or updates Cloud Run Job
- Configures environment variables and secrets
- Executes the job immediately after deployment

## Requirements

- Python 3.8+
- Chrome/Chromium (for local development)
- Docker (for containerization)
- Google Cloud account with BigQuery and Cloud Run permissions
- Google Cloud SDK (gcloud) for deployment

## Setup

### Google Cloud Setup

1. Create a Google Cloud project
2. Create a service account with BigQuery permissions
3. Download the service account key as JSON and save it as `creds.json` in the project root
4. Enable required APIs:
   ```bash
   gcloud services enable artifactregistry.googleapis.com \
       run.googleapis.com \
       secretmanager.googleapis.com \
       bigquery.googleapis.com
   ```

### Local Setup

1. Clone the repository:
   ```
   git clone <REPOSITORY_URL>
   cd yogonet-scraper
   ```

2. Set up environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```
   # Create .env file from example
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Run the scraper:
   ```
   python src/main.py
   ```

## Docker Execution

### Using the Convenience Scripts

#### On Linux/macOS:
```bash
# Make the script executable
chmod +x docker/build-and-run.sh

# Run the script
./docker/build-and-run.sh
```

#### On Windows (PowerShell):
```powershell
# Run the script
.\docker\build-and-run.ps1
```

### Manual Docker Commands

#### Building the Docker Image

```bash
# From the project root directory
docker build -t yogonet-scraper -f docker/Dockerfile .
```

#### Running the Container

##### On Linux/macOS:
```bash
docker run -it --rm \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/creds.json:/app/credentials/service_account.json" \
  -e GOOGLE_CLOUD_PROJECT="your-project-id" \
  yogonet-scraper
```

##### On Windows (CMD/PowerShell):
```powershell
docker run -it --rm ^
  -v "%cd%\output:/app/output" ^
  -v "%cd%\creds.json:/app/credentials/service_account.json" ^
  -e GOOGLE_CLOUD_PROJECT="your-project-id" ^
  yogonet-scraper
```

##### On Windows (Git Bash/MINGW64):
```bash
# This command works in Git Bash environment
docker run -it --rm \
  -v "C:/Users/YourUsername/path/to/project/output:/app/output" \
  -v "C:/Users/YourUsername/path/to/project/creds.json:/app/credentials/service_account.json" \
  -e GOOGLE_CLOUD_PROJECT="your-project-id" \
  yogonet-scraper
```

Example with actual paths:
```bash
docker run -it --rm \
  -v "C:/Users/Nicolas/Downloads/pipol/output:/app/output" \
  -v "C:/Users/Nicolas/Downloads/pipol/creds.json:/app/credentials/service_account.json" \
  -e GOOGLE_CLOUD_PROJECT="nice-storm-454804-h9" \
  yogonet-scraper
```

> **Note for Windows users**: When using Docker in Windows environments, especially with MINGW64 (Git Bash), use absolute Windows-style paths with forward slashes as shown above.

## Cloud Deployment

### Deploying to Google Cloud Run

The project includes a deployment script that automates the entire process:

```bash
# Make the script executable (Linux/macOS)
chmod +x deployment/deploy.sh

# Run the deployment script
./deployment/deploy.sh
```

This script will:
1. Build the Docker image
2. Tag it for Google Artifact Registry
3. Push the image to the registry
4. Create a secret in Secret Manager for credentials
5. Deploy the image as a Cloud Run job
6. Execute the job immediately

### GCP Configuration for Cloud Deployment

Before running the `deploy.sh` script, you need to configure your Google Cloud environment correctly:

1. **Install and initialize Google Cloud SDK (gcloud):**
   ```bash
   # Download and install gcloud SDK from https://cloud.google.com/sdk/docs/install
   
   # Initialize gcloud and login
   gcloud init
   gcloud auth login
   ```

2. **Set the active project:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable required APIs:**
   ```bash
   gcloud services enable artifactregistry.googleapis.com \
       run.googleapis.com \
       secretmanager.googleapis.com \
       bigquery.googleapis.com
   ```

4. **Create a service account and grant required permissions:**
   ```bash
   # Create service account
   gcloud iam service-accounts create yogonet-scraper-sa \
       --display-name="Yogonet Scraper Service Account"
   
   # Grant required roles
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:yogonet-scraper-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/bigquery.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:yogonet-scraper-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/artifactregistry.writer"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:yogonet-scraper-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/run.admin"
   ```

5. **Create and download service account key:**
   ```bash
   # Create and download key
   gcloud iam service-accounts keys create creds.json \
       --iam-account=yogonet-scraper-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

6. **Configure Docker for Artifact Registry authentication:**
   ```bash
   # Configure Docker to use gcloud as a credential helper
   gcloud auth configure-docker REGION-docker.pkg.dev
   ```

7. **Create Artifact Registry repository:**
   ```bash
   # Create repository
   gcloud artifacts repositories create yogonet-scraper \
       --repository-format=docker \
       --location=REGION \
       --description="Yogonet Scraper Docker images"
   ```

After completing these steps, you can run the `deploy.sh` script to deploy the application to Cloud Run.

### Local Deployment with Docker

For development or testing purposes, you can use the `deploy_local.sh` script to run the application locally using Docker:

```bash
# Make the script executable (Linux/macOS)
chmod +x deployment/deploy_local.sh

# Run the script
./deployment/deploy_local.sh
```

On Windows (using Git Bash, WSL, or similar):
```bash
# Run the script
bash deployment/deploy_local.sh
```

This script will:
1. Build the Docker image locally with a timestamp-based tag
2. Run the container with the appropriate volume mounts for output and credentials
3. Display the results from the output directory

#### Prerequisites for Local Deployment

Before running the `deploy_local.sh` script:

1. **Install Docker** on your local machine
   - [Docker Desktop for Windows/Mac](https://www.docker.com/products/docker-desktop)
   - [Docker Engine for Linux](https://docs.docker.com/engine/install/)

2. **Create a service account key file** (if connecting to BigQuery):
   - Save the service account key as `creds.json` in the project root directory
   - This file should have permissions to access BigQuery in your GCP project

3. **Create a .env file** (optional) with the following variables:
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   MAX_ARTICLES=10      # Number of articles to scrape
   ```

The `deploy_local.sh` script works without modifying any Google Cloud resources and is ideal for development, testing, or running the scraper in environments without Google Cloud access.

### Environment Configuration

You can customize the deployment by setting variables in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | (from gcloud config) |
| `CLOUD_RUN_REGION` | GCP Region for deployment | `us-central1` |
| `CLOUD_RUN_SERVICE_NAME` | Name of the Cloud Run job | `yogonet-scraper-job` |
| `ARTIFACT_REGISTRY_REPO` | Artifact Registry repository path | auto-generated |
| `GCP_CREDENTIALS_SECRET_NAME` | Name for Secret Manager credentials | `yogonet-scraper-credentials` |
| `MAX_ARTICLES` | Maximum articles to scrape | `10` |
| `MEMORY_LIMIT` | Memory limit for the Cloud Run job | `1Gi` |
| `CPU_LIMIT` | CPU limit for the Cloud Run job | `1` |
| `TIMEOUT` | Maximum job execution time | `600s` |

## Output

The script generates the following output files in the `output` directory:
- `scraped_data.json`: Raw scraped data
- `processed_data.csv`: Processed data in CSV format
- `processed_data.json`: Processed data in JSON format

Additionally, the data is stored in BigQuery under the dataset and table specified in the environment variables.

## AI-Assisted Dynamic Scraping

The project now includes an optional AI-assisted scraper that uses OpenAI's API to dynamically identify page elements, making it resilient to site layout changes.

### How It Works

1. **HTML Analysis**: The scraper sends a sample of the page's HTML structure to OpenAI's API.
2. **Intelligent Selector Detection**: The AI model analyzes the HTML and determines the most appropriate CSS selectors for articles, titles, kickers, images, and links.
3. **Dynamic Extraction**: Instead of hardcoded selectors, the scraper uses the AI-identified selectors to extract data.
4. **Fallback Mechanism**: If AI identification fails, the scraper falls back to predefined selectors.

### Using the AI Scraper

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```
   Or add it to your `.env` file:
   ```
   OPENAI_API_KEY=your-openai-api-key
   ```

2. Run the AI-assisted version:
   ```bash
   python src/ai_main.py
   ```

3. Optional parameters:
   ```bash
   python src/ai_main.py --max-articles 20 --url "https://www.yogonet.com/international/"
   ```