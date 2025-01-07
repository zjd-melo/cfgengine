# Configuration Engine

## Overview

This project provides a robust and extensible configuration engine for managing configuration files in various formats (e.g., JSON, INI). It supports custom parsing, Jinja2 template rendering, and dynamic function registration for templates. The library is highly extensible, allowing users to add support for additional file formats and integrate custom global functions or filters.

## Features

1. **Flexible Configuration Loading**:
   - Load configurations from predefined locations or user-specified paths.
   - Automatically detect and parse configuration files based on their extensions.

2. **Dynamic Template Rendering**:
   - Use Jinja2 templates to render configuration values dynamically.

3. **Extensible Parsing**:
   - Easily add support for new configuration formats by registering custom parsers.

4. **Global Function and Filter Registration**:
   - Add reusable functions and filters for use in Jinja2 templates.

5. **DotDict Support**:
   - Access configuration data using both dictionary and attribute-style access.

## Installation

Clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Loading a Configuration File

```python
from cfgengine import ConfigLoader

# Load a configuration file (searches default paths if not specified)
config_data = ConfigLoader.load_config(config_dir_or_path="/path/to/config")

# Access configuration values
print(config_data.some_key)
```

### Using Jinja2 Templates in Configuration Files

Example JSON file:

```json
{
  "key1": "{{ env_var('HOME') }}",
  "key2": "{{ 3 + 5 }}"
}
```

Loading and rendering the file:

```python
config_data = ConfigLoader.load_config("config.json")
print(config_data.key1)  # Outputs the HOME environment variable
print(config_data.key2)  # Outputs 8
```

## Decorators and Their Usage

### `@register_cfg_parser`

Register a parser for a specific file extension.

#### Example

```python
from cfgengine.parser import CfgParser, register_cfg_parser

@register_cfg_parser("yaml")
class YAMLParser(CfgParser):
    def load(self):
        import yaml
        with open(self.file_path, "r") as f:
            return yaml.safe_load(f)
```

### `@register_global_function`

Register a global function for use in Jinja2 templates.

#### Example

```python
from cfgengine import register_global_function, returns_native_non_string

@register_global_function()
@returns_native_non_string
def multiply(a, b):
    return a * b

# Usage in a configuration file
{
  "result": "{{ multiply(2, 3) }}"
}
```

### `@register_filter`

Register a custom filter for Jinja2 templates.

#### Example

```python
from cfgengine import register_filter

@register_filter()
def uppercase(value):
    return value.upper()

# Usage in a configuration file
{
  "name": "{{ 'hello' | uppercase }}"
}
```

### `@returns_native_non_string`

Mark a global function as returning a native (non-string) object.

#### Example

```python
from cfgengine.config_loader import returns_native_non_string

@register_global_function()
@returns_native_non_string
def return_list():
    return [1, 2, 3]

# Usage in a configuration file
{
  "data": "{{ return_list() }}"
}
```

## Key Classes

### `ConfigLoader`

Handles loading configuration files and determining the file path.

#### Key Methods

- `set_default_file_name(file_name)`: Updates the default configuration file name.
- `get_config_file_path(config_dir_or_path)`: Resolves the configuration file path.
- `load_config(config_dir_or_path, jinja2_env)`: Loads and parses the configuration file.

### `DotDict`

A dictionary with attribute-style access.

#### Example

```python
data = DotDict({"key": "value"})
print(data.key)  # Outputs "value"
data.new_key = "new_value"
print(data["new_key"])  # Outputs "new_value"
```

### `ParserRegistry`

Manages the registration of parsers for file extensions.

#### Key Methods

- `register_parser(extension, parser_clz)`: Registers a parser for a file extension.
- `get_parser_class(extension)`: Retrieves the parser class for a given extension.

### `CfgParser`

Abstract base class for all configuration parsers.

#### Key Methods

- `parse(jinja_env)`: Parses the configuration using Jinja2 templates.
- `load()`: Abstract method for loading raw configuration data.

## Notes and Best Practices

1. Ensure the appropriate parser is registered for the file format you intend to use.
2. Always validate Jinja2 templates in your configuration files to avoid runtime errors.
3. Use the `returns_native_non_string` decorator when functions return non-string objects to avoid unintended parsing issues.
4. To extend the library, create custom parsers and register them using `@register_cfg_parser`.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Changelog

For the full list of changes, see the [Changelog](CHANGELOG.md).
