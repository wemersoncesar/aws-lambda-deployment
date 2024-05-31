"""
This module provides the implementation of the `lambda_handler` function executed by the AWS Lambda function in charge
of executing prophet pipelines on new preprocessed data.
"""

from app.config import Config
import app.S3Cleaner as S3Cleaner
from app.emr import TransientEMRLauncher, AtaSteps, GenericPipelineStep
from submit_args import SubmitArgs
import os

def lambda_handler(event, context):
    print(">>>>> ok <<<<<<")
    config = Config()

    cleaner = S3Cleaner(config)
    cleaner.clean_checkpoint_folder()
    
