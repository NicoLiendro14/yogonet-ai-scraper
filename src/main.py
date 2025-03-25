import logging
from scraper.yogonet_scraper import YogonetScraper
from processing.data_processor import DataProcessor
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
    """Main function to run the scraper and data processor."""
    logger = setup_logging()
    
    try:
        logger.info("Initializing Yogonet scraper")
        scraper = YogonetScraper(headless=True)
        
        max_articles = int(os.environ.get("MAX_ARTICLES", "10"))
        logger.info(f"Scraping up to {max_articles} articles from Yogonet")
        articles = scraper.scrape_news(max_articles=max_articles)
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        if articles:
            logger.info(f"Successfully scraped {len(articles)} articles")
            raw_output_path = os.path.join(output_dir, "scraped_data.json")
            with open(raw_output_path, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved raw scraped data to {raw_output_path}")
            
            logger.info("Processing the scraped data with Pandas")
            processor = DataProcessor()
            processed_df = processor.process_data(articles)
            
            csv_output_path = os.path.join(output_dir, "processed_data.csv")
            processor.save_to_csv(processed_df, csv_output_path)
            
            processed_output_path = os.path.join(output_dir, "processed_data.json")
            processed_data = processed_df.to_dict(orient='records')
            with open(processed_output_path, "w", encoding="utf-8") as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved processed data to {processed_output_path}")
                
            logger.info("\nTitle Processing Metrics:")
            for i, article in enumerate(processed_data, 1):
                logger.info(f"Article {i}: {article['title']}")
                logger.info(f"  - Word count: {article['title_word_count']}")
                logger.info(f"  - Character count: {article['title_char_count']}")
                logger.info(f"  - Capital words: {article['title_capital_words']}")
        else:
            logger.warning("No articles scraped, skipping processing")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
    finally:
        if 'scraper' in locals():
            scraper.close()
            logger.info("Scraper closed")

if __name__ == "__main__":
    main()
