# 更新日志（Changelog）

## [Unreleased] / [2.1.0] - 2026-01-06

### 🚀 新增功能（Added）

#### 1. Commons 公共配置扩展（Commons Configuration Extension）

* 新增 `cfgengine.extensions.commons` 扩展模块，用于加载**公共 / 共享配置**
* Commons 设计为：

  * 只读
  * 显式启用
  * 不自动注入当前项目配置空间

启用方式：

```python
from cfgengine import enable_commons

enable_commons()
```

---

#### 2. Nacos 配置中心支持（Nacos Support）

* Commons 扩展内置支持 **Nacos** 作为配置中心
* 通过 URI 方式声明配置来源，避免与业务代码强耦合

示例（环境变量）：

```bash
export CFGENGINE_COMMONS="nacos://127.0.0.1:8848?data_id=commons.json&group=DEFAULT_GROUP"
```

加载行为说明：

* 启动时从 Nacos 拉取 `commons.json`
* 解析后以 `DotDict` 形式缓存
* 不随项目配置 reload（后续可扩展）

---

#### 3. Jinja2 全局 commons 访问函数

* 向 Jinja2 环境注册全局函数 `commons()`

示例：

```jinja2
{{ commons("SR_HOST") }}
{{ commons("mysql.host", "127.0.0.1") }}
```

特性说明：

* 支持 `.` 访问嵌套配置
* 支持默认值
* 配置不存在且未提供默认值时抛出异常

---

#### 4. 显式启用与环境变量校验

* `enable_commons()` 在以下场景会给出明确提示：

  * 未设置 `CFGENGINE_COMMONS` 环境变量
* 目的：

  * 避免“悄悄启用”
  * 明确 commons 来源
  * 降低运维与排错成本

---

### 📝 设计说明（Notes）

* Commons **不会自动合并**进项目配置
* 推荐用法：

  * Commons：跨项目、跨服务的稳定公共配置
  * 项目配置：业务相关、可变配置
* 后续版本可能支持：

  * 多 commons 源
  * 配置刷新
  * commons → project 的显式映射

---

## [2.0.0] - 2025-01-03

### 🚀 新增功能（Added）

#### 1. Jinja2 模板支持（Jinja2 Template Support）

* 新增对 **Jinja2 模板** 的支持
* 支持在配置文件中使用表达式、函数与过滤器
* 支持 `NativeEnvironment`，允许返回原生 Python 对象（如 list / dict / int）

示例：

```json
{
  "home": "{{ env_var('HOME') }}",
  "value": "{{ 1 + 2 }}"
}
```

---

#### 2. 装饰器体系（Decorators）

##### `@register_global_function`

注册 Jinja2 全局函数：

```python
@register_global_function()
def my_function():
    return "Hello, World!"
```

---

##### `@register_filter`

注册 Jinja2 过滤器：

```python
@register_filter()
def uppercase(value):
    return value.upper()
```

---

##### `@returns_native_non_string`

标记函数返回原生非字符串对象：

```python
@returns_native_non_string
def import_py_obj(path):
    ...
```

---

### 📝 说明（Notes）

* 当使用非 `NativeEnvironment` 时会给出警告
* 增强配置解析与模板渲染的异常提示

---

### 🐞 修复（Fixed）

* 改进 `ConfigLoader` 的错误提示：

  * 文件不存在
  * 不支持的配置文件扩展名

---

## [1.0.2] - 2024-12-26

### 🔄 变更（Changed）

* 对外暴露 `register_parser` 接口

---

## [1.0.1] - 2024-12-25

### ➕ 新增（Added）

* 新增 `@register_parser` 装饰器，用于自动注册解析器

### 🔄 变更（Changed）

* `ConfigParser` 重命名为 `CfgParser`
* 内置解析器统一使用装饰器注册

### ⚠️ 弃用（Deprecated）

* 不再推荐手动调用：

```python
ParserRegistry.register_parser(extension, cls)
```

---
