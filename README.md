# cfgengine

>`cfgengine` is a simple Python library designed to manage and load configuration files. It supports both JSON and INI formats, allows easy integration into projects.

## Features

- Load and parse JSON and INI configuration files.
- Support for dot-access to configuration values (e.g., config.host).
- Flexible configuration loading with support for custom directories and default paths.
- Custom Parsers: Easily register and use custom parsers for specific configuration formats.

## Installation

You can install cfgengine using pip:

`pip install git+https://github.com/zjd-melo/cfgengine.git`

## Usage

### 1. Load Configuration

You can load your configuration from a file (JSON or INI) using the `ConfigLoader`. The values in the configuration file can be accessed via dot notation or dictionary-style indexing.

```python
from cfgengine import ConfigLoader

# Load configuration (auto-detects JSON or INI format based on file extension)
config = ConfigLoader.load_config("config.json")

# Access values using dot notation
print(config.host)  # e.g., localhost

# Or use dictionary-style access
print(config["port"])  # e.g., 8080
```

### 2. Dot Access Configuration

With `cfgengine`, you can access values from your configuration file using dot notation, making it intuitive and easy to work with:

```python
config = {
    'host': 'localhost',
    'port': 8080,
    'database': {
        'user': 'admin',
        'password': 'securepassword'
    }
}

# Convert the dictionary to a DotDict object
from cfgengine import DotDict
config = DotDict(config)

# Dot notation access
print(config.host)  # Output: localhost
print(config.database.user)  # Output: admin

# Dictionary-style access
print(config["port"])  # Output: 8080
```

### 3. Custom Directory for Config File

You can specify a custom directory to load the configuration file:

```python
# explict 
# this will using /path/to/custom/directory/cfgengine.json
config = ConfigLoader.load_config(config_dir_or_path="/path/to/custom/directory")
print(config.host)
```

You can easily create and register custom parsers for any specific configuration file format. Custom parsers allow you to extend the library to support formats beyond the default JSON and INI.

### 4. Custom Parsers

#### 4.1 Registering a Custom Parser

To create a custom parser, define a new parser class that inherits from CfgParser and implement the parse method. Once the parser is created, register it with ParserRegistry.

```python
from cfgengine import CfgParser, register_cfg_parser
import yaml

# Define a custom parser for YAML files
@register_cfg_parser('yaml')
class YAMLParser(CfgParser):
    def parse(self, file_path):
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)

# Deprecated way
# Register the custom parser
ParserRegistry.register_parser("yaml", YAMLParser)
```

#### 4.2 Using a Custom Parser

Once you've registered a custom parser, you can use it just like the default parsers for JSON and INI. Simply provide the appropriate file extension when calling ConfigLoader.load_config().

```python
# Load configuration from a YAML file
config = ConfigLoader.load_config("config.yaml")

# Access configuration values
print(config.host)
print(config.database.user)
```

This way, you can easily add support for other formats like YAML, TOML, or any custom format you need by creating a parser class.

## Changelog

For the full list of changes, see the [Changelog](CHANGELOG.md).
