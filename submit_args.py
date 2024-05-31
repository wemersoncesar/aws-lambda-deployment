from app.config import Config


class SubmitArgs:

    def __init__(self, config: Config):
        self.config = config

    def split_if_needed(self, arg):
        if " " in arg:
            return arg.split(" ")
        return [arg]

    def get_job_args(self, job_name):
        args_list = []
        job_args = self.config.job_args.get(job_name, {})

        args_list.extend(self.get_runtime_arguments(job_args))
        args_list.extend(self.get_jar_arguments(job_args))
        args_list.extend(self.get_main_py_file(job_args))
        args_list.extend(self.get_application_arguments(job_args))
        args_list.extend(self.get_secrets_arguments(job_args))

        return args_list

    def get_runtime_arguments(self, job_args):
        runtime_args_list = []
        if "runtimeArguments" in job_args and isinstance(
            job_args["runtimeArguments"], list
        ):
            for arg in job_args["runtimeArguments"]:
                runtime_args_list.extend(self.split_if_needed(arg))
        return runtime_args_list

    def get_jar_arguments(self, job_args):
        jar_args_list = []
        if "applicationArtifact" in job_args and isinstance(
            job_args["applicationArtifact"], list
        ):
            jar_args_list.extend(job_args["applicationArtifact"])
        return jar_args_list

    def get_main_py_file(self, job_args):
        jar_args_list = []
        if "mainPyFile" in job_args and isinstance(job_args["mainPyFile"], list):
            jar_args_list.extend(job_args["mainPyFile"])
        return jar_args_list

    def get_application_arguments(self, job_args):
        application_args_list = []
        if "applicationArguments" in job_args and isinstance(
            job_args["applicationArguments"], list
        ):
            for arg in job_args["applicationArguments"]:
                application_args_list.extend(self.split_if_needed(arg))
        return application_args_list

    def get_secrets_arguments(self, job_args):
        secrets_args_list = []
        if "secrets" in job_args and isinstance(job_args["secrets"], list):
            for secret in job_args["secrets"]:
                argument = secret.get("argument")
                env_var_name = secret.get("envVar")
                value_from_env = getattr(
                    self.config,
                    env_var_name,
                    f"The Variable {env_var_name} is NOT defined",
                )
                secrets_args_list.append(f"{argument}")
                secrets_args_list.append(f"{value_from_env}")
        return secrets_args_list
