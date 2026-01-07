import importlib
import os
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict

from jinja2 import UndefinedError, nodes
from jinja2.nativetypes import NativeEnvironment

# 默认使用的 Jinja2 NativeEnvironment（支持返回原生 Python 类型）
_default_env = NativeEnvironment()


def custom_warning_format(message, category, filename, lineno, line=None):
    """
    自定义 warnings 的输出格式
    """
    return f"{filename}:{lineno}: {category.__name__}: {message}\n"


# 覆盖 warnings 的默认格式化方式
warnings.formatwarning = custom_warning_format


class CfgParser(ABC):
    """
    配置解析器的抽象基类
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self, jinja_env=_default_env):
        """
        解析配置文件并返回 DotDict 对象。

        如果传入的 Jinja 环境不是 NativeEnvironment，
        将发出警告，因为这可能导致渲染结果全部为字符串。
        """
        if not issubclass(jinja_env.__class__, NativeEnvironment):
            warnings.warn(
                "传入的 Jinja 环境不是 NativeEnvironment，"
                "这可能导致模板渲染结果只能是字符串。"
                "如果需要返回原生 Python 对象，请使用 NativeEnvironment。",
                UserWarning,
            )
        cfg = self.load()
        ret = Parser(jinja_env).parse_config(cfg)
        return DotDict(ret)

    @abstractmethod
    def load(self):
        """
        加载并返回配置内容（dict）。

        子类必须实现该方法。
        """
        pass


class ParserRegistry:
    """
    解析器注册表，用于维护文件扩展名与解析器类的映射关系
    """

    _parsers = {}

    @classmethod
    def register_parser(cls, extension, parser_clz):
        """为指定的文件扩展名注册解析器"""
        cls._parsers[extension] = parser_clz

    @classmethod
    def get_parser_class(cls, extension):
        """根据文件扩展名获取对应的解析器类"""
        parser_class = cls._parsers.get(extension)
        if not parser_class:
            raise ValueError(f"未找到对应扩展名的解析器: {extension}")
        return parser_class


class ParserError(Exception):
    """
    配置解析相关的自定义异常
    """

    pass


class DotDict(dict):
    """
    支持“点号访问”的字典对象

    示例：
        cfg.db.host 等价于 cfg["db"]["host"]
    """

    def __init__(self, dictionary):
        super().__init__(dictionary)
        # 将嵌套 dict 递归转换为 DotDict
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DotDict(value)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"DotDict 对象不存在属性 '{name}'")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(f"DotDict 对象不存在属性 '{name}'")


class FunctionCallExtractor:
    """
    用于从 Jinja2 模板中提取函数调用信息
    """

    def __init__(self, env):
        self.env = env

    def extract(self, template_str):
        """
        解析模板字符串，提取所有在 Jinja 环境中定义的函数调用
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
                    calls[func_name].append(func_name)
            for child in node.iter_child_nodes():
                visit_node(child)

        visit_node(ast)
        return calls


class Parser:
    """
    使用 Jinja2 模板解析配置数据的核心解析器
    """

    def __init__(self, env):
        self.env = env
        self.call_extractor = FunctionCallExtractor(env)

    def parse_config(self, config):
        """
        解析配置字典
        """
        parsed_config = {}
        for key, value in config.items():
            parsed_config[key] = self.parse_value(value, key)
        return parsed_config

    def parse_value(self, value, key):
        """
        递归解析配置中的值
        """
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
        将字符串按 Jinja2 模板进行渲染

        如果检测到同一个模板中使用了多个返回非字符串的函数，
        将抛出 ParserError。
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
                    f"配置项 '{key}' 模板错误："
                    f"同一个模板中不能同时使用多个返回非字符串的函数。"
                    f"检测到: {', '.join(non_string_functions)}"
                )

            return self.env.from_string(value).render()
        except UndefinedError as e:
            raise ValueError(f"渲染配置项 '{key}' 时发生错误: {e}")

    def parse_list(self, lst, key):
        """
        解析列表类型的配置值
        """
        return [self.parse_value(item, f"{key}[{i}]") for i, item in enumerate(lst)]


def register_global_function(env=_default_env, name=None):
    """
    将函数注册为 Jinja2 全局函数的装饰器
    """

    def decorator(func):
        _name = name if name is not None else func.__name__
        env.globals[_name] = func
        return func

    return decorator


def register_filter(env=_default_env, name=None):
    """
    将函数注册为 Jinja2 过滤器的装饰器
    """

    def decorator(func):
        _name = name if name is not None else func.__name__
        env.filters[_name] = func
        return func

    return decorator


def register_cfg_parser(extension):
    """
    注册配置解析器的装饰器（按文件扩展名）
    """

    def decorator(parser_cls):
        ParserRegistry.register_parser(extension, parser_cls)
        return parser_cls

    return decorator


def returns_native_non_string(func):
    """
    标记函数返回的是原生 Python 对象（非字符串）
    """
    func.returns_native = True
    return func


@register_global_function()
@returns_native_non_string
def import_py_obj(path):
    """
    根据点路径导入 Python 模块或对象

    示例：
        {{ import_py_obj("os.path") }}
        {{ import_py_obj("datetime.datetime") }}
    """
    try:
        if "." not in path:
            return importlib.import_module(path)
        else:
            module_name, obj = path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            return getattr(module, obj)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"无法导入 '{path}': {e}")


@register_global_function()
def env_var(var_name, default=""):
    """
    获取环境变量，如果不存在则返回默认值
    """
    return os.getenv(var_name, default)
