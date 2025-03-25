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

## Output

The script generates the following output files in the `output` directory:
- `scraped_data.json`: Raw scraped data
- `processed_data.csv`: Processed data in CSV format
- `processed_data.json`: Processed data in JSON format

## Next Steps

- Implement BigQuery integration
- Complete deployment script for Cloud Run
