import logging

from cfgengine.parser_registry import CfgParser, register_cfg_parser

_logger = logging.getLogger(__name__)


@register_cfg_parser("json")
class JSONParser(CfgParser):
    def parse(self, file_path):
        import json

        _logger.debug(f"using config file {file_path}")

        with open(file_path, "r") as f:
            return json.load(f)


@register_cfg_parser("ini")
@register_cfg_parser("INI")
class INIParser(CfgParser):
    def parse(self, file_path):
        import configparser

        _logger.debug(f"using config file {file_path}")
        config = configparser.ConfigParser()
        config.read(file_path)
        return {section: dict(config[section]) for section in config.sections()}
