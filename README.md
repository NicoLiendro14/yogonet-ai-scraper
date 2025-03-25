# Yogonet News Scraper

A Google Cloud Run job that performs web scraping, data processing, and automated deployment using Python.

## Project Structure

```
.
├── deployment/          # Deployment scripts
│   └── deploy.sh        # Google Cloud Run deployment script
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
└── requirements.txt     # Project dependencies
```

## Features

### 1. Web Scraping with Selenium

The scraper extracts the following information from each Yogonet (https://www.yogonet.com/international/) article:
- **Title**: Main article headline
- **Kicker**: Text above the main headline
- **Image**: Article image URL
- **Link**: URL to the full article

### 2. Data Processing with Pandas

Post-processes the scraped data to calculate the following metrics:
- **Word count** in each title
- **Character count** in each title
- **List of words that start with a capital letter** in each title

### 3. BigQuery Integration

Uploads the processed data to Google BigQuery for further analysis:
- Automatically creates datasets and tables if they don't exist
- Uses Google Cloud service account credentials for authentication
- Handles data type conversion for proper BigQuery storage

### 4. Dockerization

Complete containerization of the application for portable execution:
- Includes Chrome browser installation for headless web scraping
- Environment variable configuration for flexible settings
- Built-in health checks and error handling
- Optimized layer caching for faster builds
- Scripts for building and running the container

## Requirements

- Python 3.8+
- Chrome/Chromium (for local development)
- Docker (for containerization)
- Google Cloud account with BigQuery and Cloud Run permissions

## Setup

### Google Cloud Setup

1. Create a Google Cloud project
2. Create a service account with BigQuery permissions
3. Download the service account key as JSON and save it as `creds.json` in the project root

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
   # Linux/macOS
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   
   # Windows PowerShell
   $env:GOOGLE_CLOUD_PROJECT="your-project-id"
   $env:GOOGLE_APPLICATION_CREDENTIALS="path\to\service-account-key.json"
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

## Environment Variables

The application can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud Project ID | (required) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account credentials | `/app/credentials/service_account.json` |
| `BIGQUERY_DATASET_ID` | BigQuery dataset ID | `yogonet_news` |
| `BIGQUERY_TABLE_ID` | BigQuery table ID | `scraped_articles` |
| `MAX_ARTICLES` | Maximum number of articles to scrape | `10` |
| `HEADLESS` | Whether to run Chrome in headless mode | `true` |
| `CHROME_OPTIONS` | Custom Chrome options | (built-in safe defaults) |

## Output

The script generates the following output files in the `output` directory:
- `scraped_data.json`: Raw scraped data
- `processed_data.csv`: Processed data in CSV format
- `processed_data.json`: Processed data in JSON format

Additionally, the data is stored in BigQuery under the dataset and table specified in the environment variables.

## Next Steps

- Complete deployment script for Cloud Run
