# Changelog

## [1.0.1] - 2024-12-25

### Added

- Added the `@register_parser` decorator for automatically registering parser classes to ParserRegistry.

### Changed

- Renamed the following classes to avoid conflicts with standard library names:
  - `ConfigParser` -> `CfgParser`
- Applied the `@register_parser` decorator to all parser classes, simplifying the registration logic.

### Deprecated

- Manual invocation of the `ParserRegistry.register_parser(extension, cls)` method is now deprecated. Using the decorator for automatic registration is recommended.
