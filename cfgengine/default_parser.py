import logging

from cfgengine.parser import CfgParser, register_cfg_parser

_logger = logging.getLogger(__name__)


@register_cfg_parser("json")
class JSONParser(CfgParser):
    """Parser for JSON configuration files."""

    def load(self):
        import json

        _logger.info(f"Loading JSON configuration from {self.file_path}")
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            _logger.error(f"Failed to parse JSON configuration: {e}")
            raise ValueError(f"Invalid JSON configuration in {self.file_path}") from e
        except FileNotFoundError:
            _logger.error(f"Configuration file not found: {self.file_path}")
            raise
        except Exception as e:
            _logger.error(f"Unexpected error while loading JSON: {e}")
            raise


@register_cfg_parser("ini")
@register_cfg_parser("INI")
class INIParser(CfgParser):
    """Parser for INI configuration files."""

    def load(self):
        import configparser

        _logger.info(f"Loading INI configuration from {self.file_path}")
        try:
            config = configparser.ConfigParser()
            config.read(self.file_path)
            return {section: dict(config[section]) for section in config.sections()}
        except configparser.Error as e:
            _logger.error(f"Failed to parse INI configuration: {e}")
            raise ValueError(f"Invalid INI configuration in {self.file_path}") from e
        except FileNotFoundError:
            _logger.error(f"Configuration file not found: {self.file_path}")
            raise
        except Exception as e:
            _logger.error(f"Unexpected error while loading INI: {e}")
            raise
