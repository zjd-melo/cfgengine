import logging
from configparser import ConfigParser

from cfgengine.parser_registry import ParserRegistry

_logger = logging.getLogger(__name__)


class JSONParser(ConfigParser):
    def parse(self, file_path):
        import json

        _logger.debug(f"using config file {file_path}")

        with open(file_path, "r") as f:
            return json.load(f)


class INIParser(ConfigParser):
    def parse(self, file_path):
        import configparser

        _logger.debug(f"using config file {file_path}")
        config = configparser.ConfigParser()
        config.read(file_path)
        return {section: dict(config[section]) for section in config.sections()}


ParserRegistry.register_parser("json", JSONParser)
ParserRegistry.register_parser("ini", INIParser)
ParserRegistry.register_parser("INI", INIParser)
