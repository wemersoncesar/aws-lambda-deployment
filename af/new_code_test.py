from app.submit_args import SubmitArgs
from app.config import Config
from app.emr import TransientEMRLauncher, DataEngineeringStep, AtaSteps


def create_steps(steps, args):
    steps.add_step(step=DataEngineeringStep(
        name='CplPreprocessor Job',
        args=args.args_preprocessor,
    ))
    return steps


def lambda_handler(event, context):

    args = SubmitArgs()
    config = Config()
    print({context.function_name})

    emr_cluster = TransientEMRLauncher(
        name=f"prophet Transient EMR launched from {context.function_name}",
        config=config
    )

    ata_steps = AtaSteps()
    ata_steps.add_step(step=DataEngineeringStep(
        name='CplPreprocessor Job',
        args=args.args_preprocessor
    ))

    response = emr_cluster.run(steps=ata_steps)

    return response
