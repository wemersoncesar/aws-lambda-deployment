from abc import ABC, abstractmethod


class EMRStep(ABC):
    """Abstract base class for EMR steps."""

    @abstractmethod
    def __call__(self):
        """Return the EMR step configuration."""
        pass


class AtaSteps:
    """Class representing the necessary steps to process a given ATA."""

    def __init__(self):
        self.__steps = []

    def add_step(self, step: EMRStep):
        self.__steps.append(step)

    def __call__(self):
        return self.__steps


class DataEngineeringStep(EMRStep):
    """Class representing a step performed by the data engineering code in EMR."""

    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []

    def __call__(self):
        """Return the Spark step configuration."""
        print(f"printing the args {self.args}")
        return {
            'Name': self.name,
            'ActionOnFailure': 'TERMINATE_CLUSTER',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': ['spark-submit'] + self.args
            }
        }


class DataScienceStep(EMRStep):
    """Class representing a step performed by the data science code in EMR."""

    def __init__(self, step_name, script_name, fleet, config, on_failure="TERMINATE_CLUSTER"):
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
        data_bucket = f"{data_base_bucket}-{self.config.customer_id}-{self.config.environment}"
        data_bucket_uri = f"s3://{data_bucket}"
        data_base_uri = f"{data_bucket_uri}/processed/{self.fleet}"

        script_uri = f"{application_bucket_uri}/or/sparksubmits/pipelines/{self.fleet}/{self.script_name}"
        arguments = [
            script_uri,
            application_bucket_uri,
            data_base_uri,
            self.config.environment
        ]
        return {
            'Name': self.step_name,
            'ActionOnFailure': self.on_failure,
            'HadoopJarStep': {
                'Jar': jar_path,
                'Args': arguments
            }
        }
