import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline


# Importing constants for data transformation configuration
from networksecurity.constant.training_pipeline import(
    TARGET_COLUMN,
    DATA_TRANSFORMATION_IMPUTER_PARAMA
)

# Importing artifact entities related to data transformation
from networksecurity.entity.artifact_entity import(
    DataTransformationArtifact,
    DataValidationArtifact
)

# Importing configuration entity for data transformation
from networksecurity.entity.config_entity import DataTransformationConfig

# Importing custom exception and logging utilities
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# Importing utility functions for saving processed data
from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_object


class DataTransformation:
    """
    Handles the transformation of raw validated data.
    - Applies missing value imputation using KNNImputer.
    - Converts data into a structured format for model training.
    - Saves transformed data as numpy arrays.
    """
    def __init__(self,data_validation_artifact:DataValidationArtifact,
                 data_transformation_config:DataTransformationConfig):
        """
        Initializes the DataTransformation class with necessary configurations.

        Args:
            data_validation_artifact (DataValidationArtifact): Contains paths to validated training and test files.
            data_transformation_config (DataTransformationConfig): Configuration object for transformation process.
        """
        try:
            self.data_validation_artifact:DataValidationArtifact=data_validation_artifact
            self.data_transformation_config:DataTransformationConfig=data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path)-> pd.DataFrame:
        """
        Reads data from a CSV file and loads it into a Pandas DataFrame.

        Args:
            file_path (str): Path to the CSV file.

        Returns:
            pd.DataFrame: The loaded data as a DataFrame.
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def get_data_transformer_object(cls)->Pipeline:
        """
        Initializes a data transformation pipeline using KNNImputer for missing value imputation.

        Returns:
            Pipeline: A scikit-learn Pipeline object with KNNImputer as the transformation step.
        """
        logging.info("Entered get_data_transformer_object method of Transformation class")
        try:
            # Initialize KNNImputer with parameters from configuration
            imputer:KNNImputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMA)
            logging.info(
                f"Initialise KNNImputer with {DATA_TRANSFORMATION_IMPUTER_PARAMA}"
            )
            # Create a pipeline with KNNImputer as the transformation step
            processor:Pipeline=Pipeline([("imputer",imputer)])
            return processor

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_transformation(self)->DataTransformationArtifact:
        """
        Orchestrates the data transformation process, which includes:
        - Reading validated train and test data.
        - Separating input features and target column.
        - Applying missing value imputation using KNNImputer.
        - Saving transformed data as numpy arrays.
        - Saving the transformation object for future use.

        Returns:
            DataTransformationArtifact: Contains paths to transformed data and transformation object.
        """
        try:
            logging.info("Starting data transformation")
            # Load validated train and test data
            train_df=DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df=DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            # Splitting training data into input features and target
            input_feature_train_df=train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df=train_df[TARGET_COLUMN]
            # Convert target labels (-1) to (0) if needed
            target_feature_train_df=target_feature_train_df.replace(-1, 0)

            # Splitting testing data into input features and target
            input_feature_test_df=test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df=test_df[TARGET_COLUMN]
            # Splitting testing data into input features and target
            target_feature_test_df=target_feature_test_df.replace(-1, 0)

            # Get the transformation pipeline
            preprocessor=self.get_data_transformer_object()

            # Fit the preprocessor on training data and transform both train and test data
            preprocessor_object=preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature=preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature=preprocessor_object.transform(input_feature_test_df)

            # Combine transformed input features with target column
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            # Save transformed train and test data as numpy arrays
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,array=train_arr,)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,array=test_arr,)
            # Save the preprocessing object for future inference
            save_object(self.data_transformation_config.transformd_object_file_path,preprocessor_object)
            
            # Also save the transformation object in a separate directory for final model use
            save_object("final_model/preprocessor.pkl", preprocessor_object)

            # Prepare and return the data transformation artifact
            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformd_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                trasformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
            )
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
