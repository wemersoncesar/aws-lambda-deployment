"""
Module to manage configuration settings from both JSON file and environment variables.
"""

import os
from pathlib import Path
import json


class Config:
    """
    A class to manage configuration settings from both JSON file and environment variables.

    Attributes
    ----------
    config : dict
        A dictionary containing configuration key-value pairs.
    """

    def __init__(self, config_file_path=None):
        """
        Initialize the Config object.

        Parameters
        ----------
        config_file_path : str, optional
            Path to the JSON configuration file.
        """
        self.__config = {}
        if not config_file_path:
            config_file_path = os.path.join(
                Path(os.path.abspath(__file__)).parent.parent, "config.json"
            )
        self._load_from_json(config_file_path)
        self._load_from_env()

    def _load_from_json(self, config_file_path):
        """
        Load environment variable names from a JSON configuration file.

        Parameters
        ----------
        config_file_path : str
            Path to the JSON configuration file.
        """
        with open(config_file_path, "r") as file:
            json_data = json.load(file)
            self.environment_variables = json_data.get("environment_variables")
            self.job_args = json_data.get("jobArgs", {})
            self.__config["BUCKET_BASE_NAME"] = json_data.get("bucket_base_name")

    def _load_from_env(self):
        """
        Load configuration settings from environment variables.
        """
        set_env_variables = os.environ.keys()
        unset_env_variables = [
            var for var in self.environment_variables if var not in set_env_variables
        ]
        if unset_env_variables:
            unset_vars = ", ".join(unset_env_variables)
            raise KeyError(
                f"Some expected environment variables ({unset_vars}) are not defined."
            )
        for env_var in self.environment_variables:
            self.__config[env_var] = os.environ[env_var]

    def get(self, key, default=None):
        """
        Get the value for a configuration key.

        Parameters
        ----------
        key : str
            The configuration key.
        default : any, optional
            Default value to return if key is not found.

        Returns
        -------
        any
            The value corresponding to the key, or the default value if key is not found.
        """
        return self.__config.get(key, default)

    def __getitem__(self, key):
        """
        Get the value for a configuration key using square bracket notation.

        Parameters
        ----------
        key : str
            The configuration key.

        Returns
        -------
        any
            The value corresponding to the key.

        Raises
        ------
        KeyError
            If the key is not found in the configuration.
        """
        return self.__config[key]

    def __getattr__(self, key):
        """
        Get the value for a configuration key using attribute notation.

        Parameters
        ----------
        key : str
            The configuration key.

        Returns
        -------
        any
            The value corresponding to the key.

        Raises
        ------
        AttributeError
            If the key is not found in the configuration.
        """
        if key.upper() in self.__config:
            return self.__config[key.upper()]
        else:
            raise AttributeError(f"'Config' object has no attribute '{key}'")
