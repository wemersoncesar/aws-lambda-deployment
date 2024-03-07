"""
This module provides the implementation of the `lambda_handler` function executed by the AWS Lambda function in charge
of executing Prognos pipelines on new preprocessed data.
"""
from app.config import Config
from app.emr import DataScienceStep, TransientEMRLauncher, AtaSteps

def lambda_handler(event, context):
    lambda_name = context.function_name

    config = Config()
    emr = TransientEMRLauncher(
        name=f"Prognos Transient EMR launched from {lambda_name}",
        config=config
    )
    
    # ATA 32 40
    ata3240_steps = AtaSteps()
    ata3240_steps.add_step(
        step=DataScienceStep(
            step_name="A350 ATA3240 - KPIs",
            script_name="sparksubmit_ata32_wheels_and_brakes_kpi.sh",
            fleet="a350",
            config=config,
        )
    )
    ata3240_steps.add_step(
        step=DataScienceStep(
            step_name="A350 ATA3240 - Prognostics",
            script_name="sparksubmit_ata32_wheels_and_brakes_prognostic.sh",
            fleet="a350",
            config=config,
        )
    )
    
    response = emr.run(steps=ata3240_steps())
    
    return response
