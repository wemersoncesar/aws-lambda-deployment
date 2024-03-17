"""
This module provides the implementation of the `lambda_handler` function executed by the AWS Lambda function in charge
of executing prophet pipelines on new preprocessed data.
"""
from app.config import Config
from app.emr_steps import AtaSteps, DataScienceStep
from app.emr import TransientEMRLauncher


def lambda_handler(event, context):
    lambda_name = context.function_name

    config = Config()
    emr = TransientEMRLauncher(
        name=f"prophet Transient EMR launched from {lambda_name}",
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
            step_name="A350 ATA3240 - prophettics",
            script_name="sparksubmit_ata32_wheels_and_brakes_prophettic.sh",
            fleet="a350",
            config=config,
        )
    )

    response = emr.run(steps=ata3240_steps())

    return response
