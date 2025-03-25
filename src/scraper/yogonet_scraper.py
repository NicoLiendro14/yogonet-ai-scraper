from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import os

class YogonetScraper:
    """
    Scraper for Yogonet news portal.
    Extracts titles, kickers, images, and links from news articles.
    """
    
    def __init__(self, headless=None):
        """
        Initialize the scraper with Chrome WebDriver.
        
        Args:
            headless (bool): Whether to run Chrome in headless mode. If None, uses HEADLESS env var.
        """
        self.logger = logging.getLogger(__name__)
        
        if headless is None:
            headless_env = os.environ.get("HEADLESS", "false").lower()
            headless = headless_env in ("true", "1", "yes")
            self.logger.info(f"Using HEADLESS environment setting: {headless}")
        
        self.setup_driver(headless)
        
    def setup_driver(self, headless):
        """
        Set up Chrome WebDriver with appropriate options.
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
        """
        chrome_options = Options()
        
        chrome_env_options = os.environ.get("CHROME_OPTIONS", "")
        if chrome_env_options:
            self.logger.info(f"Using Chrome options from environment: {chrome_env_options}")
            for option in chrome_env_options.split():
                chrome_options.add_argument(option)
        else:
            if headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
        
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--log-level=0")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Chrome WebDriver initialized with ChromeDriverManager")
        except Exception as e:
            self.logger.warning(f"Error using ChromeDriverManager: {str(e)}")
            self.logger.info("Falling back to default Chrome WebDriver")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Chrome WebDriver initialized with default settings")
        
    def scrape_news(self, url="https://www.yogonet.com/international/", max_articles=None):
        """
        Scrape news articles from Yogonet.
        
        Args:
            url (str): The URL to scrape
            max_articles (int): Maximum number of articles to scrape. If None, uses MAX_ARTICLES env var.
            
        Returns:
            list: List of dictionaries containing article data
        """
        if max_articles is None:
            max_articles = int(os.environ.get("MAX_ARTICLES", "10"))
            self.logger.info(f"Using MAX_ARTICLES environment setting: {max_articles}")
        
        self.logger.info(f"Starting to scrape {url} for up to {max_articles} articles")
        self.driver.get(url)
        
        time.sleep(3)
        self.logger.info(f"Page loaded with title: {self.driver.title}")
        
        try:
            article_containers = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.slot.noticia"))
            )
            
            self.logger.info(f"Found {len(article_containers)} article containers")
            
            articles_data = []
            for i, container in enumerate(article_containers[:max_articles]):
                try:
                    article_data = self._extract_article_data(container)
                    if article_data:
                        articles_data.append(article_data)
                except Exception as e:
                    self.logger.error(f"Error extracting data from article {i}: {str(e)}")
            
            return articles_data
            
        except Exception as e:
            self.logger.error(f"Error scraping news: {str(e)}")
            return []
        
    def _extract_article_data(self, container):
        """
        Extract data from an article container.
        
        Args:
            container: WebElement representing the article container
            
        Returns:
            dict: Dictionary containing article data
        """
        try:
            kicker_elem = container.find_element(By.CSS_SELECTOR, "div.volanta")
            kicker = kicker_elem.text.strip() if kicker_elem else ""
            
            title_elem = container.find_element(By.CSS_SELECTOR, "h2.titulo a")
            title = title_elem.text.strip() if title_elem else ""
            
            link = title_elem.get_attribute("href") if title_elem else ""
            
            image_elem = container.find_element(By.CSS_SELECTOR, "div.imagen img")
            image_url = image_elem.get_attribute("src") if image_elem else ""
            
            return {
                "title": title,
                "kicker": kicker,
                "image_url": image_url,
                "link": link
            }
        except Exception as e:
            self.logger.error(f"Error extracting article data: {str(e)}")
            return None
    
    def close(self):
        """Close the WebDriver."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            
    def __del__(self):
        """Ensure the WebDriver is closed when the object is deleted."""
        self.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scraper = YogonetScraper(headless=True)
    articles = scraper.scrape_news(max_articles=5)
    
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"Kicker: {article['kicker']}")
        print(f"Image URL: {article['image_url']}")
        print(f"Link: {article['link']}")
        
    scraper.close()
