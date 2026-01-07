# Configuration Engine（cfgengine）

## 项目简介

**cfgengine** 是一个 **灵活、可扩展、配置即代码（Configuration as Code）** 的配置引擎，用于统一管理和解析多种来源、多种格式的配置数据。

它不仅支持传统的本地配置文件（JSON / INI 等），还支持：

* Jinja2 模板动态渲染
* 自定义全局函数与过滤器
* 远程配置中心（如 **Nacos**）
* 公共配置（commons）复用能力

cfgengine 的核心目标是：

> **让配置具备表达能力、依赖能力和可扩展能力，而不是简单的 key-value 文件。**

---

## 核心特性

### 1️⃣ 灵活的配置加载机制

* 支持从以下位置加载配置：

  * 用户指定路径
  * 当前目录
  * 用户 HOME 目录
  * 环境变量
  * 远程配置中心（Nacos）
* 根据文件扩展名自动选择解析器

---

### 2️⃣ 基于 Jinja2 的动态配置渲染

* 配置文件中的值支持 Jinja2 模板
* 支持表达式、函数调用、环境变量等

```json
{
  "home": "{{ env_var('HOME') }}",
  "workers": "{{ 2 * 4 }}"
}
```

---

### 3️⃣ 可扩展的解析器体系（Parser Registry）

* 内置支持：

  * JSON
  * INI
  * Nacos（JSON 格式）
* 支持通过装饰器轻松扩展新格式

---

### 4️⃣ 全局函数与过滤器注册

* 可向 Jinja2 环境注册：

  * 全局函数（globals）
  * 过滤器（filters）
* 支持标记返回 **非字符串的原生对象**

---

### 5️⃣ DotDict 支持（点号访问）

* 配置数据支持：

  * `dict["key"]`
  * `dict.key`
* 深层结构自动递归支持

---

### 6️⃣ 公共配置（Commons）支持（可选启用）

* 支持从 Nacos / 文件加载 **公共配置**
* 项目配置可通过 `commons` 引用公共配置
* 不会自动 merge，不污染项目配置

---

## 安装

```bash
pip install xr-cfgengine
```

---

## 快速开始

### 加载配置文件

```python
from xr.cfgengine import ConfigLoader

config = ConfigLoader.load_config("config.json")

print(config.app_name)
print(config.database.host)
```

---

## 使用 Jinja2 模板

### 示例配置（JSON）

```json
{
  "home": "{{ env_var('HOME') }}",
  "port": "{{ 8000 + 1 }}"
}
```

```python
config = ConfigLoader.load_config("config.json")
print(config.home)
print(config.port)
```

---

## Nacos 配置支持

### 1️⃣ 安装依赖

```bash
pip install xr-cfgengine[nacos]

```

---

### 2️⃣ 使用 Nacos 作为配置源

cfgengine 使用统一的 **URI Scheme** 来表示 Nacos 配置源：

```text
nacos://host:port?data_id=xxx&group=xxx&namespace=xxx
```

#### 示例

```python
config = ConfigLoader.load_config(
    "nacos://127.0.0.1:8848?data_id=app.json&group=DEFAULT_GROUP"
)
```

> 说明：
>
> * 当前 Nacos 配置内容 **仅支持 JSON 格式**
> * 解析后仍会经过 Jinja2 渲染流程

---

## 公共配置（Commons）机制

### 设计理念

* commons 是 **配置依赖源**，不是项目配置的一部分
* 不自动 merge，避免隐式覆盖
* 通过显式引用保证可读性和可维护性

---

### 启用 commons 支持

```python
from xr.cfgengine import enable_commons

enable_commons()
```

设置公共配置来源（例如 Nacos）：

```bash
export CFGENGINE_COMMONS="nacos://127.0.0.1:8848?data_id=commons.json&group=DEFAULT_GROUP"
```

---

### 使用方式（推荐）

```yaml
SR_HOST_IP: {{ commons.SR_HOST }}
MYSQL_HOST: {{ commons.mysql.host }}
```

---

### 兼容函数调用方式

```yaml
REDIS_PORT: {{ commons("redis.port", 6379) }}
```

> `commons` 同时支持：
>
> * 属性访问（DSL 风格）
> * 函数调用（支持 default）

---

## 装饰器说明

### `@register_cfg_parser`

注册新的配置解析器。

```python
from xr.cfgengine.parser import CfgParser, register_cfg_parser

@register_cfg_parser("yaml")
class YAMLParser(CfgParser):
    def load(self):
        import yaml
        with open(self.file_path) as f:
            return yaml.safe_load(f)
```

---

### `@register_global_function`

注册 Jinja2 全局函数。

```python
from xr.cfgengine import register_global_function, returns_native_non_string

@register_global_function()
@returns_native_non_string
def multiply(a, b):
    return a * b
```

配置中使用：

```json
{
  "result": "{{ multiply(2, 3) }}"
}
```

---

### `@register_filter`

注册 Jinja2 过滤器。

```python
from xr.cfgengine import register_filter

@register_filter()
def upper(value):
    return value.upper()
```

---

### `@returns_native_non_string`

标记函数返回非字符串原生对象，避免被强制转为字符串。

---

## 核心类说明

### `ConfigLoader`

负责定位并加载配置源。

* `set_default_file_name()`
* `get_config_file_path()`
* `load_config()`

---

### `CfgParser`

所有解析器的抽象基类。

* `load()`：加载原始配置
* `parse()`：Jinja2 渲染 + 解析

---

### `ParserRegistry`

管理扩展名与解析器的映射关系。

---

### `DotDict`

支持点号访问的字典结构。

---

## 最佳实践建议

1. 公共配置建议只存放 **稳定、不频繁变动** 的内容
2. 项目配置中显式引用 commons，避免隐式依赖
3. 不同环境（dev / prod）使用不同的 Nacos namespace
4. 不建议在配置中写复杂业务逻辑
