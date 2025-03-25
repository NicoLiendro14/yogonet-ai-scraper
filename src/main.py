import logging
from scraper.yogonet_scraper import YogonetScraper
import json
import os

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    """Main function to run the scraper."""
    logger = setup_logging()
    
    try:
        logger.info("Initializing Yogonet scraper") 
        scraper = YogonetScraper(headless=True)
        
        max_articles = int(os.environ.get("MAX_ARTICLES", "10"))
        logger.info(f"Scraping up to {max_articles} articles from Yogonet")
        articles = scraper.scrape_news(max_articles=max_articles)
        
        logger.info(f"Successfully scraped {len(articles)} articles")
        for i, article in enumerate(articles, 1):
            logger.info(f"Article {i}: {article['title']}")
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, "scraped_data.json"), "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved scraped data to {os.path.join(output_dir, 'scraped_data.json')}")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
    finally:
        if 'scraper' in locals():
            scraper.close()
            logger.info("Scraper closed")

if __name__ == "__main__":
    main()
