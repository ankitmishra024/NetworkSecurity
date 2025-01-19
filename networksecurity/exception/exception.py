import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from networksecurity.logging import logger  # Import the custom logger module

class NetworkSecurityException(Exception):
    """
    Custom exception class for handling network security-related errors.
    """

    def __init__(self, error_message, error_details: sys):
        """
        Initialize the exception with an error message and details.
        
        Args:
        error_message (str): A descriptive error message.
        error_details (sys): System information for extracting traceback details.
        """
        self.error_message = error_message
        
        # Extract traceback details to identify the line number and file where the error occurred
        _, _, exc_tb = error_details.exc_info()
        self.lineno = exc_tb.tb_lineno  # Line number where the exception occurred
        self.file_name = exc_tb.tb_frame.f_code.co_filename  # File name where the exception occurred

    def __str__(self):
        """
        Return a formatted string representation of the error details.
        """
        return (f"Error occurred in python script: {self.file_name}, "
                f"line number: {self.lineno}, error message: {str(self.error_message)}")

if __name__ == "__main__":
    try:
        logger.logging.info("Entering the try block")
        a = 1 / 0
        print("This will not be printed", a)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
