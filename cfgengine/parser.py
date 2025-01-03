import importlib
import os
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict

from jinja2 import UndefinedError, nodes
from jinja2.nativetypes import NativeEnvironment

# Default Jinja2 NativeEnvironment
_default_env = NativeEnvironment()


def custom_warning_format(message, category, filename, lineno, line=None):
    return f"{filename}:{lineno}: {category.__name__}: {message}\n"


warnings.formatwarning = custom_warning_format


class CfgParser(ABC):
    """
    Abstract base class for configuration parsers.
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self, jinja_env=_default_env):
        """
        Parse the configuration file and return the data as a DotDict.
        If the provided Jinja environment is not a NativeEnvironment, issue a warning.
        """
        if not issubclass(jinja_env.__class__, NativeEnvironment):
            warnings.warn(
                "The provided Jinja environment is not NativeEnvironment. "
                "This may result in rendering output as strings only. "
                "If you need native Python objects, consider using NativeEnvironment.",
                UserWarning,
            )
        cfg = self.load()
        ret = Parser(jinja_env).parse_config(cfg)
        return DotDict(ret)

    @abstractmethod
    def load(self):
        """
        Load and return the configuration as a dictionary.
        Must be implemented by subclasses.
        """
        pass


class ParserRegistry:
    """
    Registry for associating file extensions with parser classes.
    """

    _parsers = {}

    @classmethod
    def register_parser(cls, extension, parser_clz):
        """Register a parser for a specific file extension."""
        cls._parsers[extension] = parser_clz

    @classmethod
    def get_parser_class(cls, extension):
        """Retrieve the parser class associated with a file extension."""
        parser_class = cls._parsers.get(extension)
        if not parser_class:
            raise ValueError(f"No parser registered for extension: {extension}")
        return parser_class


class ParserError(Exception):
    """
    Custom exception for parser-related errors.
    """

    pass


class DotDict(dict):
    """
    A dictionary that allows attribute-style access.
    """

    def __init__(self, dictionary):
        super().__init__(dictionary)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DotDict(value)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"DotDict object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(f"DotDict object has no attribute '{name}'")


class FunctionCallExtractor:
    """
    Extracts function calls from Jinja2 templates.
    """

    def __init__(self, env):
        self.env = env

    def extract(self, template_str):
        """
        Parse a template string and extract all function calls defined in the Jinja
        environment.
        """
        ast = self.env.parse(template_str)
        calls = defaultdict(list)

        def visit_node(node):
            if isinstance(node, nodes.Call):
                if (
                    isinstance(node.node, nodes.Name)
                    and node.node.name in self.env.globals
                ):
                    func_name = node.node.name
                    # args = [arg.as_const() for arg in node.args]
                    calls[func_name].append(func_name)
            for child in node.iter_child_nodes():
                visit_node(child)

        visit_node(ast)
        return calls


class Parser:
    """
    Responsible for parsing configuration data using Jinja2 templates.
    """

    def __init__(self, env):
        self.env = env
        self.call_extractor = FunctionCallExtractor(env)

    def parse_config(self, config):
        """Parse a configuration dictionary."""
        parsed_config = {}
        for key, value in config.items():
            parsed_config[key] = self.parse_value(value, key)
        return parsed_config

    def parse_value(self, value, key):
        """Recursively parse values in the configuration."""
        if isinstance(value, str):
            return self.parse_string(value, key)
        elif isinstance(value, list):
            return self.parse_list(value, key)
        elif isinstance(value, dict):
            return self.parse_config(value)
        else:
            return value

    def parse_string(self, value, key):
        """
        Parse a string value as a Jinja2 template.
        Raises a ParserError if multiple non-string-returning functions are detected.
        """
        try:
            function_calls = self.call_extractor.extract(value)
            non_string_functions = [
                func
                for func in function_calls
                if getattr(self.env.globals.get(func), "returns_native", False)
            ]

            if len(non_string_functions) > 1:
                raise ParserError(
                    f"Template error for key '{key}': Multiple non-string-returning"
                    f"functions cannot be used together in the same template. Found: "
                    f"{', '.join(non_string_functions)}"
                )

            return self.env.from_string(value).render()
        except UndefinedError as e:
            raise ValueError(f"Error rendering template for key '{key}': {e}")

    def parse_list(self, lst, key):
        """Parse a list of values."""
        return [self.parse_value(item, f"{key}[{i}]") for i, item in enumerate(lst)]


def register_global_function(env=_default_env, name=None):
    """
    Decorator to register a global function in the Jinja environment.
    """

    def decorator(func):
        _name = name if name is not None else func.__name__
        env.globals[_name] = func
        return func

    return decorator


def register_filter(env=_default_env, name=None):
    """
    Decorator to register a filter in the Jinja environment.
    """

    def decorator(func):
        _name = name if name is not None else func.__name__
        env.filters[_name] = func
        return func

    return decorator


def register_cfg_parser(extension):
    """
    Decorator to register a configuration parser for a specific file extension.
    """

    def decorator(parser_cls):
        ParserRegistry.register_parser(extension, parser_cls)
        return parser_cls

    return decorator


def returns_native_non_string(func):
    """
    Decorator to mark a function as returning a native (non-string) object.
    """
    func.returns_native = True
    return func


@register_global_function()
@returns_native_non_string
def import_py_obj(path):
    """
    Import a Python module or object by its dotted path.
    """
    try:
        if "." not in path:
            return importlib.import_module(path)
        else:
            module_name, obj = path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            return getattr(module, obj)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Unable to import '{path}': {e}")


@register_global_function()
def env_var(var_name, default=""):
    """
    Retrieve an environment variable, returning a default value if not found.
    """
    return os.getenv(var_name, default)
