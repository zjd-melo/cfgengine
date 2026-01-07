import os
import sys

from xr.cfgengine.parser import ParserRegistry


class ConfigLoader:
    """
    配置加载器。

    负责根据用户指定路径或默认规则查找配置文件，
    并根据配置来源（本地文件 / nacos）选择对应的解析器进行加载。
    """

    # 通过环境变量指定配置文件路径
    DEFAULT_CONFIG_FILE_VAR = "CFGENGINE_CONF"
    # 默认配置文件名
    DEFAULT_CONFIG_FILE_NAME = "config_engine.json"
    # 默认用户目录下的配置路径
    DEFAULT_HOME_PATH = os.path.expanduser(f"~/.config/{DEFAULT_CONFIG_FILE_NAME}")
    # 默认当前目录下的配置路径
    DEFAULT_CURRENT_PATH = f"./{DEFAULT_CONFIG_FILE_NAME}"

    @classmethod
    def set_default_file_name(cls, file_name):
        """
        设置默认配置文件名，并同步更新相关默认路径。

        参数：
            file_name (str): 新的默认配置文件名
        """
        cls.DEFAULT_CONFIG_FILE_NAME = file_name
        cls.DEFAULT_HOME_PATH = os.path.expanduser(f"~/.config/{file_name}")
        cls.DEFAULT_CURRENT_PATH = f"./{file_name}"

    @staticmethod
    def check_file_path(path):
        """
        校验给定路径是否存在且为文件。

        参数：
            path (str): 待检查的文件路径

        返回：
            bool: 若路径存在且为文件则返回 True，否则返回 False
        """
        return os.path.isfile(path) if path else False

    @classmethod
    def get_config_file_path(cls, config_dir_or_path=None):
        """
        根据用户输入或默认规则确定最终使用的配置路径。

        查找顺序：
        1. nacos:// 协议（直接返回）
        2. 用户指定的文件路径
        3. 用户指定目录 + 默认文件名
        4. 当前目录默认配置文件
        5. 环境变量 CFGENGINE_CONF 指定的路径
        6. 用户 home 目录下的默认配置文件

        参数：
            config_dir_or_path (str, optional): 用户指定的配置目录或完整路径

        返回：
            str: 最终确定的配置路径

        异常：
            FileNotFoundError: 未找到任何有效配置文件
        """
        # 若是 nacos 配置，直接返回（不做文件系统校验）
        if config_dir_or_path and config_dir_or_path.startswith("nacos://"):
            return config_dir_or_path

        if config_dir_or_path:
            # 情况一：用户直接指定的是配置文件路径
            if cls.check_file_path(config_dir_or_path):
                sys.stdout.write(
                    f"[INFO] Using configuration file: {config_dir_or_path}\n"
                )
                return config_dir_or_path

            # 情况二：用户指定的是目录，拼接默认配置文件名
            custom_path = os.path.join(config_dir_or_path, cls.DEFAULT_CONFIG_FILE_NAME)
            if cls.check_file_path(custom_path):
                sys.stdout.write(f"[INFO] Using configuration file: {custom_path}\n")
                return custom_path

            # 用户提供的路径无效
            raise FileNotFoundError(f"Specified path is invalid: {config_dir_or_path}")

        # 默认查找路径列表
        paths = [
            cls.DEFAULT_CURRENT_PATH,
            os.environ.get(cls.DEFAULT_CONFIG_FILE_VAR),
            cls.DEFAULT_HOME_PATH,
        ]

        for path in paths:
            if cls.check_file_path(path):
                sys.stdout.write(f"[INFO] Using configuration file: {path}\n")
                return path

        # 所有路径均未命中，抛出详细异常信息
        raise FileNotFoundError(
            "Configuration file not found. Please provide a configuration file in one "
            "of the following paths:\n"
            f"    1. Specified path or directory: {config_dir_or_path or 'Not provided'}\n"
            f"    2. Current directory: {cls.DEFAULT_CURRENT_PATH}\n"
            f"    3. Environment variable {cls.DEFAULT_CONFIG_FILE_VAR}: "
            f"{os.environ.get(cls.DEFAULT_CONFIG_FILE_VAR) or 'Not set'}\n"
            f"    4. User home directory: {cls.DEFAULT_HOME_PATH}\n"
        )

    @classmethod
    def load_config(cls, config_dir_or_path=None, jinja2_env=None):
        """
        加载并解析配置文件。

        根据配置路径类型（nacos / 本地文件），
        自动选择对应的解析器进行解析。

        参数：
            config_dir_or_path (str, optional): 用户指定的配置目录或完整路径
            jinja2_env: Jinja2 环境对象（可选，默认使用 NativeEnvironment）

        返回：
            dict: 解析后的配置数据（DotDict）

        异常：
            FileNotFoundError: 未找到配置文件
            ValueError: 未找到对应的配置解析器
        """
        config_path = cls.get_config_file_path(config_dir_or_path)

        # nacos 配置源，使用 nacos 解析器
        if config_path.startswith("nacos://"):
            parser_class = ParserRegistry.get_parser_class("nacos")
            parser = parser_class(config_path)
            return parser.parse(jinja2_env) if jinja2_env else parser.parse()

        # 本地文件配置，根据文件后缀选择解析器
        _, ext = os.path.splitext(config_path)
        ext = ext.lstrip(".")

        try:
            parser_class = ParserRegistry.get_parser_class(ext)
        except ValueError as e:
            raise ValueError(f"Error retrieving parser for extension '{ext}': {e}")

        parser = parser_class(config_path)
        ret = parser.parse(jinja2_env) if jinja2_env else parser.parse()
        return ret
