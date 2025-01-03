# Changelog

## [2.0.0] - 2025-01-03

### Added Jinja2 support and some decorators

- **Jinja2 Template Support**:
  - Introduced support for parsing and rendering configuration files with Jinja2 templates.
  - Added the ability to utilize `NativeEnvironment` for rendering native Python objects.

- **Decorators**:

  - **`@register_global_function(env=_default_env, name=None)`**: Registers a global function for the Jinja2 environment.
    - **Usage Example**:

      ```python
      @register_global_function()
      def my_function():
          return "Hello, World!"
      ```

  - **`@register_filter(env=_default_env, name=None)`**: Registers a custom filter for the Jinja2 environment.
    - **Usage Example**:

      ```python
      @register_filter()
      def uppercase(value):
          return value.upper()
      ```

  - **`@returns_native_non_string(func)`**: Marks a function as returning a native (non-string) object for Jinja2 templates.
    - **Usage Example**:

      ```python
      @returns_native_non_string
      def import_py_obj(path):
          ...
      ```

### Notes

- Added warnings for using non-`NativeEnvironment` Jinja2 environments.
- Enhanced error handling for configuration parsing and template rendering.

### Fixed

- Improved error messages for file not found and invalid file extensions in `ConfigLoader`.

## [1.0.2] - 2024-12-26

### Changed: Register Parser

- Expose register_parser.

## [1.0.1] - 2024-12-25

### Added `@register_parser`

- Added the `@register_parser` decorator for automatically registering parser classes to ParserRegistry.

### Changed: Class Renaming and Registration Logic

- Renamed the following classes to avoid conflicts with standard library names:
  - `ConfigParser` -> `CfgParser`
- Applied the `@register_parser` decorator to all parser classes, simplifying the registration logic.

### Deprecated: Manual Parser Registration

- Manual invocation of the `ParserRegistry.register_parser(extension, cls)` method is now deprecated. Using the decorator for automatic registration is recommended.
