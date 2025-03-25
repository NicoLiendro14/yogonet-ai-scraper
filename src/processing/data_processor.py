import pandas as pd
import re
import logging


class DataProcessor:
    """
    Process the scraped news data using Pandas.
    Calculates metrics including word count, character count,
    and capitalized words in the titles.
    """
    
    def __init__(self):
        """Initialize the data processor."""
        self.logger = logging.getLogger(__name__)
    
    def process_data(self, articles_data):
        """
        Process the scraped article data.
        
        Args:
            articles_data (list): List of dictionaries containing article data
            
        Returns:
            pandas.DataFrame: DataFrame with the processed data
        """
        if not articles_data:
            self.logger.warning("No articles data to process")
            return pd.DataFrame()
            
        df = pd.DataFrame(articles_data)
        
        df = self._process_titles(df)
        
        self.logger.info(f"Processed {len(df)} articles")
        return df
    
    def _process_titles(self, df):
        """
        Process the titles in the DataFrame.
        
        Args:
            df (pandas.DataFrame): DataFrame with article data
            
        Returns:
            pandas.DataFrame: DataFrame with processed title metrics
        """
        if 'title' not in df.columns:
            self.logger.error("No 'title' column found in the data")
            return df

        df['title_word_count'] = df['title'].apply(lambda x: len(str(x).split()))
        
        df['title_char_count'] = df['title'].apply(lambda x: len(str(x)))
        
        df['title_capital_words'] = df['title'].apply(self._find_capitalized_words)
        
        return df
    
    def _find_capitalized_words(self, text):
        """
        Find words that start with a capital letter in the given text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            list: List of capitalized words
        """
        if not text:
            return []
            
        words = re.findall(r'\b[A-Z][a-zA-Z\']*\b', str(text))
        return words
    
    def save_to_csv(self, df, output_path):
        """
        Save the processed data to a CSV file.
        
        Args:
            df (pandas.DataFrame): DataFrame with processed data
            output_path (str): Path to save the CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            df.to_csv(output_path, index=False)
            self.logger.info(f"Saved processed data to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving data to CSV: {str(e)}")
            return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    sample_articles = [
        {
            "title": "Rep. Dina Titus Revives Push to Eliminate Federal Sports Betting Tax",
            "kicker": "EFFORT SEEKS TO LEVEL PLAYING FIELD FOR LEGAL OPERATORS",
            "image_url": "https://example.com/image.jpg",
            "link": "https://example.com/article"
        }
    ]
    
    processor = DataProcessor()
    processed_df = processor.process_data(sample_articles)
    
    print("\nProcessed Data:")
    print(processed_df)
    print("\nTitle Word Count:", processed_df['title_word_count'].values[0])
    print("Title Character Count:", processed_df['title_char_count'].values[0])
    print("Title Capital Words:", processed_df['title_capital_words'].values[0]) 