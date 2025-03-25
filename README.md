# Yogonet News Scraper

A Google Cloud Run job that performs web scraping, data processing, and automated deployment using Python.

## Project Structure

```
.
├── deployment/          # Deployment scripts
│   └── deploy.sh        # Google Cloud Run deployment script
├── docker/              # Docker files
│   └── Dockerfile       # Dockerfile for building the image
├── output/              # Output directory (created at runtime)
├── src/                 # Source code
│   ├── database/        # BigQuery integration code
│   ├── processing/      # Data processing code
│   ├── scraper/         # Web scraping code
│   │   └── yogonet_scraper.py  # Yogonet scraper
│   └── main.py          # Main entry point
└── requirements.txt     # Project dependencies
```

## Part 1: Web Scraping with Selenium

The scraper extracts the following information from each Yogonet (https://www.yogonet.com/international/) article:
- **Title**: Main article headline
- **Kicker**: Text above the main headline
- **Image**: Article image URL
- **Link**: URL to the full article

## Requirements

- Python 3.8+
- Chrome/Chromium (for Selenium)
- Docker (for containerization)
- Google Cloud account with BigQuery and Cloud Run permissions

## Usage

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

3. Run the scraper:
   ```
   python src/main.py
   ```

### Docker Execution

```
docker build -t yogonet-scraper -f docker/Dockerfile .
docker run -v $(pwd)/output:/app/output yogonet-scraper
```

## Next Steps

- Implement data post-processing with Pandas
- Implement BigQuery integration
- Complete Dockerfile
- Create Cloud Run deployment script
