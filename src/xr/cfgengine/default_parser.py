import json
import logging

from xr.cfgengine.parser import CfgParser, register_cfg_parser

_logger = logging.getLogger(__name__)


@register_cfg_parser("json")
class JSONParser(CfgParser):
    """JSON 配置文件解析器"""

    def load(self):

        _logger.info(f"正在加载 JSON 配置文件: {self.file_path}")
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            _logger.error(f"JSON 配置解析失败: {e}")
            raise ValueError(f"{self.file_path} 中的 JSON 配置不合法") from e
        except FileNotFoundError:
            _logger.error(f"配置文件不存在: {self.file_path}")
            raise
        except Exception as e:
            _logger.error(f"加载 JSON 配置时发生未知错误: {e}")
            raise


@register_cfg_parser("ini")
@register_cfg_parser("INI")
class INIParser(CfgParser):
    """INI 配置文件解析器"""

    def load(self):
        import configparser

        _logger.info(f"正在加载 INI 配置文件: {self.file_path}")
        try:
            config = configparser.ConfigParser()
            config.read(self.file_path)
            # 将每个 section 转换为普通 dict 返回
            return {section: dict(config[section]) for section in config.sections()}
        except configparser.Error as e:
            _logger.error(f"INI 配置解析失败: {e}")
            raise ValueError(f"{self.file_path} 中的 INI 配置不合法") from e
        except FileNotFoundError:
            _logger.error(f"配置文件不存在: {self.file_path}")
            raise
        except Exception as e:
            _logger.error(f"加载 INI 配置时发生未知错误: {e}")
            raise


@register_cfg_parser("nacos")
class NacosParser(CfgParser):
    """
    Nacos 配置源解析器

    支持的 URL 格式示例：
    nacos://host:port?data_id=xxx&group=xxx&namespace=xxx
    """

    def __init__(self, nacos_url):
        # 保存原始 nacos URL
        self.nacos_url = nacos_url
        # Nacos 客户端实例（懒加载）
        self.client = None
        # 解析 URL 中的连接参数
        self.params = self._parse_url(nacos_url)
        super().__init__(nacos_url)

    def _parse_url(self, url):
        """
        解析 Nacos URL，提取连接与配置参数
        """
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        return {
            "server": parsed.netloc,
            "data_id": qs.get("data_id", [None])[0],
            "group": qs.get("group", ["DEFAULT_GROUP"])[0],
            "namespace": qs.get("namespace", [None])[0],
            "username": qs.get("username", [None])[0],
            "password": qs.get("password", [None])[0],
        }

    def _get_client(self):
        """
        获取或初始化 NacosClient 实例
        """
        try:
            from nacos import NacosClient
        except ImportError:
            raise ImportError(
                "使用 Nacos 配置需要安装 nacos-sdk-python，"
                "请执行: pip install nacos-sdk-python"
            )

        if not self.client:
            self.client = NacosClient(
                self.params["server"],
                namespace=self.params["namespace"],
                username=self.params["username"],
                password=self.params["password"],
            )
        return self.client

    def load(self):
        """
        从 Nacos 拉取配置内容并解析
        """
        client = self._get_client()

        _logger.info(
            "从 Nacos 加载配置: data_id=%s group=%s",
            self.params["data_id"],
            self.params["group"],
        )

        content = client.get_config(
            data_id=self.params["data_id"],
            group=self.params["group"],
        )

        if content is None:
            raise ValueError("Nacos 返回的配置内容为空")

        content = content.strip()

        # 当前仅支持 JSON 格式的 Nacos 配置
        if content.startswith("{"):
            return json.loads(content)

        raise ValueError("不支持的 Nacos 配置格式（目前仅支持 JSON）")
