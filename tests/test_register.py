import os
import unittest

from cfgengine.config_loader import ConfigLoader
from cfgengine.parser_registry import ConfigParser, ParserRegistry


class MockParser(ConfigParser):
    def parse(self, file_path):
        return {"mock": "data"}


class TestParserRegistry(unittest.TestCase):
    def test_register_and_get_parser(self):
        """Test registering and retrieving a parser."""
        ParserRegistry.register_parser("mock", MockParser)
        parser = ParserRegistry.get_parser("mock")
        self.assertIsInstance(parser, MockParser)

    def test_get_parser_not_registered(self):
        """Test retrieving a parser that is not registered."""
        with self.assertRaises(ValueError):
            ParserRegistry.get_parser("unknown")


class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        """Setup mock paths and environment variables."""
        self.default_current_path = ConfigLoader.DEFAULT_CURRENT_PATH
        self.default_home_path = ConfigLoader.DEFAULT_HOME_PATH
        self.default_env_var = ConfigLoader.DEFAULT_CONFIG_FILE_VAR
        self.mock_file_name = "config.mock"
        self.mock_file_path = f"./{self.mock_file_name}"

        # Create a mock file
        with open(self.mock_file_name, "w") as mock_file:
            mock_file.write("{}")

    def tearDown(self):
        """Cleanup mock files and environment variables."""
        if os.path.exists(self.mock_file_name):
            os.remove(self.mock_file_name)
        if self.default_env_var in os.environ:
            del os.environ[self.default_env_var]

    def test_check_file_path(self):
        """Test file path validation."""
        self.assertTrue(ConfigLoader.check_file_path(self.mock_file_path))
        self.assertFalse(ConfigLoader.check_file_path("/nonexistent/path"))

    def test_get_config_file_path_current_dir(self):
        """Test getting config file path from the current directory."""
        ConfigLoader.DEFAULT_CURRENT_PATH = self.mock_file_path
        self.assertEqual(ConfigLoader.get_config_file_path(), self.mock_file_path)

    def test_get_config_file_path_env_var(self):
        """Test getting config file path from environment variable."""
        os.environ[self.default_env_var] = self.mock_file_path
        self.assertEqual(ConfigLoader.get_config_file_path(), self.mock_file_path)

    def test_get_config_file_path_home_dir(self):
        """Test getting config file path from the home directory."""
        ConfigLoader.DEFAULT_HOME_PATH = self.mock_file_path
        self.assertEqual(ConfigLoader.get_config_file_path(), self.mock_file_path)

    def test_get_config_file_path_not_found(self):
        """Test raising exception when no config file is found."""
        ConfigLoader.DEFAULT_CURRENT_PATH = "/nonexistent/path"
        ConfigLoader.DEFAULT_HOME_PATH = "/nonexistent/home"
        with self.assertRaises(FileNotFoundError):
            ConfigLoader.get_config_file_path()

    def test_load_config(self):
        """Test loading configuration with a mock parser."""
        ParserRegistry.register_parser("mock", MockParser)
        ConfigLoader.DEFAULT_CURRENT_PATH = self.mock_file_path
        config = ConfigLoader.load_config()
        self.assertEqual(config, {"mock": "data"})


if __name__ == "__main__":
    unittest.main()
