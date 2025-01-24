from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


# Importing configuration classes for data ingestion

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import numpy as np
import pandas as pd
import pymongo
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
# Loading environment variables from .env file
load_dotenv()

# Fetching MongoDB connection URL from environment variables
MONGO_DB_URL=os.getenv("MONGO_DB_URL")


class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        """
        Initializes the DataIngestion class with configuration settings.
        """
        try:
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def export_collection_as_dataframe(self):
        """
        Reads data from MongoDB and exports it as a Pandas DataFrame.
        - Drops the '_id' column if present.
        - Replaces 'na' values with NaN for consistency.
        """
        try:
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name]

            # Convert MongoDB collection to DataFrame
            df=pd.DataFrame(list(collection.find()))

            # Drop the '_id' column if it exists
            if "_id" in df.columns.to_list():
                df=df.drop(columns=["_id"],axis=1)
            
            # Replace 'na' with NaN for better handling of missing values
            df.replace({"na":np.nan},inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def export_data_into_feature_store(self,dataframe: pd.DataFrame):
        """
        Exports the DataFrame into a CSV file stored in the feature store path.
        - Creates necessary directories if they do not exist.
        """
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            
            # Creating the directory for the feature store file if it doesn't exist
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)

            # Save the DataFrame as a CSV file
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def split_data_as_train_test(self,dataframe: pd.DataFrame):
        """
        Splits the DataFrame into training and testing datasets.
        - Saves the train and test datasets into separate CSV files.
        """
        try:
            # Splitting the data into train and test sets based on the specified ratio
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Performed train test split on the dataframe")

            logging.info(
                "Exited split_data_as_train_test method of Data_Ingestion class"
            )
            # Creating directories for train and test files if they don't exist

            dir_train= os.path.dirname(self.data_ingestion_config.training_file_path)
            dir_test = os.path.dirname(self.data_ingestion_config.testing_file_path)
            
            os.makedirs(dir_train, exist_ok=True)
            os.makedirs(dir_test, exist_ok=True)
            
            logging.info(f"Exporting train and test file path.")

            # Save train set to a CSV file
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            # Save test set to a CSV file
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            logging.info(f"Exported train and test file path.")
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
        
    def initiate_data_ingestion(self):
        """
        Main method to orchestrate the data ingestion process:
        - Export data from MongoDB to a DataFrame.
        - Save the data to a feature store.
        - Split the data into training and testing datasets.
        - Returns a DataIngestionArtifact with paths to the train and test files.
        """
        try:
            # Step 1: Export data from MongoDB to a DataFrame
            dataframe=self.export_collection_as_dataframe()

            # Step 2: Save the DataFrame to the feature store
            dataframe=self.export_data_into_feature_store(dataframe)

            # Step 3: Split the data into train and test sets
            self.split_data_as_train_test(dataframe)

            # Step 4: Create an artifact with train and test file paths
            dataingestionartifact=DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
                                                        test_file_path=self.data_ingestion_config.testing_file_path)
            return dataingestionartifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)