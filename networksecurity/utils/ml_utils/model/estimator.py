from networksecurity.constant.training_pipeline import MODEL_FILE_NAME,SAVED_MODEL_DIR
import os,sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkModel:
    """
    A wrapper class for the trained machine learning model and preprocessor.
    This class ensures that input data is preprocessed before making predictions.
    """
    def __init__(self,preprocessor,model):
        """
        Initializes the NetworkModel with a preprocessor and a trained model.

        Args:
            preprocessor: The data preprocessing object used during training.
            model: The trained machine learning model.
        """
        try:
            self.preprocessor = preprocessor # Store the preprocessor
            self.model = model # Store the trained model
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def predict(self,x):
        """
        Transforms input data using the preprocessor and makes predictions using the trained model.

        Args:
            x: Input feature data to be predicted.

        Returns:
            y_hat: Predicted values from the model.
        """
        try:
            # Transform input features using the preprocessor
            x_transform=self.preprocessor.transform(x)
            
            # Make predictions using the trained model
            y_hat = self.model.predict(x_transform)
            return y_hat 
        except Exception as e:
            raise NetworkSecurityException(e, sys)
