import os

class S3Sync:
    """
    A utility class for syncing local folders with AWS S3.
    """

    def sync_folder_to_s3(self,folder,aws_bucket_url):
        """
        Syncs a local folder to an AWS S3 bucket.
        
        Args:
            folder (str): Path to the local folder to be uploaded.
            aws_bucket_url (str): S3 bucket URL where data will be stored.
        
        Returns:
            None
        """
        command=f"aws s3 sync {folder} {aws_bucket_url}"
        os.system(command)

    def sync_folder_form_s3(self,folder,aws_bucket_url):
        """
        Syncs an AWS S3 bucket to a local folder.
        
        Args:
            folder (str): Path to the local folder where data will be downloaded.
            aws_bucket_url (str): S3 bucket URL to retrieve data from.
        
        Returns:
            None
        """
        command=f"aws s3 sync {aws_bucket_url} {folder}"
        os.system(command)