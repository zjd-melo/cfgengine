# Changelog

## [1.0.1] - 2024-12-25

### Added

- 新增了 `@register_parser` 装饰器，用于自动注册解析器类到 `ParserRegistry` 中。

### Changed

- 重命名了以下类以避免和标准库中的类重名：
  - `ConfigParser` -> `CfgParser`
- 在所有解析器类上添加了 `@register_parser` 装饰器，简化了注册逻辑。

### Deprecated

- `ParserRegistry.register_parser(extension, cls)` 方法的手动调用方式，推荐使用装饰器自动注册。
