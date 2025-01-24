from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig
import sys

# Main entry point for the script
if __name__=="__main__":
    try:
        # Step 1: Initialize the training pipeline configuration
        training_pipeline_config=TrainingPipelineConfig()

        # Step 2: Configure data ingestion settings
        data_ingestion_config=DataIngestionConfig(training_pipeline_config=training_pipeline_config)

        # Step 3: Create an instance of the DataIngestion class
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)

        # Log the initiation of the data ingestion process
        logging.info("Initiate the data ingestion")

        # Step 4: Execute the data ingestion process
        data_ingestion_artifact=data_ingestion.initiate_data_ingestion()

        logging.info("Data Initiation Completed")
        # Output the data ingestion artifact details
        print(data_ingestion_artifact)

        data_validation_config=DataValidationConfig(training_pipeline_config)
        data_validation=DataValidation(data_ingestion_artifact,data_validation_config)
        logging.info("Initiate the data validation")
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("Data validation completed")
        print(data_validation_artifact)

        


    except Exception as e:
        raise NetworkSecurityException(e, sys)