FROM python:3.10-slim


RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN google-chrome --version

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip list | grep -E "selenium|pandas|pyarrow|google-cloud-bigquery"

COPY src/ ./src/

RUN mkdir -p /app/output /app/credentials


ENV PYTHONUNBUFFERED=1
ENV MAX_ARTICLES=10
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/service_account.json"
ENV BIGQUERY_DATASET_ID="yogonet_news"
ENV BIGQUERY_TABLE_ID="scraped_articles"
ENV PYTHONDONTWRITEBYTECODE=1
ENV HEADLESS=true

ENV CHROME_OPTIONS="--no-sandbox --disable-dev-shm-usage --disable-gpu --headless"

# Set user to non-root for security (optional - comment out if causing issues)
# RUN groupadd -r scraper && useradd -r -g scraper scraper
# RUN chown -R scraper:scraper /app
# USER scraper

HEALTHCHECK --interval=5m --timeout=30s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

CMD ["python", "src/main.py"]
