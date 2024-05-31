import boto3
from abc import ABC, abstractmethod


class EMRStep(ABC):
    """Abstract base class for EMR steps."""

    @abstractmethod
    def __call__(self):
        """Return the EMR step configuration."""
        pass


class DataEngineeringStep(EMRStep):
    """Class representing a step performed by the data engineering code in EMR."""

    def __init__(self, name, script_path, args=None):
        self.name = name
        self.script_path = script_path
        self.args = args or []

    def __call__(self):
        """Return the Spark step configuration."""
        return {
            "Name": self.name,
            "ActionOnFailure": "CONTINUE",
            "HadoopJarStep": {
                "Jar": "command-runner.jar",
                "Args": ["spark-submit", "--deploy-mode", "cluster", self.script_path]
                + self.args,
            },
        }


class GenericPipelineStep(EMRStep):
    """Class representing a step performed by the data engineering code in EMR."""

    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []

    def __call__(self):
        """Return the Spark step configuration."""
        return {
            "Name": self.name,
            "ActionOnFailure": "TERMINATE_CLUSTER",
            "HadoopJarStep": {
                "Jar": "command-runner.jar",
                "Args": ["spark-submit"] + self.args,
            },
        }


class DataScienceStep(EMRStep):
    """Class representing a step performed by the data science code in EMR."""

    def __init__(
        self, step_name, script_name, fleet, config, on_failure="TERMINATE_CLUSTER"
    ):
        self.step_name = step_name
        self.script_name = script_name
        self.fleet = fleet
        self.config = config
        self.on_failure = on_failure

    def __call__(self):
        """Return the Spark step configuration."""
        jar_path = f"s3://{self.config.region}.elasticmapreduce/libs/script-runner/script-runner.jar"
        application_base_bucket = self.config.bucket_base_name["application"]
        application_bucket = f"{application_base_bucket}-{self.config.customer_id}-{self.config.environment}"
        application_bucket_uri = f"s3://{application_bucket}"
        # To adapt with HDFS URIs once data engineers implement working steps.
        data_base_bucket = self.config.bucket_base_name["data"]
        data_bucket = (
            f"{data_base_bucket}-{self.config.customer_id}-{self.config.environment}"
        )
        data_bucket_uri = f"s3://{data_bucket}"
        data_base_uri = f"{data_bucket_uri}/processed/{self.fleet}"

        script_uri = f"{application_bucket_uri}/or/sparksubmits/pipelines/{self.fleet}/{self.script_name}"
        arguments = [
            script_uri,
            application_bucket_uri,
            data_base_uri,
            self.config.environment,
        ]
        return {
            "Name": self.step_name,
            "ActionOnFailure": self.on_failure,
            "HadoopJarStep": {"Jar": jar_path, "Args": arguments},
        }


class AtaSteps:
    """Class representing the necessary steps to process a given ATA."""

    def __init__(self):
        self.__steps = []

    def add_step(self, step: EMRStep):
        self.__steps.append(step)

    def __call__(self):
        return self.__steps


class TransientEMRLauncher:
    """Class for launching transient EMR on AWS."""

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.emr_client = boto3.client("emr", region_name=config.region)

    def run(self, steps):
        """Launch EMR with specified steps."""

        if not all([isinstance(step, EMRStep) for step in steps]):
            raise ValueError("All steps must be defined from EMRStep.")

        response = self.emr_client.run_job_flow(
            Name=self.name,
            LogUri=self.config.emr_logs_uri,
            Instances={
                "MasterInstanceType": self.config.master_instance_type,
                "SlaveInstanceType": self.config.slave_instance_type,
                "InstanceCount": int(self.config.instance_count),
                "Ec2SubnetId": self.config.ec2_subnet_id,
                "Ec2KeyName": self.config.ec2_key_name,
                "EmrManagedMasterSecurityGroup": self.config.security_group,
                "EmrManagedSlaveSecurityGroup": self.config.security_group,
                "ServiceAccessSecurityGroup": self.config.service_access_security_group,
            },
            ReleaseLabel=self.config.emr_version,
            Applications=[{"Name": "Spark"}],
            Steps=[step() for step in steps],
            ServiceRole=self.config.emr_service_role,
            JobFlowRole=self.config.emr_job_flow_role,
            VisibleToAllUsers=True,
        )
        return response
