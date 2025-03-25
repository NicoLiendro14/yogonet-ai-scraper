import logging
from scraper.yogonet_scraper import YogonetScraper
from processing.data_processor import DataProcessor
from database.bigquery_client import BigQueryClient
import json
import os
from dotenv import load_dotenv

load_dotenv()


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
            processed_data = processed_df.to_dict(orient="records")
            with open(processed_output_path, "w", encoding="utf-8") as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved processed data to {processed_output_path}")

            logger.info("\nTitle Processing Metrics:")
            for i, article in enumerate(processed_data, 1):
                logger.info(f"Article {i}: {article['title']}")
                logger.info(f"  - Word count: {article['title_word_count']}")
                logger.info(f"  - Character count: {article['title_char_count']}")
                logger.info(f"  - Capital words: {article['title_capital_words']}")

            try:
                logger.info("Uploading processed data to BigQuery")

                project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
                credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                dataset_id = os.environ.get("BIGQUERY_DATASET_ID", "yogonet_news")
                table_id = os.environ.get("BIGQUERY_TABLE_ID", "scraped_articles")

                if not credentials_path and not project_id:
                    logger.warning(
                        "Skipping BigQuery upload - missing credentials or project ID"
                    )
                    logger.warning(
                        "Set GOOGLE_CLOUD_PROJECT and GOOGLE_APPLICATION_CREDENTIALS environment variables"
                    )
                else:
                    logger.info(
                        f"Initializing BigQuery client with project_id: {project_id}"
                    )
                    logger.info(f"Using credentials from: {credentials_path}")

                    if not os.path.exists(credentials_path):
                        logger.error(
                            f"Credentials file not found at: {credentials_path}"
                        )
                    else:
                        logger.info(f"Credentials file exists at: {credentials_path}")

                    bq_client = BigQueryClient(project_id, credentials_path)

                    if bq_client.client is None:
                        logger.error("BigQuery client initialization failed")
                    else:
                        logger.info("BigQuery client initialized successfully")

                        try:
                            insert_result = bq_client.insert_data(
                                dataset_id, table_id, processed_df
                            )
                            if insert_result:
                                logger.info(
                                    f"Successfully uploaded data to BigQuery {dataset_id}.{table_id}"
                                )
                            else:
                                logger.error(
                                    "Failed to upload data to BigQuery - see previous error logs for details"
                                )
                        except Exception as insert_error:
                            import traceback

                            logger.error(
                                f"Error during BigQuery data insertion: {str(insert_error)}"
                            )
                            logger.error(f"Error type: {type(insert_error).__name__}")
                            logger.error(f"Error details: {traceback.format_exc()}")
            except Exception as e:
                import traceback

                logger.error(f"Error in BigQuery upload process: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
        else:
            logger.warning("No articles scraped, skipping processing")

    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
    finally:
        if "scraper" in locals():
            scraper.close()
            logger.info("Scraper closed")


if __name__ == "__main__":
    main()
