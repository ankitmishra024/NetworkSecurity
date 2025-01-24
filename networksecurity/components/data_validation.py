# input of data_validation comes form dataIngestion artifact
from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file
from scipy.stats import ks_2samp
import pandas as pd
import os, sys

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        """
        Constructor to initialize DataValidation with the data ingestion artifact 
        and data validation configuration.
        """
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config

            # Load schema configuration from YAML file
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        """
        Reads a CSV file and returns it as a pandas DataFrame.
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def validate_number_of_column(self,dataframe:pd.DataFrame)->bool:
        """
        Validates whether the number of columns in the dataframe matches the required number
        defined in the schema.
        """
        try:
            number_of_columns=len(self._schema_config)
            logging.info(f"Required number of columns:{number_of_columns}")
            logging.info(f"Dataframe has columns:{len(dataframe.columns)}")
            if len(dataframe.columns) == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def detect_dataset_drift(self,base_df,current_df,thresshold=0.05)->bool:
        """
        Detects dataset drift between the base dataframe (e.g., train) and the current dataframe (e.g., test).
        Drift is determined using the KS test for each column.
        """
        try:
            status=True
            report={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                # Perform KS test to compare distributions
                is_same_dist=ks_2samp(d1, d2)

                # Check if p-value is below the threshold (indicating drift)
                if thresshold <= is_same_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status=False
                
                # Update drift report
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                }})

            # Write drift report to YAML file    
            drift_report_file_path = self.data_validation_config.report_file_path

            # create directory
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

        
    def initiate_data_validation(self)->DataValidationArtifact:
        """
        Initiates the data validation process:
        - Reads training and testing data
        - Validates the number of columns
        - Checks for dataset drift
        - Saves validated data and generates a validation artifact
        """
        try:
            # Get paths to training and testing files
            train_file_path=self.data_ingestion_artifact.trained_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            # Read the data from train and test files
            train_dataframe=self.read_data(train_file_path)
            test_dataframe=self.read_data(test_file_path)

            # Validate the number of columns for the train dataframe
            status=self.validate_number_of_column(dataframe=train_dataframe)
            if not status:
                error_message=f"Train dataframe does not contain all columns.\n"
            
            # Validate the number of columns for the test dataframe
            status=self.validate_number_of_column(dataframe=test_dataframe)
            if not status:
                error_message=f"Test dataframe does not contains all columns.\n"

            # Check for dataset drift
            status=self.detect_dataset_drift(base_df=train_dataframe, current_df=test_dataframe)

            # Create directories to save validated train and test data
            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)

            # Save validated train and test data
            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True

            )
            
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )

            # Create a DataValidationArtifact to store validation results
            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.report_file_path
            )

            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)