"""
配置管理模块。

该模块提供用于加载和解析配置文件的通用工具，
支持多种配置格式（如 JSON / INI），并支持通过注册机制
扩展自定义解析器、过滤器和全局函数。
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
    # 配置解析器基类
    "CfgParser",
    # 配置加载入口
    "ConfigLoader",
    # 内置解析器
    "INIParser",
    "JSONParser",
    # 解析器注册表
    "ParserRegistry",
    # Jinja 过滤器注册装饰器
    "register_filter",
    # Jinja 全局函数注册装饰器
    "register_global_function",
    # 配置解析器注册装饰器
    "register_cfg_parser",
    # 标记返回原生（非字符串）对象的装饰器
    "returns_native_non_string",
    # 支持属性访问的字典结构
    "DotDict",
]


def enable_commons():
    """
    启用内置的 commons 公共配置支持。

    该函数会加载 cfgengine.extensions.commons 模块，
    从而向 Jinja 环境中注册 commons() 全局函数。

    说明：
    - 默认不启用，避免 cfgengine 对具体配置中心产生强依赖
    - 项目侧按需调用一次即可生效
    - 如果未配置 CFGENGINE_COMMONS 环境变量，会给出提示信息
    """
    import os
    import warnings

    if not os.getenv("CFGENGINE_COMMONS"):
        warnings.warn(
            "CFGENGINE_COMMONS 环境变量未配置，commons() 将使用默认配置地址。\n"
            "示例：\n"
            "  export CFGENGINE_COMMONS='nacos://127.0.0.1:8848?"
            "data_id=commons.json&group=DEFAULT_GROUP'",
            UserWarning,
        )

    import xr.cfgengine.extensions.commons  # noqa


version = "2.1.0"
