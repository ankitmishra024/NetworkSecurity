import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME
from networksecurity.cloud.s3_syncer import S3Sync

from networksecurity.entity.config_entity import(
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)

class TrainingPipeline:
    """
    A class to define the complete machine learning pipeline, including data ingestion, 
    validation, transformation, model training, and artifact synchronization with AWS S3.
    """
    def __init__(self):
        """
        Initializes the TrainingPipeline with necessary configurations and S3Sync instance.
        """
        self.training_pipeline_config=TrainingPipelineConfig()
        self.s3_sync = S3Sync()

    def start_data_ingestion(self):
        """
        Initiates the data ingestion process.

        Returns:
            DataIngestionArtifact: Artifact containing details of the ingested data.
        """
        try:
            self.data_ingestion_config=DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Start data Ingestion")
            data_ingestion=DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
            logging.info(f"Data Ingestion completed and artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def start_data_validation(self,data_ingestion_artifact:DataIngestionArtifact):
        """
        Initiates the data validation process.

        Args:
            data_ingestion_artifact: Artifact from data ingestion process.

        Returns:
            DataValidationArtifact: Artifact containing validation results.
        """
        try:
            data_validation_config=DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            data_validation=DataValidation(data_ingestion_artifact=data_ingestion_artifact,data_validation_config=data_validation_config)
            logging.info("Initiate the data validation")
            data_validation_artifact=data_validation.initiate_data_validation()
            logging.info(f"Data validation completed and artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def start_data_transformation(self,data_validation_artifact:DataValidationArtifact):
        """
        Initiates the data transformation process.

        Args:
            data_validation_artifact: Artifact from data validation process.

        Returns:
            DataTransformationArtifact: Artifact containing transformed data details.
        """
        try:
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,data_transformation_config=data_transformation_config)
            logging.info("Initiate the data transformation")
            data_transformation_artifact=data_transformation.initiate_data_transformation()
            logging.info(f"Data transformation completed and artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def start_model_trainer(self,data_transformation_artifact:DataTransformationArtifact)->ModelTrainerArtifact:
        """
        Initiates the model training process.

        Args:
            data_transformation_artifact: Artifact from data transformation process.

        Returns:
            ModelTrainerArtifact: Artifact containing model training results.
        """
        try:
            self.model_trainer_config: ModelTrainerConfig = ModelTrainerConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            model_trainer = ModelTrainer(
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_config=self.model_trainer_config,
            )
            logging.info("Model trainer started")
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info("Model tainer completed")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def sync_artifact_dir_to_s3(self):
        """
        Syncs the local artifact directory to AWS S3.
        """
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.artifact_dir,aws_bucket_url = aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def sync_saved_model_dir_to_s3(self):
        """
        Syncs the saved model directory to AWS S3.
        """
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder=self.training_pipeline_config.model_dir,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def run_pipeline(self):
        """
        Runs the complete training pipeline, including:
        - Data ingestion
        - Data validation
        - Data transformation
        - Model training
        - Synchronization of artifacts and models to AWS S3

        Returns:
            ModelTrainerArtifact: The final artifact from the model training process.
        """
        try:
            # Step 1: Data Ingestion
            data_ingestion_artifact=self.start_data_ingestion()

            # Step 2: Data Validation
            data_validation_artifact=self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)

            # Step 3: Data Transformation
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)

            # Step 4: Model Training
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            
            # Step 5: Sync Artifacts to S3
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)


