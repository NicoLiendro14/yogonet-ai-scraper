FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN mkdir -p /app/output /app/credentials

ENV PYTHONUNBUFFERED=1
ENV MAX_ARTICLES=10
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/service_account.json"
ENV BIGQUERY_DATASET_ID="yogonet_news"
ENV BIGQUERY_TABLE_ID="scraped_articles"

CMD ["python", "src/main.py"]
