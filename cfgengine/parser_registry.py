from abc import ABC, abstractmethod


class CfgParser(ABC):
    @abstractmethod
    def parse(self, file_path):
        """Parse the configuration file and return the data as a dictionary."""


class ParserRegistry:
    _parsers = {}

    @classmethod
    def register_parser(cls, extension, parser_clz):
        """Register a parser for a specific file extension."""
        cls._parsers[extension] = parser_clz

    @classmethod
    def get_parser(cls, extension):
        """Get the parser for a specific file extension."""
        parser_class = cls._parsers.get(extension)
        if not parser_class:
            raise ValueError(f"No parser registered for extension: {extension}")
        return parser_class()


def register_cfg_parser(extension):

    def decorator(parser_cls):
        ParserRegistry.register_parser(extension, parser_cls)
        return parser_cls

    return decorator
