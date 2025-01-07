"""
Module for configuration management.

This module provides utilities for loading and parsing configuration files
with support for custom parsers and registration.
"""

from .config_loader import ConfigLoader
from .default_parser import INIParser, JSONParser
from .parser import (
    CfgParser,
    DotDict,
    ParserRegistry,
    register_cfg_parser,
    register_filter,
    register_global_function,
    returns_native_non_string,
)

__all__ = [
    "CfgParser",
    "ConfigLoader",
    "INIParser",
    "JSONParser",
    "ParserRegistry",
    "register_filter",
    "register_global_function",
    "register_cfg_parser",
    "returns_native_non_string",
    "DotDict",
]

version = "2.0.0"
