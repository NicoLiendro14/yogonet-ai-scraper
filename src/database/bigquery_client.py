from google.cloud import bigquery
import os
import logging
import pandas as pd
from datetime import datetime


class BigQueryClient:
    """
    Client for interacting with Google BigQuery.
    Handles creating datasets and tables, and uploading data.
    """
    
    def __init__(self, project_id=None, credentials_path=None):
        """
        Initialize the BigQuery client.
        
        Args:
            project_id (str): Google Cloud project ID
            credentials_path (str): Path to the service account credentials JSON file
        """
        self.logger = logging.getLogger(__name__)
        
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not self.project_id:
            self.logger.warning("No project ID provided or found in environment variables") 
        
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                self.client = bigquery.Client.from_service_account_json(
                    self.credentials_path,
                    project=self.project_id
                )
                self.logger.info(f"BigQuery client initialized with credentials from {self.credentials_path}")
            else:
                self.client = bigquery.Client(project=self.project_id)
                self.logger.info("BigQuery client initialized with default credentials")
        except Exception as e:
            self.logger.error(f"Error initializing BigQuery client: {str(e)}")
            self.client = None
    
    def create_dataset_if_not_exists(self, dataset_id):
        """
        Create a dataset if it doesn't exist.
        
        Args:
            dataset_id (str): The ID of the dataset to create
            
        Returns:
            google.cloud.bigquery.dataset.Dataset or None: The dataset if created or exists
        """
        if not self.client:
            self.logger.error("BigQuery client not initialized")
            return None
            
        try:
            dataset_ref = self.client.dataset(dataset_id)
            
            try:
                dataset = self.client.get_dataset(dataset_ref)
                self.logger.info(f"Dataset {dataset_id} already exists")
                return dataset
            except Exception:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"
                dataset = self.client.create_dataset(dataset)
                self.logger.info(f"Created dataset {dataset_id}")
                return dataset
                
        except Exception as e:
            self.logger.error(f"Error creating dataset {dataset_id}: {str(e)}")
            return None
    
    def create_table_if_not_exists(self, dataset_id, table_id, schema=None):
        """
        Create a table if it doesn't exist.
        
        Args:
            dataset_id (str): The ID of the dataset
            table_id (str): The ID of the table to create
            schema (list): The schema for the table
            
        Returns:
            google.cloud.bigquery.table.Table or None: The table if created or exists
        """
        if not self.client:
            self.logger.error("BigQuery client not initialized")
            return None
            
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            
            try:
                table = self.client.get_table(table_ref)
                self.logger.info(f"Table {dataset_id}.{table_id} already exists")
                return table
            except Exception:
                if not schema:
                    schema = [
                        bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
                        bigquery.SchemaField("kicker", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("image_url", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("link", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("title_word_count", "INTEGER", mode="NULLABLE"),
                        bigquery.SchemaField("title_char_count", "INTEGER", mode="NULLABLE"),
                        bigquery.SchemaField("title_capital_words", "STRING", mode="REPEATED"),
                        bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED")
                    ]
                
                table = bigquery.Table(table_ref, schema=schema)
                table = self.client.create_table(table)
                self.logger.info(f"Created table {dataset_id}.{table_id}")
                return table
                
        except Exception as e:
            self.logger.error(f"Error creating table {dataset_id}.{table_id}: {str(e)}")
            return None
    
    def insert_data(self, dataset_id, table_id, data):
        """
        Insert data into a BigQuery table.
        
        Args:
            dataset_id (str): The dataset ID
            table_id (str): The table ID
            data (pandas.DataFrame): The data to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            self.logger.error("BigQuery client not initialized")
            return False
            
        if not isinstance(data, pd.DataFrame):
            self.logger.error("Data must be a pandas DataFrame")
            return False
            
        if data.empty:
            self.logger.warning("No data to insert")
            return False
            
        try:
            dataset = self.create_dataset_if_not_exists(dataset_id)
            if not dataset:
                self.logger.error(f"Failed to create or get dataset: {dataset_id}")
                return False
            
            table = self.create_table_if_not_exists(dataset_id, table_id)
            if not table:
                self.logger.error(f"Failed to create or get table: {dataset_id}.{table_id}")
                return False
            
            data['ingestion_timestamp'] = datetime.utcnow()
            
            self.logger.info(f"DataFrame columns: {list(data.columns)}")
            self.logger.info(f"DataFrame dtypes: {data.dtypes}")
            
            if 'title_capital_words' in data.columns:
                data['title_capital_words'] = data['title_capital_words'].apply(
                    lambda x: x if x and len(x) > 0 else None
                )
            
            table_ref = self.client.dataset(dataset_id).table(table_id)
            
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            )
            
            self.logger.info(f"Starting BigQuery load job for {len(data)} rows")
            
            job = self.client.load_table_from_dataframe(
                data, table_ref, job_config=job_config
            )
            
            job_result = job.result()
            
            self.logger.info(f"Job completed with ID: {job.job_id}")
            
            if hasattr(job_result, 'errors') and job_result.errors:
                for error in job_result.errors:
                    self.logger.error(f"Job error: {error}")
                return False
            
            self.logger.info(
                f"Successfully loaded {len(data)} rows into {dataset_id}.{table_id}"
            )
            return True
            
        except Exception as e:
            import traceback
            self.logger.error(f"Error inserting data: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            self.logger.error(f"Error details: {traceback.format_exc()}")
            return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    bq_client = BigQueryClient()
    
    dataset_id = "yogonet_news"
    table_id = "scraped_articles"
    
    bq_client.create_dataset_if_not_exists(dataset_id)
    bq_client.create_table_if_not_exists(dataset_id, table_id)
    
    data = pd.DataFrame([
        {
            "title": "Test Article",
            "kicker": "TEST",
            "image_url": "https://example.com/image.jpg",
            "link": "https://example.com/article",
            "title_word_count": 2,
            "title_char_count": 12,
            "title_capital_words": ["Test", "Article"]
        }
    ])
    
    bq_client.insert_data(dataset_id, table_id, data) 