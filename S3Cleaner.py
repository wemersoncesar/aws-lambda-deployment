import boto3

class S3Cleaner:
    def __init__(self, config):
        self.config = config
        self.s3 = boto3.client('s3')

    def get_checkpoint_path(self):
        """ Extracts the S3 checkpoint path from the configuration. """
        job_args = self.config.job_args.get("preprocessor", {})

        for arg in job_args["applicationArguments"]:
            if arg.startswith("--checkpoint-path"):
                return arg.split(" ")[1]
        raise ValueError("Checkpoint path not found in the configuration.")

    def clean_s3_folder(self, bucket, prefix):
        """ Deletes all objects within a specified bucket and prefix. """
        paginator = self.s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            objects = page.get('Contents', [])
            if objects:
                objects_to_delete = [{'Key': obj['Key']} for obj in objects]
                self.s3.delete_objects(Bucket=bucket, Delete={'Objects': objects_to_delete})

    def clean_checkpoint_folder(self):
        """ Cleans the S3 folder specified in the '--checkpoint-path' argument. """
        s3_checkpoint_path = self.get_checkpoint_path()
        bucket_name, prefix = s3_checkpoint_path.replace("s3://", "").split("/", 1)
        print(bucket_name)
        self.clean_s3_folder(bucket_name, prefix)
