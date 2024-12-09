import os
import unittest

from cfgengine.config_loader import ConfigLoader
from cfgengine.parser_registry import ConfigParser, ParserRegistry


class MockParser(ConfigParser):
    """Mock parser for testing."""

    def parse(self, file_path):
        return {"mock_key": "mock_value"}


class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        """Setup mock files and environment variables for testing."""
        self.mock_file_name = "mock_config.mock"
        self.mock_file_path = f"./{self.mock_file_name}"
        self.env_var_name = ConfigLoader.DEFAULT_CONFIG_FILE_VAR

        # Create a mock configuration file
        with open(self.mock_file_path, "w") as mock_file:
            mock_file.write("{}")

    def tearDown(self):
        """Cleanup after each test."""
        if os.path.exists(self.mock_file_path):
            os.remove(self.mock_file_path)
        if self.env_var_name in os.environ:
            del os.environ[self.env_var_name]

    def test_check_file_path(self):
        """Test checking if a file path exists."""
        self.assertTrue(ConfigLoader.check_file_path(self.mock_file_path))
        self.assertFalse(ConfigLoader.check_file_path("/nonexistent/path"))

    def test_get_config_file_path_current_directory(self):
        """Test resolving the config file path in the current directory."""
        ConfigLoader.DEFAULT_CURRENT_PATH = self.mock_file_path
        self.assertEqual(ConfigLoader.get_config_file_path(), self.mock_file_path)

    def test_get_config_file_path_env_variable(self):
        """Test resolving the config file path via an environment variable."""
        os.environ[self.env_var_name] = self.mock_file_path
        self.assertEqual(ConfigLoader.get_config_file_path(), self.mock_file_path)

    def test_get_config_file_path_home_directory(self):
        """Test resolving the config file path in the home directory."""
        ConfigLoader.DEFAULT_HOME_PATH = self.mock_file_path
        self.assertEqual(ConfigLoader.get_config_file_path(), self.mock_file_path)

    def test_get_config_file_path_not_found(self):
        """Test behavior when no config file is found."""
        ConfigLoader.DEFAULT_CURRENT_PATH = "/nonexistent/current"
        ConfigLoader.DEFAULT_HOME_PATH = "/nonexistent/home"
        with self.assertRaises(FileNotFoundError):
            ConfigLoader.get_config_file_path()

    def test_load_config(self):
        """Test loading the configuration with a registered parser."""
        ParserRegistry.register_parser("mock", MockParser)
        ConfigLoader.DEFAULT_CURRENT_PATH = self.mock_file_path
        config = ConfigLoader.load_config()
        self.assertEqual(config, {"mock_key": "mock_value"})

    def test_load_config_unregistered_extension(self):
        """Test loading configuration with an unregistered file extension."""
        unregistered_file = "unregistered_config.unknown"
        with open(unregistered_file, "w") as f:
            f.write("{}")
        ConfigLoader.DEFAULT_CURRENT_PATH = unregistered_file

        with self.assertRaises(ValueError):
            ConfigLoader.load_config()

        os.remove(unregistered_file)

    def test_get_config_file_path_specific_file(self):
        """Test resolving a user-specified full file path."""
        result = ConfigLoader.get_config_file_path(self.mock_file_path)
        self.assertEqual(result, self.mock_file_path)

    def test_load_config_specific_file(self):
        """Test loading configuration from a user-specified full file path."""
        config = ConfigLoader.load_config(config_dir_or_path=self.mock_file_path)
        self.assertEqual(config, {"mock_key": "mock_value"})

    def test_get_config_file_path_invalid_specific_file(self):
        """Test handling when a user-specified file path does not exist."""
        invalid_file_path = "./nonexistent_config.json"
        with self.assertRaises(FileNotFoundError):
            ConfigLoader.get_config_file_path(config_dir_or_path=invalid_file_path)


if __name__ == "__main__":
    unittest.main()
