from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

class YogonetScraper:
    """
    Scraper for Yogonet news portal.
    Extracts titles, kickers, images, and links from news articles.
    """
    
    def __init__(self, headless=True):
        """
        Initialize the scraper with Chrome WebDriver.
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
        """
        self.logger = logging.getLogger(__name__)
        self.setup_driver(headless)
        
    def setup_driver(self, headless):
        """
        Set up Chrome WebDriver with appropriate options.
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def scrape_news(self, url="https://www.yogonet.com/international/", max_articles=10):
        """
        Scrape news articles from Yogonet.
        
        Args:
            url (str): The URL to scrape
            max_articles (int): Maximum number of articles to scrape
            
        Returns:
            list: List of dictionaries containing article data
        """
        self.logger.info(f"Starting to scrape {url}")
        self.driver.get(url)
        
        time.sleep(3)
        
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
