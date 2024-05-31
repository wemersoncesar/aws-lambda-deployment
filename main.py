"""
This module provides the implementation of the `lambda_handler` function executed by the AWS Lambda function in charge
of executing prophet pipelines on new preprocessed data.
"""
from S3Cleaner import S3Cleaner
from app.config import Config



def lambda_handler(event, context):

    config = Config()
    print(">>>>> ok <<<<<<")
    cleaner = S3Cleaner(config)
    cleaner.clean_checkpoint_folder()


lambda_handler("", "")
