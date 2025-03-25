 import os
import json
import logging
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

# Configurar logging
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
        # Get OpenAI API key from environment or parameter
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        
        # Initialize Chrome options
        chrome_options = Options()
        chrome_options_env = os.environ.get("CHROME_OPTIONS", "")
        if chrome_options_env:
            options_list = chrome_options_env.split()
            for option in options_list:
                chrome_options.add_argument(option)
                logger.info(f"Added Chrome option: {option}")
        else:
            # Default options for headless operation
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--headless")
        
        logger.info(f"Using Chrome options from environment: {chrome_options_env}")
        
        # Initialize WebDriver
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
        # Simplified HTML for AI analysis
        soup = BeautifulSoup(html_content, 'html.parser')
        # Get a representative sample of the HTML structure
        simplified_html = str(soup.body)[:10000]  # Limited to 10k chars to save tokens
        
        # Prompt for OpenAI
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
            
            # Extract the JSON from the response
            ai_response = response.choices[0].message.content.strip()
            
            # Find the JSON part in the response (in case there's additional text)
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            json_str = ai_response[start_idx:end_idx]
            
            selectors = json.loads(json_str)
            logger.info(f"AI identified selectors: {selectors}")
            return selectors
            
        except Exception as e:
            logger.error(f"Failed to identify elements with AI: {str(e)}")
            # Return default selectors as fallback
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
        
        # Navigate to the URL
        self.driver.get(url)
        time.sleep(5)  # Give page time to load
        
        # Get page title
        page_title = self.driver.title
        logger.info(f"Page loaded with title: {page_title}")
        
        # Get page HTML
        html_content = self.driver.page_source
        
        # Identify selectors with AI
        selectors = self.identify_elements_with_ai(html_content)
        
        # Find all article containers using the AI-identified selector
        article_selector = selectors["article_selector"]
        article_containers = self.driver.find_elements(By.CSS_SELECTOR, article_selector)
        
        logger.info(f"Found {len(article_containers)} article containers")
        
        # Limit the number of articles
        article_containers = article_containers[:max_articles]
        
        # Scrape each article
        articles = []
        for container in article_containers:
            try:
                # Extract data using AI-provided selectors
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