#!/usr/bin/env python3
"""
AI-assisted version of the Yogonet scraper
Uses OpenAI API to dynamically identify page elements
"""

import logging
import os
import json
import argparse
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import openai

from processing.data_processor import DataProcessor
from database.bigquery_client import BigQueryClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIYogonetScraper:
    """
    Yogonet scraper that uses OpenAI API to dynamically identify page elements
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI-assisted scraper
        
        Args:
            api_key (str, optional): OpenAI API key. If None, will try to get from env var.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        
        chrome_options = Options()
        chrome_options_env = os.environ.get("CHROME_OPTIONS", "")
        if chrome_options_env:
            options_list = chrome_options_env.split()
            for option in options_list:
                chrome_options.add_argument(option)
                logger.info(f"Added Chrome option: {option}")
        else:
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--headless")
        
        logger.info(f"Using Chrome options from environment: {chrome_options_env}")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized with ChromeDriverManager")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            raise
    
    def __del__(self):
        """Close the WebDriver when the object is destroyed"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("Scraper closed")
    
    def identify_elements_with_ai(self, html_content: str) -> Dict[str, str]:
        """
        Use OpenAI API to identify the relevant selectors in the HTML
        
        Args:
            html_content (str): HTML content of the page
            
        Returns:
            Dict[str, str]: Dictionary with selectors for article, title, kicker, image, link
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        simplified_html = str(soup.body)[:10000]
        
        prompt = f"""
        You are an expert web scraper. Analyze this HTML from yogonet.com and identify CSS selectors for the following elements:
        
        1. Article container: The div or element that contains each news article
        2. Title: The title or headline of each article
        3. Kicker: The text above the main headline (might be a category or short summary)
        4. Image: The main image of the article
        5. Link: The URL to the full article
        
        Format your response as JSON with keys: "article_selector", "title_selector", "kicker_selector", "image_selector", "link_selector"
        
        Here's the sample HTML:
        {simplified_html}
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes HTML and returns precise CSS selectors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            json_str = ai_response[start_idx:end_idx]
            
            selectors = json.loads(json_str)
            logger.info(f"AI identified selectors: {selectors}")
            return selectors
            
        except Exception as e:
            logger.error(f"Failed to identify elements with AI: {str(e)}")
            return {
                "article_selector": "div.item",
                "title_selector": "h2",
                "kicker_selector": "h5",
                "image_selector": "img",
                "link_selector": "a"
            }
    
    def scrape_yogonet(self, url: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape Yogonet website with AI-assisted selectors
        
        Args:
            url (str): URL to scrape
            max_articles (int): Maximum number of articles to scrape
            
        Returns:
            List[Dict[str, Any]]: List of scraped articles
        """
        logger.info(f"Starting to scrape {url} for up to {max_articles} articles")
        
        self.driver.get(url)
        time.sleep(5)
        
        page_title = self.driver.title
        logger.info(f"Page loaded with title: {page_title}")
        
        html_content = self.driver.page_source
        
        selectors = self.identify_elements_with_ai(html_content)
        
        article_selector = selectors["article_selector"]
        article_containers = self.driver.find_elements(By.CSS_SELECTOR, article_selector)
        
        logger.info(f"Found {len(article_containers)} article containers")
        
        article_containers = article_containers[:max_articles]
        
        articles = []
        for container in article_containers:
            try:
                title_element = container.find_element(By.CSS_SELECTOR, selectors["title_selector"])
                title = title_element.text.strip()
                
                try:
                    kicker_element = container.find_element(By.CSS_SELECTOR, selectors["kicker_selector"])
                    kicker = kicker_element.text.strip()
                except:
                    kicker = ""
                
                try:
                    image_element = container.find_element(By.CSS_SELECTOR, selectors["image_selector"])
                    image_url = image_element.get_attribute("src")
                except:
                    image_url = ""
                
                try:
                    link_element = container.find_element(By.CSS_SELECTOR, selectors["link_selector"])
                    link = link_element.get_attribute("href")
                except:
                    link = ""
                
                articles.append({
                    "title": title,
                    "kicker": kicker,
                    "image_url": image_url,
                    "link": link,
                    "ingestion_timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error scraping article: {str(e)}")
                continue
        
        logger.info(f"Successfully scraped {len(articles)} articles")
        return articles

def main():
    """Main entry point for the AI-assisted Yogonet scraper"""
    
    parser = argparse.ArgumentParser(description='Yogonet AI-assisted Scraper')
    parser.add_argument('--max-articles', type=int, default=int(os.environ.get('MAX_ARTICLES', 10)),
                        help='Maximum number of articles to scrape')
    parser.add_argument('--url', type=str, default='https://www.yogonet.com/international/',
                        help='URL to scrape')
    args = parser.parse_args()
    
    logger.info("Initializing Yogonet AI-assisted scraper")
    
    scraper = AIYogonetScraper()
    
    try:
        logger.info(f"Scraping up to {args.max_articles} articles from Yogonet")
        articles = scraper.scrape_yogonet(args.url, max_articles=args.max_articles)
        
        if not articles:
            logger.error("No articles were scraped. Exiting.")
            return 1
        
        logger.info(f"Successfully scraped {len(articles)} articles")
        
        os.makedirs('output', exist_ok=True)
        with open('output/scraped_data.json', 'w') as f:
            json.dump(articles, f, indent=2)
        logger.info("Saved raw scraped data to output/scraped_data.json")
        
        logger.info("Processing the scraped data with Pandas")
        processor = DataProcessor()
        processed_df = processor.process_data(articles)
        
        processed_df.to_csv('output/processed_data.csv', index=False)
        logger.info("Saved processed data to output/processed_data.csv")
        
        processed_df.to_json('output/processed_data.json', orient='records', indent=2)
        logger.info("Saved processed data to output/processed_data.json")
        
        logger.info("\nTitle Processing Metrics:")
        for i, row in processed_df.iterrows():
            logger.info(f"Article {i+1}: {row['title']}")
            logger.info(f"  - Word count: {row['title_word_count']}")
            logger.info(f"  - Character count: {row['title_char_count']}")
            logger.info(f"  - Capital words: {row['title_capital_words']}")
        
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if project_id:
            logger.info("Uploading processed data to BigQuery")
            logger.info(f"Initializing BigQuery client with project_id: {project_id}")
            
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '/app/credentials/service_account.json')
            logger.info(f"Using credentials from: {credentials_path}")
            
            if os.path.exists(credentials_path):
                logger.info(f"Credentials file exists at: {credentials_path}")
                try:
                    bq_client = BigQueryClient(project_id=project_id, credentials_path=credentials_path)
                    logger.info("BigQuery client initialized successfully")
                    
                    dataset_id = 'yogonet_news'
                    table_id = 'scraped_articles'
                    bq_client.upload_dataframe_to_table(processed_df, dataset_id, table_id)
                    logger.info(f"Successfully uploaded data to BigQuery {dataset_id}.{table_id}")
                except Exception as e:
                    logger.error(f"Error uploading to BigQuery: {str(e)}")
            else:
                logger.warning(f"Credentials file not found at {credentials_path}. Skipping BigQuery upload.")
        else:
            logger.info("No GOOGLE_CLOUD_PROJECT environment variable set. Skipping BigQuery upload.")
        
        return 0
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return 1
    finally:
        if 'scraper' in locals():
            del scraper

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code) 