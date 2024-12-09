import os
import sys

from cfgengine.parser_registry import ParserRegistry
from cfgengine.utils import DotDict


class ConfigLoader:
    DEFAULT_CONFIG_FILE_VAR = "CFGENGINE_CONF"
    DEFAULT_CONFIG_FILE_NAME = "config_engine.json"
    DEFAULT_HOME_PATH = os.path.expanduser(f"~/.config/{DEFAULT_CONFIG_FILE_NAME}")
    DEFAULT_CURRENT_PATH = f"./{DEFAULT_CONFIG_FILE_NAME}"

    @staticmethod
    def set_default_file_name(file_name):
        """Set a new default configuration file name."""
        ConfigLoader.DEFAULT_CONFIG_FILE_NAME = file_name
        ConfigLoader.DEFAULT_HOME_PATH = os.path.expanduser(f"~/.config/{file_name}")
        ConfigLoader.DEFAULT_CURRENT_PATH = f"./{file_name}"

    @staticmethod
    def check_file_path(path):
        """Validate if the provided path exists and is a file."""
        return bool(path and os.path.isfile(path))

    @staticmethod
    def get_config_file_path(config_dir_or_path=None):
        if config_dir_or_path:
            # Check if it's a full path to a file
            if os.path.isfile(config_dir_or_path):
                sys.stdout.write(
                    f"[INFO] Using configuration file: {config_dir_or_path}\n"
                )
                return config_dir_or_path

            # Treat as a directory and append the default file name
            custom_path = os.path.join(
                config_dir_or_path, ConfigLoader.DEFAULT_CONFIG_FILE_NAME
            )
            if ConfigLoader.check_file_path(custom_path):
                sys.stdout.write(f"[INFO] Using configuration file: {custom_path}\n")
                return custom_path
            raise FileNotFoundError(f"Specified path is invalid: {config_dir_or_path}")

        # Default search paths
        paths = [
            ConfigLoader.DEFAULT_CURRENT_PATH,
            os.environ.get(ConfigLoader.DEFAULT_CONFIG_FILE_VAR),
            ConfigLoader.DEFAULT_HOME_PATH,
        ]
        for path in paths:
            if ConfigLoader.check_file_path(path):
                sys.stdout.write(f"[INFO] Using configuration file: {path}\n")
                return path

        raise FileNotFoundError(
            "Configuration file not found. Please provide a configuration file in one of the following paths:\n"
            f"    1. Specified path or directory: {config_dir_or_path or 'Not provided'}\n"
            f"    2. Current directory: {ConfigLoader.DEFAULT_CURRENT_PATH}\n"
            f"    3. Environment variable {ConfigLoader.DEFAULT_CONFIG_FILE_VAR}: {os.environ.get(ConfigLoader.DEFAULT_CONFIG_FILE_VAR) or 'Not set'}\n"
            f"    4. User home directory: {ConfigLoader.DEFAULT_HOME_PATH}\n"
        )

    @staticmethod
    def load_config(config_dir_or_path=None):
        """
        Load the configuration from the specified directory, file path, or default paths.

        Parameters:
            config_dir_or_path: The directory or full path specified by the user.

        Returns:
            Parsed configuration as a dictionary.
        """
        config_path = ConfigLoader.get_config_file_path(config_dir_or_path)
        _, ext = os.path.splitext(config_path)
        ext = ext.lstrip(".")
        parser = ParserRegistry.get_parser(ext)
        ret = parser.parse(config_path)
        return DotDict(ret)
