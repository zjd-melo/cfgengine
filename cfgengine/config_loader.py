import os
import sys

from cfgengine.parser import ParserRegistry


class ConfigLoader:
    """
    Handles loading configuration files by searching default paths or a specified
    directory/path.
    """

    DEFAULT_CONFIG_FILE_VAR = "CFGENGINE_CONF"
    DEFAULT_CONFIG_FILE_NAME = "config_engine.json"
    DEFAULT_HOME_PATH = os.path.expanduser(f"~/.config/{DEFAULT_CONFIG_FILE_NAME}")
    DEFAULT_CURRENT_PATH = f"./{DEFAULT_CONFIG_FILE_NAME}"

    @classmethod
    def set_default_file_name(cls, file_name):
        """
        Set a new default configuration file name and update related paths.

        Parameters:
            file_name (str): New default configuration file name.
        """
        cls.DEFAULT_CONFIG_FILE_NAME = file_name
        cls.DEFAULT_HOME_PATH = os.path.expanduser(f"~/.config/{file_name}")
        cls.DEFAULT_CURRENT_PATH = f"./{file_name}"

    @staticmethod
    def check_file_path(path):
        """
        Validate if the provided path exists and is a file.

        Parameters:
            path (str): The file path to check.

        Returns:
            bool: True if the path exists and is a file, False otherwise.
        """
        return os.path.isfile(path) if path else False

    @classmethod
    def get_config_file_path(cls, config_dir_or_path=None):
        """
        Determine the configuration file path to use.

        Parameters:
            config_dir_or_path (str, optional): User-specified directory or file path.

        Returns:
            str: Resolved configuration file path.

        Raises:
            FileNotFoundError: If no valid configuration file is found.
        """
        if config_dir_or_path:
            # Check if it's a full path to a file
            if cls.check_file_path(config_dir_or_path):
                sys.stdout.write(
                    f"[INFO] Using configuration file: {config_dir_or_path}\n"
                )
                return config_dir_or_path

            # Treat as a directory and append the default file name
            custom_path = os.path.join(config_dir_or_path, cls.DEFAULT_CONFIG_FILE_NAME)
            if cls.check_file_path(custom_path):
                sys.stdout.write(f"[INFO] Using configuration file: {custom_path}\n")
                return custom_path

            raise FileNotFoundError(f"Specified path is invalid: {config_dir_or_path}")

        # Default search paths
        paths = [
            cls.DEFAULT_CURRENT_PATH,
            os.environ.get(cls.DEFAULT_CONFIG_FILE_VAR),
            cls.DEFAULT_HOME_PATH,
        ]

        for path in paths:
            if cls.check_file_path(path):
                sys.stdout.write(f"[INFO] Using configuration file: {path}\n")
                return path

        raise FileNotFoundError(
            "Configuration file not found. Please provide a configuration file in one "
            "of the following paths:\n"
            f"    1. Specified path or directory: {config_dir_or_path or 'Not provided'}\n"
            f"    2. Current directory: {cls.DEFAULT_CURRENT_PATH}\n"
            f"    3. Environment variable {cls.DEFAULT_CONFIG_FILE_VAR}: "
            f"{os.environ.get(cls.DEFAULT_CONFIG_FILE_VAR) or 'Not set'}\n"
            f"    4. User home directory: {cls.DEFAULT_HOME_PATH}\n"
        )

    @classmethod
    def load_config(cls, config_dir_or_path=None, jinja2_env=None):
        """
        Load the configuration from the specified directory, file path, or default
        paths.

        Parameters:
            config_dir_or_path (str, optional): The directory or full path specified
            by the user.
            jinja2_env: The jiaja2 Environment.

        Returns:
            dict: Parsed configuration data.

        Raises:
            FileNotFoundError: If no configuration file is found.
            ValueError: If no parser is registered for the file extension.
        """
        config_path = cls.get_config_file_path(config_dir_or_path)
        _, ext = os.path.splitext(config_path)
        ext = ext.lstrip(".")

        try:
            parser_class = ParserRegistry.get_parser_class(ext)
        except ValueError as e:
            raise ValueError(f"Error retrieving parser for extension '{ext}': {e}")

        parser = parser_class(config_path)
        ret = parser.parse(jinja2_env) if jinja2_env else parser.parse()
        return ret
