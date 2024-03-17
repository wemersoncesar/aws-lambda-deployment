"""
This module provides the implementation of the `lambda_handler` function executed by the AWS Lambda function in charge
of executing prophet pipelines on new preprocessed data.
"""
from app.config import Config
from app.emr_steps import AtaSteps, DataEngineeringStep
from app.emr import TransientEMRLauncher


def lambda_handler(event, context):
    #'--class', 'com.linkit.em.prophet.preprocessor.Preprocessor',
    #s3://w-emr-code-deployment/main/prophet-preprocessor_2.12-1.3.0-assembly.jar
    lambda_name = context.function_name
    args_preprocessor = ['--class', 'com.linkit.Main',
                         '--master', 'yarn',
                         '--deploy-mode', 'cluster',
                         #'--files', 's3://w-emr-code-deployment/main/log4j.properties',
                         '--conf', 'spark.sql.parquet.fs.optimized.committer.optimization-enabled=true',
                         '--conf', 'spark.streaming.backpressure.enabled=true',
                         's3://w-emr-code-deployment/job-jar/test-s3_2.12-0.1.0-SNAPSHOT.jar',
                         '-p', 'Aws',
                         '-e', 'Dev',
                         '-s', 'Ags',
                         '-c', 'va',
                         '--checkpoint-path', 's3://w-emr-code-deployment/preprocessor-checkpoints-16',
                         '--input-folder', 's3://w-emr-code-deployment/input-folder/',
                         '--output-path', 's3://w-emr-code-deployment/output-path/',
                         '--ignore-days-before', '2023-01-01',
                         '--allow-reprocessing',
                         '--as-batch',
                         '--max-files-per-trigger',
                         '5']

    lambda_name = context.function_name

    config = Config()
    emr = TransientEMRLauncher(
        name=f"prophet Transient EMR launched from {lambda_name}",
        config=config
    )

    # ATA 32 40
    ata3240_steps = AtaSteps() 
    ata3240_steps.add_step(
        step=DataEngineeringStep(
            name="A350 ATA3240 - prophettics", 
            args=args_preprocessor,
        )
    )

    response = emr.run(steps=ata3240_steps())

    return response
